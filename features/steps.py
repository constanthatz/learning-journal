from lettuce import step
from lettuce import world
import journal
from journal import INSERT_ENTRY

READ_ENTRY = """SELECT * FROM entries
"""
import datetime


@step('that I want to see detail for post (\d+)')
def the_post(step, id):
    world.number = int(id)


@step('when I enter the url /detail/1')
def test_read_entry(req_context):
    # prepare data for testing
    now = datetime.datetime.utcnow()
    expected = ('Test Title', 'Test Text', now)
    run_query(req_context.db, INSERT_ENTRY, expected, False)
    item = run_query(req_context.db, READ_ENTRY)
    req_context.matchdict = {'id': item[0][0]}
    from journal import read_entry
    result = read_entry(req_context)
    # make assertions about the result

    assert 'entries' in result
    assert len(result['entries']) == 4

    assert expected[0] == result['entries']['title']
    assert '<p>{}</p>'.format(expected[1]) == result['entries']['text']
    for key in 'id', 'created':
        assert key in result['entries']

@step('I see the detail view for post ')


@pytest.fixture(scope='function')
def entry(db, request):
    """provide a single entry in the database"""
    settings = db
    now = datetime.datetime.utcnow()
    expected = ('Test Title', 'Test Text', now)
    with closing(connect_db(settings)) as db:
        run_query(db, INSERT_ENTRY, expected, False)
        db.commit()

    def cleanup():
        clear_entries(settings)

    request.addfinalizer(cleanup)

    return expected


@pytest.fixture(scope='session')
def db(request):
    """set up and tear down a database"""
    settings = {'db': TEST_DSN}
    init_db(settings)

    def cleanup():
        clear_db(settings)

    request.addfinalizer(cleanup)

    return settings


@pytest.yield_fixture(scope='function')
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
