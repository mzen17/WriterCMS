from fastapi.testclient import TestClient
from tests.conftest import set_up_database

client = TestClient(set_up_database())

def test_read_main():



    response = client.post("/users/", json={"username":"john", "password":"12345678"})
    assert response.status_code == 200
    assert response.json = {"resp":True}