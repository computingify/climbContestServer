from datetime import datetime
from climb_contest.extensions import db
from climb_contest.models import Climber, Bloc, Success

def test_create_climber(app):
    """Add climber in the database"""
    with app.app_context():
        # Create a new climber
        climber = Climber(
            name="John Doe",
            bib=2,
            club="Club A",
            category="SNH"
        )

        # Add and commit to the database
        db.session.add(climber)
        db.session.commit()

        # Retrieve the climber from the database
        saved_climber = Climber.query.filter_by(name="John Doe").first()

        # Verifications
        assert saved_climber is not None
        assert saved_climber.name == "John Doe"
        assert saved_climber.bib == 2
        assert saved_climber.club == "Club A"
        assert saved_climber.category == "SNH"

def test_create_bloc(app):
    """Add bloc in the database"""
    with app.app_context():
        # Create a new bloc
        bloc = Bloc(
            tag="Bloc A",
            number="001"
        )

        # Add and commit to the database
        db.session.add(bloc)
        db.session.commit()

        # Retrieve the bloc from the database
        saved_bloc = Bloc.query.filter_by(tag="Bloc A").first()

        # Verifications
        assert saved_bloc is not None
        assert saved_bloc.tag == "Bloc A"
        assert saved_bloc.number == "001"

def test_create_success(app):
    """Add success in the database"""
    with app.app_context():
        # Create climber
        climber = Climber(name="Alice Smith", bib=2, club="Club B", category="U18")

        # Create blocs
        bloc = Bloc(tag="A1", number="1")
        db.session.add_all([bloc, climber])
        db.session.commit()
        # Create a new success
        success = Success(
            climber_id=climber.id,
            bloc_id=bloc.id,
        )

        # Add and commit to the database
        db.session.add(success)
        db.session.commit()

        # Retrieve the success from the database
        saved_success = Success.query.filter_by(climber_id=climber.id).first()

        # Verifications
        assert saved_success is not None
        assert saved_success.climber_id == climber.id
        assert saved_success.bloc_id == bloc.id
        assert saved_success.timestamp is not None

def test_2_success(app):
    """Add success in the database"""
    with app.app_context():
        # Create climber
        climber = Climber(name="Alice Smith", bib=2, club="Club B", category="U18")
        db.session.add(climber)
        db.session.commit()

        # Create blocs
        bloc1 = Bloc(tag="A1", number="1")
        bloc2 = Bloc(tag="B2", number="2")
        db.session.add_all([bloc1, bloc2])
        db.session.commit()

        # Create new successes
        success1 = Success(
            climber_id=climber.id,
            bloc_id=bloc1.id,
            timestamp=datetime.utcnow()
        )
        success2 = Success(
            climber_id=climber.id,
            bloc_id=bloc2.id,
            timestamp=datetime.utcnow()
        )

        # Add and commit to the database
        db.session.add_all([success1, success2])
        db.session.commit()

        # Retrieve the success from the database
        saved_success = Success.query.filter_by(climber_id=climber.id).all()

        # Verifications
        assert len(saved_success) == 2
        assert saved_success[0].climber_id == climber.id
        assert saved_success[0].bloc_id == bloc1.id
        assert saved_success[0].timestamp is not None
        assert saved_success[1].climber_id == climber.id
        assert saved_success[1].bloc_id == bloc2.id
        assert saved_success[1].timestamp is not None

def test_climber_successes(app):
    """Test a climber succeeding on multiple blocs and retrieving all successes"""
    with app.app_context():
        # Create climber
        climber = Climber(name="Bob Johnson", bib=3, club="Club C", category="U20")
        db.session.add(climber)
        db.session.commit()

        # Create blocs
        bloc1 = Bloc(tag="C1", number="3")
        bloc2 = Bloc(tag="D2", number="4")
        db.session.add_all([bloc1, bloc2])
        db.session.commit()

        # Create new successes
        success1 = Success(
            climber_id=climber.id,
            bloc_id=bloc1.id,
        )
        success2 = Success(
            climber_id=climber.id,
            bloc_id=bloc2.id,
        )

        # Add and commit to the database
        db.session.add_all([success1, success2])
        db.session.commit()

        # Retrieve the successes from the database
        saved_climber = Climber.query.filter_by(name=climber.name).first()
        saved_successes = saved_climber.successes

        # Verifications
        assert len(saved_successes) == 2
        assert saved_successes[0].bloc_id == bloc1.id
        assert saved_successes[1].bloc_id == bloc2.id
        assert saved_successes[0].timestamp is not None
        assert saved_successes[1].timestamp is not None