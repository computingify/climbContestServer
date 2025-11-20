from climb_contest.models import Climber, Bloc, Success, climber_category_bloc
from climb_contest.extensions import db

_climber_bib_counter = 1  # compteur global pour bib unique

def add_climber():
    global _climber_bib_counter
    # Create a new climber with unique bib
    climber = Climber(
        name=f"John Doe {_climber_bib_counter}",
        bib=_climber_bib_counter,
        club="Club A",
        category="SNH"
    )
    _climber_bib_counter += 1
    db.session.add(climber)
    db.session.commit()
    return climber

def add_bloc_simple():
    return add_bloc(tag="Bloc A", number="001")

def add_bloc(tag, number):
    # Create a new bloc
    bloc = Bloc(
        tag=tag,
        number=number
    )
    # print(f'======> bloc tag = {bloc.tag} number = {bloc.number}')
    # Add and commit to the database
    db.session.add(bloc)
    db.session.commit()
    return bloc

def associate_climber_bloc(climber, bloc):
    # Associate climber and bloc
    db.session.execute(climber_category_bloc.insert().values(category="SNH", bloc_id=bloc.id))

    # print the association db
    # print(f'climber = {climber.id} {climber.name} {climber.bib} {climber.club} {climber.category}')
    # print(f'bloc.categories = {bloc.categories} {bloc.tag} {bloc.number}')
    # print(f'climber_category_bloc = {climber_category_bloc}')
 
    # Commit to the database
    db.session.commit()

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
        assert data['success'] == True
        assert data['id'] == climber.name

def test_check_climber_not_present(client):
    """Test the API for checking a climber"""
    with client.application.app_context():
        add_climber()
        # Prepare the request
        payload = {
            "id": "1456"
        }

        # Send POST request
        response = client.post(
            '/api/v2/contest/climber/name',
            json=payload,
            content_type='application/json'
        )

        # Verify the response
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False

def test_check_bloc_tag(client):
    """Test the API for checking a bloc tag"""
    with client.application.app_context():
        bloc = add_bloc_simple()
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
        assert data['success'] == True
        assert data['id'] == bloc.tag

def test_climber_bloc(client):
    """Test the API for climber checking a bloc"""
    with client.application.app_context():
        climber = add_climber()
        bloc = add_bloc_simple()
        associate_climber_bloc(climber, bloc)
        
        # Prepare the request
        payload = {
            "bib": climber.bib,
            "bloc": bloc.tag
        }

        # Send POST request
        response = client.post(
            '/api/v2/contest/climber/bloc',
            json=payload,
            content_type='application/json'
        )

        # Verify the response
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] == True

def test_climber_bloc_no_associated_bloc(client):
    """Test the API for climber that is not in the request bloc to be done for the contest"""
    with client.application.app_context():
        climber = add_climber()
        bloc = add_bloc_simple()
        bloc2 = add_bloc("Bloc B", "002")
        associate_climber_bloc(climber, bloc)
        
        # Prepare the request
        payload = {
            "bib": climber.bib,
            "bloc": bloc2.tag
        }

        # Send POST request
        response = client.post(
            '/api/v2/contest/climber/bloc',
            json=payload,
            content_type='application/json'
        )

        # Verify the response
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False

def test_climber_bloc_climber_not_present(client):
    """Test the API for climber that is not finded in the database"""
    with client.application.app_context():
        climber = add_climber()
        bloc = add_bloc_simple()
        associate_climber_bloc(climber, bloc)
        
        # Prepare the request
        payload = {
            "bib": "4",
            "bloc": bloc.tag
        }

        # Send POST request
        response = client.post(
            '/api/v2/contest/climber/bloc',
            json=payload,
            content_type='application/json'
        )

        # Verify the response
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False

def test_climber_bloc_bloc_not_present(client):
    """Test the API for bloc that is not finded in the database"""
    with client.application.app_context():
        climber = add_climber()
        bloc = add_bloc_simple()
        associate_climber_bloc(climber, bloc)
        
        # Prepare the request
        payload = {
            "bib": climber.bib,
            "bloc": "Hell block"
        }

        # Send POST request
        response = client.post(
            '/api/v2/contest/climber/bloc',
            json=payload,
            content_type='application/json'
        )

        # Verify the response
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False
        
def test_register_success(client):
    """Test the API for registering a success"""
    with client.application.app_context():
        climber = add_climber()
        bloc = add_bloc_simple()
        associate_climber_bloc(climber, bloc)
        
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
        assert data['success'] == True
        
        # Verify in the database
        success = Success.query.filter_by(climber_id=climber.id, bloc_id=bloc.id).first()
        assert success is not None
        assert success.climber_id == climber.id
        assert success.bloc_id == bloc.id
        
def test_register_success_not_right_bloc(client):
    """Test the API for registering a success"""
    with client.application.app_context():
        climber = add_climber()
        bloc = add_bloc_simple()
        bloc2 = add_bloc("Bloc B", "002")
        associate_climber_bloc(climber, bloc)
        
        # Prepare the request
        payload = {
            "bib": climber.bib,
            "bloc": bloc2.tag
        }

        # Send POST request
        response = client.post(
            '/api/v2/contest/success',
            json=payload,
            content_type='application/json'
        )

        # Verify the response
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] == False

        # Verify in the database
        success = Success.query.filter_by(climber_id=climber.id, bloc_id=bloc.id).first()
        assert success is None