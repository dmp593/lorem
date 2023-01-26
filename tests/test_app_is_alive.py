from fastapi.testclient import TestClient

from app.main import app


@app.get('/')
def welcome():
    return {'message': 'Welcome to Lorem!'}


client = TestClient(app)


def test_app_is_alive():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'message': 'Welcome to Lorem!'}
