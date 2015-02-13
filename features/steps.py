from lettuce import *
from journal import *
import datetime

world.DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id serial PRIMARY KEY,
    title VARCHAR (127) NOT NULL,
    text TEXT NOT NULL,
    created TIMESTAMP NOT NULL
)
"""
world.INSERT_ENTRY = """INSERT INTO entries (title, text, created) VALUES (%s, %s, %s)
"""

world.TEST_DSN = 'dbname=test_learning_journal user=chatzis'
world.INPUT_BTN = '<input type="submit" value="Share" name="Share"/>'
world.READ_ENTRY = """SELECT * FROM entries
"""


@world.absorb
def run_query(db, query, params=(), get_results=True):
    cursor = db.cursor()
    cursor.execute(query, params)
    db.commit()
    results = None
    if get_results:
        results = cursor.fetchall()
    return results


@world.absorb
def clear_entries(settings):
    with closing(connect_db(settings)) as db:
        db.cursor().execute("DELETE FROM entries")
        db.commit()


@world.absorb
def clear_db(settings):
    with closing(connect_db(settings)) as db:
        db.cursor().execute("DROP TABLE entries")
        db.commit()


@world.absorb
def init_db(settings):
    with closing(connect_db(settings)) as db:
        db.cursor().execute(world.DB_SCHEMA)
        db.commit()


@before.all
def db(request):
    """set up and tear down a database"""
    settings = {'db': world.TEST_DSN}
    world.init_db(settings)

    def cleanup():
        world.clear_db(settings)

    request.addfinalizer(cleanup)

    return settings


@before.each_scenario
def app(db, request):
    from journal import main
    from webtest import TestApp
    os.environ['DATABASE_URL'] = world.TEST_DSN
    app = main()

    def cleanup():
        settings = {'db': world.TEST_DSN}
        clear_entries(settings)

    request.addfinalizer(cleanup)

    return TestApp(app)


@before.each_scenario
def entry(db, request):
    """provide a single entry in the database"""
    settings = db
    now = datetime.datetime.utcnow()
    expected = ('Test Title', 'Test Text', now)
    with closing(connect_db(settings)) as db:
        world.run_query(db, world.INSERT_ENTRY, expected, False)
        db.commit()

    def cleanup():
        world.clear_entries(settings)

    request.addfinalizer(cleanup)

    return expected


@before.each_scenario
def req_context(db, request):
    """mock a request with a database attached"""
    settings = db
    req = testing.DummyRequest()
    with closing(connect_db(settings)) as db:
        req.db = db
        req.exception = None
        yield req

        # after a test has run, we clear out entries for isolation
        clear_entries(settings)


@step('that I want to see detail for post (\d+)')
def the_post(step, id):
    world.number = int(id)


@step('when I enter the url /detail/1')
def test_detail_listing(app, entry, req_context):
    item = run_query(req_context.db, world.READ_ENTRY)
    response = app.get('/detail/{}'.format(item[0][0]))
    world.status_code = response.status_code
    world.response_body = response.body
    world.entry = entry[:2]
    for expected in entry[:2]:
        assert expected in actual


@step('I see the detail view with response code (\d+)')
def compare(step, expected):
    assert expected == world.status_code
