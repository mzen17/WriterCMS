# User Testing
# Tests if users side works by simulating the front end's fetches.

def test_user_creation(init_client):
    resp = init_client.post("/users/create", json={"username":"john", "password":"12345678"})
    assert resp.json()["resp"] == True, "john should be successfully created."


def test_user_correct_login(init_client):
    init_client.post("/users/create", json={"username":"john", "password":"12345678"})    
    response = init_client.post("/users/authenticate", json={"username":"john", "password":"12345678"})
    assert response.json()["resp"] == True, "john should be able to login."


def test_user_bad_password_login(init_client):
    init_client.post("/users/create", json={"username":"john", "password":"12345678"})
    response = init_client.post("/users/authenticate", json={"username":"john", "password":"123f45678"})
    assert response.json()["resp"] == False, "john should not be able to login."


def test_unregistered_user_login(init_client):
    response = init_client.post("/users/authenticate", json={"username":"john", "password":"12345678"})
    assert response.json()["resp"] == False, "john should not be validate name"


def test_double_name_register(init_client):
    init_client.post("/users/create", json={"username":"john", "password":"12345678"})
    response = init_client.post("/users/create", json={"username":"john", "password":"fwe"})
    assert response.json()["resp"] == False, "john should not be able to sign up twice."


def test_user_session_info(init_client):
    init_client.post("/users/create", json={"username":"john", "password":"12345678"})
    resp = init_client.post("/users/authenticate", json={"username":"john","password":"12345678"})

    sk = resp.json()["resp"]
    resp = init_client.post("/users/authenticate", json={"username":"john","session":sk,"command":"check"})
    assert response.json()["resp"] == True, "john's session should work."

    