# -*- coding: utf-8 -*-
import os
import logging
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.view import view_config
from waitress import serve
import psycopg2
from contextlib import closing
from pyramid.events import NewRequest, subscriber
import datetime
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound, HTTPInternalServerError
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from cryptacular.bcrypt import BCRYPTPasswordManager
from pyramid.security import remember, forget
import markdown
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension

USER = 'chatzis'

here = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig()
log = logging.getLogger(__file__)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Entry(Base):
    __tablename__ = 'entries'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.Unicode(127), nullable=False)
    text = sa.Column(sa.UnicodeText, nullable=False)
    created = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow
    )

    def __repr__(self):
        return u"{}: {}".format(self.__class__.__name__, self.title)

    @classmethod
    def all(cls):
        return DBSession.query(cls).order_by(cls.created.desc()).all()

    @classmethod
    def newest_entry(cls):
        return DBSession.query(cls).order_by(cls.created.desc()).first()

    @classmethod
    def by_id(cls, id):
        return DBSession.query(cls).filter(cls.id == id).one()

    @classmethod
    def from_request(cls, request):
        title = request.params.get('title', None)
        text = request.params.get('text', None)
        created = datetime.datetime.utcnow()
        new_entry = cls(title=title, text=text, created=created)
        DBSession.add(new_entry)

    def update_from_request(self, request):
        self.title = request.params.get('title', None)
        self.text = request.params.get('text', None)

    def render_markdown(self):
        return markdown.markdown(
            self.text, extensions=['codehilite', 'fenced_code'])

    def convert_strftime(self):
        return self.created.strftime('%b %d, %Y')

    def json(self):
        return {'title': self.title,
                'text': self.render_markdown(),
                'created': self.created.strftime('%b %d, %Y'),
                'id': self.id}

    def json_edit_get(self):
        return {'title': self.title,
                'text': self.text,
                'created': self.created.strftime('%b %d, %Y'),
                'id': self.id}


logging.basicConfig()
log = logging.getLogger(__file__)


def main():
    """Create a configured wsgi app"""
    settings = {}
    settings['reload_all'] = os.environ.get('DEBUG', True)
    settings['debug_all'] = os.environ.get('DEBUG', True)
    settings['sqlalchemy.url'] = os.environ.get(
        'DATABASE_URL',
        'postgresql://{}:@localhost:5432/learning_journal'.format(USER)
    )
    engine = sa.engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    settings['auth.username'] = os.environ.get('AUTH_USERNAME', 'admin')
    manager = BCRYPTPasswordManager()
    settings['auth.password'] = os.environ.get(
        'AUTH_PASSWORD', manager.encode('secret'))
    # secret value for session signing:
    secret = os.environ.get('JOURNAL_SESSION_SECRET', 'itsaseekrit')
    session_factory = SignedCookieSessionFactory(secret)
    # add a secret value for auth tkt signing
    auth_secret = os.environ.get('JOURNAL_AUTH_SECRET', 'anotherseekrit')
    # configuration setup
    config = Configurator(
        settings=settings,
        session_factory=session_factory,
        authentication_policy=AuthTktAuthenticationPolicy(
            secret=auth_secret,
            hashalg='sha512'
        ),
        authorization_policy=ACLAuthorizationPolicy(),
    )
    config.include('pyramid_jinja2')
    config.include('pyramid_tm')
    config.add_static_view('static', os.path.join(here, 'static'))
    config.add_route('home', '/')
    config.add_route('add', '/add')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('detail', '/detail/{id}')
    config.add_route('editview', '/editview')
    config.scan()
    app = config.make_wsgi_app()
    return app


def do_login(request):
    username = request.params.get('username', None)
    password = request.params.get('password', None)
    if not (username and password):
        raise ValueError('both username and password are required')
    settings = request.registry.settings
    manager = BCRYPTPasswordManager()
    if username == settings.get('auth.username', ''):
        hashed = settings.get('auth.password', '')
        return manager.check(hashed, password)


@view_config(route_name='login', renderer="templates/login.jinja2")
def login(request):
    """authenticate a user by username/password"""
    username = request.params.get('username', '')
    error = ''
    if request.method == 'POST':
        error = "Login Failed"
        authenticated = False
        try:
            authenticated = do_login(request)
        except ValueError as e:
            error = str(e)
        if authenticated:
            headers = remember(request, username)
            return HTTPFound(request.route_url('home'), headers=headers)
    return {'error': error, 'username': username}


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


@view_config(route_name='detail', renderer='templates/detail.jinja2')
def read_entry(request):
    """return a list of one entry as a dict"""
    # import pdb; pdb.set_trace()

    entry = Entry.by_id(request.matchdict['id'])
    return {'entry': entry}


@view_config(route_name='home', renderer='templates/list.jinja2')
def read_entries(request):
    """return a list of all entries as dicts"""
    entries = Entry.all()
    return {'entries': entries}


@view_config(route_name='add', renderer="json")
def add_entry(request):
    if request.authenticated_userid:
        if request.method == 'POST':
            try:
                Entry.from_request(request)
            except psycopg2.Error:
                # this will catch any errors generated by the database
                return HTTPInternalServerError()
            entry = Entry.newest_entry()
            return entry.json()
    else:
        return HTTPForbidden()


@view_config(route_name='editview', renderer='json')
def editview_entry(request):
    """return a list of all entries as dicts"""
    # import pdb; pdb.set_trace()
    if request.authenticated_userid:
        entry = Entry.by_id(request.params.get('id', None))
        if request.method == 'GET':
            return entry.json_edit_get()

        elif request.method == 'POST':
            try:
                entry.update_from_request(request)
            except psycopg2.Error:
                # this will catch any errors generated by the database
                return HTTPInternalServerError()
            return entry.json()
    else:
        return HTTPForbidden()

if __name__ == '__main__':
    app = main()
    port = os.environ.get('PORT', 5000)
    serve(app, host='0.0.0.0', port=port)
