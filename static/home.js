box = document.getElementById("status_text")

un = getCookie("username")
sk = getCookie("session_ck")

send = {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: "{\"username\":\"" + un + "\", \"session\":\""+ sk +"\"}"
}

async function update() {
    response = await fetch("/users/session_validate", send)
    data = await response.json()

    if(data["resp"] === true) {
        box.innerText = ("You are currently logged in as " + un)

        var div = document.getElementById('status_box');
        var link = document.createElement('a');
        link.textContent = 'Go to Pages App.';
        link.href = '/buckets'; // Set the href attribute to the desired URL
        div.appendChild(link);
    } else {
        box.innerText = "You are not currently logged in."

        var div = document.getElementById('status_box');
        var link = document.createElement('a');
        link.textContent = 'Login';
        link.href = '/login'; // Set the href attribute to the desired URL
        div.appendChild(link);

    }
}


update()