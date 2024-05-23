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

    response = await fetch("/users/session_validate", send)
    data = await response.json()

    return data["resp"]
}
guest_mode = get_results()