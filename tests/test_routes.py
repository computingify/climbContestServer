from climb_contest.models import Climber, Bloc, Success

def test_simple(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b'Hello from the other side' in response.data
    print(response.data)