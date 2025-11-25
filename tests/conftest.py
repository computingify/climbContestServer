import pytest
from climb_contest import create_app, db
from climb_contest.models import Climber, Bloc, Success, climber_category_bloc
from climb_contest.database_handler import handler

@pytest.fixture(autouse=True)
def app():
    app = create_app(config_name='testing')

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
    climber = Climber(name="Test Climber", bib=123, club="Test Club", category="SNH")
    db.session.add(climber)
    db.session.commit()
    return climber

@pytest.fixture()
def new_bloc(app):
    """Creates a new bloc in the database."""
    bloc = Bloc(tag="Test Bloc", number="456")
    db.session.add(bloc)
    db.session.commit()
    return bloc

@pytest.fixture()
def new_success(app, new_climber, new_bloc):
    """Creates a new success in the database."""
    success = Success(climber_id=new_climber.id, bloc_id=new_bloc.id)
    db.session.add(success)
    db.session.commit()
    return success
    
@pytest.fixture()
def complete_database(app):
    """Sets up a complete database with climbers, blocs, and successes."""
    categoryF = "U16 F"
    categoryH = "U16 H"
    category11H = "U11 H"
    climber1 = Climber(name="Climber One", bib=1, club="Club A", category=categoryH)
    climber2 = Climber(name="Climber Two", bib=2, club="Club B", category=categoryF)
    climber3 = Climber(name="Climber Three", bib=3, club="Club B", category=categoryF)
    climber4 = Climber(name="Climber Four", bib=4, club="Club C", category=category11H)
    bloc1 = Bloc(tag="Bloc1", number="1")
    bloc2 = Bloc(tag="Bloc2", number="2")
    bloc3 = Bloc(tag="Bloc3", number="3")
    
    db.session.add_all([climber1, climber2, climber3, climber4, bloc1, bloc2, bloc3])
    
    for i in [1, 2, 3]:
        db.session.execute(climber_category_bloc.insert().values(category=categoryF, bloc_id=i))
        db.session.execute(climber_category_bloc.insert().values(category=categoryH, bloc_id=i))
        db.session.execute(climber_category_bloc.insert().values(category=category11H, bloc_id=i))
    
    db.session.commit()
    
    handler.add_success(climber1, bloc1)
    handler.add_success(climber1, bloc3)
    handler.add_success(climber2, bloc1)
    handler.add_success(climber3, bloc1)
    handler.add_success(climber3, bloc2)
    handler.add_success(climber3, bloc3)
    handler.add_success(climber4, bloc2)
    
    return {
        "climber_ids": [climber1.id, climber2.id, climber3.id, climber4.id],
        "bloc_ids": [bloc1.id, bloc2.id, bloc3.id],
        "categories": [categoryF, categoryH, category11H]
    }