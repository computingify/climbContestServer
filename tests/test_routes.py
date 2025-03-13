from climb_contest.models import Climber, Bloc, Success
from climb_contest.extensions import db

def add_climber():
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
    return climber

def add_bloc():
    # Create a new bloc
    bloc = Bloc(
        tag="Bloc A",
        number="001"
    )

    # Add and commit to the database
    db.session.add(bloc)
    db.session.commit()
    return bloc

def test_check_climber(client):
    """Test the API for checking a climber"""
    with client.application.app_context():
        climber = add_climber()
        # Prepare the request
        payload = {
            "id": climber.bib
        }

        # Send POST request
        response = client.post(
            '/api/v2/contest/climber/name',
            json=payload,
            content_type='application/json'
        )

        # Verify the response
        assert response.status_code == 201
        data = response.get_json()
        assert data['success']
        assert data['message'] == 'Climber registered successfully'
        assert data['id'] == climber.name

def test_check_bloc_tag(client):
    """Test the API for checking a bloc tag"""
    with client.application.app_context():
        bloc = add_bloc()
        # Prepare the request
        payload = {
            "id": bloc.tag
        }

        # Send POST request
        response = client.post(
            '/api/v2/contest/bloc/name',
            json=payload,
            content_type='application/json'
        )

        # Verify the response
        assert response.status_code == 201
        data = response.get_json()
        assert data['success']
        assert data['message'] == 'Bloc registered successfully'
        assert data['id'] == bloc.tag

def test_register_success(client):
    """Test the API for registering a success"""
    with client.application.app_context():
        climber = add_climber()
        bloc = add_bloc()
        
        # Prepare the request
        payload = {
            "bib": climber.bib,
            "bloc": bloc.tag
        }

        # Send POST request
        response = client.post(
            '/api/v2/contest/success',
            json=payload,
            content_type='application/json'
        )

        # Verify the response
        assert response.status_code == 201
        data = response.get_json()
        assert data['success']
        assert data['message'] == 'Well done'

        # Verify in the database
        success = Success.query.filter_by(climber_id=climber.id, bloc_id=bloc.id).first()
        assert success is not None
        assert success.climber_id == climber.id
        assert success.bloc_id == bloc.id