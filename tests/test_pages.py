
def test_page_creation(init_client, create_bucket):
    create_bucket["title"] = "PAGET"
    create_bucket["content"] = ""

    resp = init_client.post("/bucket/1/addpage", json=create_bucket)
    print(resp)
    assert resp.json()["resp"] == True, "A page should be created."


def test_page_list(init_client, create_bucket):
    create_bucket["title"] = "PAGET"
    create_bucket["content"] = ""

    resp = init_client.post("/bucket/1/addpage", json=create_bucket)
    del create_bucket["title"]
    del create_bucket["content"] 

    resp = init_client.post("/bucket/1/pages", json=create_bucket)
    print(resp.json())
    pg = resp.json()["pages"]

    assert len(pg) == 1, "john's session should work."
    assert pg[0]["title"] == "PAGET"


def test_page_update(init_client, create_bucket):
    create_bucket["title"] = "PAGET"
    create_bucket["content"] = "Update"

    resp = init_client.post("/bucket/1/addpage", json=create_bucket)

    create_bucket["title"] = "PAGET_U"
    create_bucket["content"] = "UPDATE"

    resp = init_client.post("/bucket/1/update/1/", json=create_bucket)

    del create_bucket["title"]
    del create_bucket["content"] 

    resp = init_client.post("/bucket/1/pages", json=create_bucket)
    pg = resp.json()["pages"]

    assert len(pg) == 1, "john's session only have 1."
    assert pg[0]["title"] == "PAGET_U"
    assert pg[0]["description"] == "UPDATE"