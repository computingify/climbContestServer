import pytest
from climb_contest import create_app, db
from climb_contest.models import Climber, Bloc, Success

@pytest.fixture()
def app():
    app = create_app(config_name='testing')
    app.config.update({
        "TESTING": True,
    })

    # Initialize the test database
    with app.app_context():
        db.create_all()

    yield app

    # Clean up the test database
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture()
def new_climber(app):
    """Creates a new climber in the database."""
    with app.app_context():
        climber = Climber(name="Test Climber", bib=123, club="Test Club", category="SNH")
        db.session.add(climber)
        db.session.commit()
        return climber

@pytest.fixture()
def new_bloc(app):
    """Creates a new bloc in the database."""
    with app.app_context():
        bloc = Bloc(tag="Test Bloc", number="456")
        db.session.add(bloc)
        db.session.commit()
        return bloc

@pytest.fixture()
def new_success(app, new_climber, new_bloc):
    """Creates a new success in the database."""
    with app.app_context():
        success = Success(climber_id=new_climber.id, bloc_id=new_bloc.id)
        db.session.add(success)
        db.session.commit()
        return success