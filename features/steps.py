from lettuce import *
from journal import *
import datetime
import os
from contextlib import closing

from journal import connect_db


world.DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id serial PRIMARY KEY,
    title VARCHAR (127) NOT NULL,
    text TEXT NOT NULL,
    created TIMESTAMP NOT NULL
)
"""
INSERT_ENTRY = """INSERT INTO entries (title, text, created) VALUES (%s, %s, %s)
"""

TEST_DSN = 'dbname=test_learning_journal user=chatzis'
INPUT_BTN = '<input type="submit" value="Share" name="Share"/>'
READ_ENTRY = """SELECT * FROM entries where id=%s
"""

settings = {'db': TEST_DSN}


@world.absorb
def run_query(db, query, params=(), get_results=True):
    cursor = db.cursor()
    cursor.execute(query, params)
    db.commit()
    results = None
    if get_results:
        results = cursor.fetchall()
    return results


@before.each_scenario
def init_db(scenario):
    with closing(connect_db(settings)) as db:
        db.cursor().execute(world.DB_SCHEMA)
        db.commit()


@after.each_scenario
def clear_db(scenario):
    with closing(connect_db(settings)) as db:
        db.cursor().execute("DROP TABLE entries")
        db.commit()


@before.each_scenario
def app(scenario):
    from journal import main
    from webtest import TestApp
    os.environ['DATABASE_URL'] = TEST_DSN
    app = main()

    world.app = TestApp(app)


# @after.each_scenario
# def clear_entries(scenario):
#     with closing(connect_db(settings)) as db:
#         db.cursor().execute("DELETE FROM entries")
#         db.commit()


@world.absorb
def add_entry(app):
    """provide a single entry in the database"""
    now = datetime.datetime.utcnow()
    expected = ('Test Title', 'Test Text', now)
    with closing(connect_db(settings)) as db:
        world.run_query(db, INSERT_ENTRY, expected, False)
        db.commit()

    return expected


@world.absorb
def login_helper(username, password, app):
    """encapsulate app login for reuse in tests

    Accept all status codes so that we can make assertions in tests
    """
    login_data = {'username': username, 'password': password}
    return app.post('/login', params=login_data, status='*')




# @before.all
# def db(request):
#     """set up and tear down a database"""
#     settings = {'db': world.TEST_DSN}
#     world.init_db(settings)

#     def cleanup():
#         world.clear_db(settings)

#     request.addfinalizer(cleanup)

#     return settings



    # def cleanup():
    #     settings = {'db': world.TEST_DSN}
    #     clear_entries()

    #request.addfinalizer(cleanup)



# @before.each_scenario
# def req_context(db, request):
#     """mock a request with a database attached"""
#     settings = db
#     req = testing.DummyRequest()
#     with closing(connect_db(settings)) as db:
#         req.db = db
#         req.exception = None
#         yield req

#         # after a test has run, we clear out entries for isolation
#         clear_entries()


@step('that I want to see detail for post (\d+)')
def the_post(step, id):
    world.number = int(id)


@step('when I enter the url /detail/(\d+)')
def test_detail_listing(step, id):
    world.entry = world.add_entry(world.app)
    world.response = world.app.get('/detail/{}'.format(id))


@step('Then I see the detail page and the content of that post')
def detial_compare(step):
    assert world.response.status_code == 200

    actual = world.response.body
    for expected in world.entry[:2]:
        assert expected in actual


@step('that I want to edit post (\d+)')
def the_edit(step, id):
    world.number = int(id)


@step('when I enter the url /editview/(\d+)')
def test_edit_listing(step, id):
    world.entry = world.add_entry(world.app)
    world.entry_data = {
        'title': 'Hello there',
        'text': 'This is a post',
    }

    username, password = ('admin', 'secret')
    login_helper(username, password, world.app)

    world.response_post = world.app.post(
        '/editview/{}'.format(id), params=world.entry_data, status='3*')
    world.new_entry = world.add_entry(world.app)
    world.response_get = world.app.get('/detail/{}'.format(id))


@step('Then I can see the new edit page and edit the entry')
def edit_compare(step):
    assert world.response_get.status_code == 200
    world.entry_data
    actual = world.response_get.body
    for expected in world.entry_data:
        assert world.entry_data[expected] in actual


# @step("that I'm on the detail view for a post")
# def on_detail_view(step, request):
#     assert "detail" in request.url

# @step("when I click a link from the detail view")
# def link_exists(step, request):



