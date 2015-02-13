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
world.INSERT_ENTRY = """INSERT INTO entries (title, text, created) VALUES (%s, %s, %s)
"""

TEST_DSN = 'dbname=test_learning_journal user=henryhowes'
world.INPUT_BTN = '<input type="submit" value="Share" name="Share"/>'
world.READ_ENTRY = """SELECT * FROM entries
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


@before.all
def init_db():
    with closing(connect_db(settings)) as db:
        db.cursor().execute(world.DB_SCHEMA)
        db.commit()


@after.all
def clear_db(total):
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


@after.each_scenario
def clear_entries(scenario):
    with closing(connect_db(settings)) as db:
        db.cursor().execute("DELETE FROM entries")
        db.commit()


@world.absorb
def entry(app):
    """provide a single entry in the database"""
    now = datetime.datetime.utcnow()
    expected = ('Test Title', 'Test Text', now)
    with closing(connect_db(settings)) as db:
        world.run_query(db, world.INSERT_ENTRY, expected, False)
        db.commit()

    return expected





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


    # item = run_query(req_context.db, world.READ_ENTRY)
    world.entry = world.entry(world.app)
    world.response = world.app.get('/detail/{}'.format(id))
   

@step('Then I see the content of that post')
def compare(step):
    assert world.response.status_code == 200


    actual = world.response.body
    for expected in world.entry[:2]:
        assert expected in actual



# @step("that I'm on the detail view for a post")
# def on_detail_view(step, request):
#     assert "detail" in request.url

# @step("when I click a link from the detail view")
# def link_exists(step, request):



