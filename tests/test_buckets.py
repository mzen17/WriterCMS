# Pages Testing
# Tests if pages API works by simulating front page.abs
# Assumes that users is working

def test_bucket_creation(init_client, set_up_john):
    set_up_john["bucket_name"] = "Test Bucket"
    resp = init_client.post("/buckets/editor/create", json=set_up_john)
    print(resp)
    assert resp.json()["resp"] == True, "john's session should work."


def test_bucket_list(init_client, set_up_john):
    set_up_john["bucket_name"] = "Test Bucket"
    resp = init_client.post("/buckets/editor/create", json=set_up_john)
    set_up_john["bucket_name"] = "Test Bucket"
    resp = init_client.post("/buckets/editor/create", json=set_up_john)
    set_up_john["bucket_name"] = "Test Bucket"
    resp = init_client.post("/buckets/editor/create", json=set_up_john)
  
    del set_up_john['bucket_name']
    resp = init_client.post("/buckets/list", json=set_up_john)
    bks = resp.json()["buckets"]
    assert len(bks) == 3, "John bucket should have 3 items."


def test_bucket_list_0(init_client, set_up_john):
    resp = init_client.post("/buckets/list", json=set_up_john)
    bks = resp.json()["buckets"]
    assert len(bks) == 0, "John bucket should have 0 items."


def test_bucket_list_contents(init_client, set_up_john):
    set_up_john["bucket_name"] = "Test Bucket"
    resp = init_client.post("/buckets/editor/create", json=set_up_john)
    set_up_john["bucket_name"] = "Test 2"
    resp = init_client.post("/buckets/editor/create", json=set_up_john)
    set_up_john["bucket_name"] = "Test 3"
    resp = init_client.post("/buckets/editor/create", json=set_up_john)
  
    resp = init_client.post("/buckets/list", json=set_up_john)
    bks = resp.json()["buckets"]

    assert bks[0] == {"name":"Test Bucket", "id":1,"owner_id":1}, "John bucket should have 3 items."
    assert bks[1] == {"name":"Test 2", "id":2,"owner_id":1}, "John bucket should have 3 items."
    assert bks[2] == {"name":"Test 3", "id":3,"owner_id":1}, "John bucket should have 3 items."


def test_bucket_get(init_client, set_up_john):
    set_up_john["bucket_name"] = "Test Bucket"
    resp = init_client.post("/buckets/editor/create", json=set_up_john)
    set_up_john["bucket_name"] = "Test Bucket2"
    resp = init_client.post("/buckets/editor/create", json=set_up_john)
    set_up_john["bucket_name"] = "Test Bucket3"
    resp = init_client.post("/buckets/editor/create", json=set_up_john)

    del set_up_john['bucket_name']
    set_up_john['bucketid']=1

    resp = init_client.post("/buckets/get", json=set_up_john)
    bks = resp.json()['bucket']["name"]
    assert bks == "Test Bucket", "John bucket 1 should be named Test Bucket."

    set_up_john['bucketid']=3

    resp = init_client.post("/buckets/get", json=set_up_john)
    bks = resp.json()['bucket']["name"]
    assert bks == "Test Bucket3", "John bucket 3 should be named Test Bucket3."



