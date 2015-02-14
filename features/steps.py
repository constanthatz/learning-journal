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

TEST_DSN = 'dbname=test_learning_journal user=henryhowes'
INPUT_BTN = '<input type="submit" value="Share" name="Share"/>'
READ_ENTRY = """SELECT * FROM entries
"""
RETRIEVE_BY_TITLE = """SELECT * FROM entries WHERE title=%s
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


@world.absorb
def add_entry(app, title, body):
    """provide a single entry in the database"""
    now = datetime.datetime.utcnow()
    expected = (title, body, now)
    with closing(connect_db(settings)) as db:
        world.run_query(db, INSERT_ENTRY, expected, False)
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
    world.entry = world.add_entry(world.app, 'Test Title', 'Test Text')
    world.response = world.app.get('/detail/{}'.format(id))
   

@step('Then I see the content of that post')
def compare(step):
    assert world.response.status_code == 200


    actual = world.response.body
    for expected in world.entry[:2]:
        assert expected in actual


@step ("that I want to add markdown to a post")
def markdown(step):
    pass

@step ("When I add markdown syntax to a post and submit")
def add_post_with_markdown(step):
    world.markdown_post = world.add_entry(world.app, 'Test Markdown Title', '#Test Text\n##Test H2\n*list item\n*list item 2')

@step("Then markdown in the post will be rendered as properly")
def test_markdown_renders(step):
    # markdown_id = world.run_query(db, RETRIEVE_BY_TITLE, world.markdown_post., False)
    response = world.app.get('/detail/{}'.format(1))

    assert "<h1>Test Text</h1>" in response.body

