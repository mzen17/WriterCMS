un = getCookie("username")
sk = getCookie("session_ck")

async function get_results() {

    data = {"username":un, "session":sk}
    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: "{\"username\":\"" + un + "\", \"session\":\""+ sk +"\"}"
    }
    response = fetch("/users/session_validate", send)
    data = response.json()

    return data["resp"]
}
guest_mode = get_results()