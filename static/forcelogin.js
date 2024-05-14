un = getCookie("username")
sk = getCookie("session_ck")
guest_mode = false

data = {"username":un, "session":sk}
send = {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: "{\"username\":\"" + un + "\", \"session\":\""+ sk +"\"}"
}

// Load page
async function update() {
    response = await fetch("/users/session_validate", send)
    data = await response.json()

    if(data["resp"] !== true) {
        window.location.href="/login"
    }
}
update()