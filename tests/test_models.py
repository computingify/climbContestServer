import pytest
from datetime import datetime
from climb_contest.models import db, Climber, Bloc, Success
import os

def test_create_climber(app, client, db):
    """Add climber in the database"""
    with app.app_context():
        # Création d'un nouveau grimpeur
        climber = Climber(
            name="John Doe",
            bib=1,
            club="Club A",
            category="SNH"
        )

        # Ajout et validation dans la base de données
        db.session.add(climber)
        db.session.commit()

        # Récupération du grimpeur depuis la base de données
        saved_climber = Climber.query.filter_by(name="John Doe").first()

        # Vérifications
        assert saved_climber is not None
        assert saved_climber.name == "John Doe"
        assert saved_climber.bib == 1
        assert saved_climber.club == "Club A"
        assert saved_climber.category == "SNH"

def test_create_bloc(app, client, db):
    """Add bloc in the database"""
    with app.app_context():
        # Création d'un nouveau bloc
        bloc = Bloc(
            tag="Bloc A",
            number="001"
        )

        # Ajout et validation dans la base de données
        db.session.add(bloc)
        db.session.commit()

        # Récupération du bloc depuis la base de données
        saved_bloc = Bloc.query.filter_by(tag="Bloc A").first()

        # Vérifications
        assert saved_bloc is not None
        assert saved_bloc.tag == "Bloc A"
        assert saved_bloc.number == "001"

def test_create_success(app, client, db, new_climber, new_bloc):
    """Add success in the database"""
    with app.app_context():
        # Création d'un nouveau succès
        success = Success(
            climber_id=new_climber.id,
            bloc_id=new_bloc.id,
            timestamp=datetime.utcnow()  # Use datetime.utcnow() for timezone-naive timestamps
        )

        # Ajout et validation dans la base de données
        db.session.add(success)
        db.session.commit()

        # Récupération du succès depuis la base de données
        saved_success = Success.query.filter_by(climber_id=new_climber.id).first()

        # Vérifications
        assert saved_success is not None
        assert saved_success.climber_id == new_climber.id
        assert saved_success.bloc_id == new_bloc.id
        assert saved_success.timestamp is not None

def test_2_success(app, client, db, new_climber):
    """Add success in the database"""
    with app.app_context():
        # Create blocs
        bloc1 = Bloc(tag="A1", number="1")
        bloc2 = Bloc(tag="B2", number="2")
        db.session.add_all([bloc1, bloc2])
        db.session.commit()

        # Création de nouveaux succès
        success1 = Success(
            climber_id=new_climber.id,
            bloc_id=bloc1.id,
            timestamp=datetime.utcnow()
        )
        success2 = Success(
            climber_id=new_climber.id,
            bloc_id=bloc2.id,
            timestamp=datetime.utcnow()
        )

        # Ajout et validation dans la base de données
        db.session.add_all([success1, success2])
        db.session.commit()

        # Récupération du succès depuis la base de données
        saved_success = Success.query.filter_by(climber_id=new_climber.id).all()

        # Vérifications
        assert len(saved_success) == 2
        assert saved_success[0].climber_id == new_climber.id
        assert saved_success[0].bloc_id == bloc1.id
        assert saved_success[0].timestamp is not None
        assert saved_success[1].climber_id == new_climber.id
        assert saved_success[1].bloc_id == bloc2.id
        assert saved_success[1].timestamp is not None

def test_climber_successes(app, client, db):
    """Test a climber succeeding on multiple blocs and retrieving all successes"""
    with app.app_context():
        # Create climber
        climber = Climber(name="Alice Smith", bib=3, club="Club C", category="U18")
        db.session.add(climber)
        db.session.commit()

        # Create blocs
        bloc1 = Bloc(tag="C1", number="3")
        bloc2 = Bloc(tag="D2", number="4")
        db.session.add_all([bloc1, bloc2])
        db.session.commit()

        # Création de nouveaux succès
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

        # Ajout et validation dans la base de données
        db.session.add_all([success1, success2])
        db.session.commit()

        # Récupération des succès depuis la base de données
        saved_climber = Climber.query.filter_by(name="Alice Smith").first()
        saved_successes = saved_climber.successes

        # Vérifications
        assert len(saved_successes) == 2
        assert saved_successes[0].bloc_id == bloc1.id
        assert saved_successes[1].bloc_id == bloc2.id
        assert saved_successes[0].timestamp is not None
        assert saved_successes[1].timestamp is not None