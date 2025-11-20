import pytest
from climb_contest.extensions import db
from climb_contest.models import Climber, Bloc, BlocScore, Success
from climb_contest.database_handler import DatabaseHandler

@pytest.fixture()
def handler():
    return DatabaseHandler()

def test_add_success_first(app, handler):
    with app.app_context():
        climber = Climber(name="Alice", bib=1, club="Club A", category="U16")
        bloc = Bloc(tag="A1", number="1")
        db.session.add_all([climber, bloc])
        db.session.commit()

        handler.add_success(climber, bloc)

        # BlocScore should be created and set to 1000
        bloc_score = BlocScore.query.filter_by(bloc_id=bloc.id, category=climber.category).first()
        assert bloc_score is not None
        assert bloc_score.value == 1000

        # Success should be present
        success = Success.query.filter_by(climber_id=climber.id, bloc_id=bloc.id).first()
        assert success is not None

def test_add_success_second(app, handler):
    with app.app_context():
        climber1 = Climber(name="Alice", bib=1, club="Club A", category="U16")
        climber2 = Climber(name="Bob", bib=2, club="Club B", category="U16")
        bloc = Bloc(tag="A1", number="1")
        db.session.add_all([climber1, climber2, bloc])
        db.session.commit()

        handler.add_success(climber1, bloc)
        handler.add_success(climber2, bloc)

        # BlocScore should be updated to 500
        bloc_score = BlocScore.query.filter_by(bloc_id=bloc.id, category=climber1.category).first()
        assert bloc_score is not None
        assert bloc_score.value == 500

        # Both successes should be present
        success1 = Success.query.filter_by(climber_id=climber1.id, bloc_id=bloc.id).first()
        success2 = Success.query.filter_by(climber_id=climber2.id, bloc_id=bloc.id).first()
        assert success1 is not None
        assert success2 is not None
