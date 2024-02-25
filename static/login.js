var form = document.getElementById("login");

async function submit(event) {
    event.preventDefault();

    
    username = document.getElementById("user")
    password = document.getElementById("pass")
    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: "{\"username\":\"" + username.value + "\", \"password\":\""+ password.value +"\"}"
    }


    response = await fetch("/users/authenticate", send)
    data = await response.json()

    if(data["resp"] === "false") {
        warn_msg = document.getElementById("msg");
        warn_msg.innerText = "Bad username or password"
    } else {
        warn_msg = document.getElementById("msg");
        warn_msg.innerText = "Logging in..."

        document.cookie = `username=${username.value};path=/;`;
        document.cookie = `session_ck=${data["session_ck"]};path=/;`;
                
        // Return user to previous page
        var previousPage = document.referrer;
        if (previousPage) {
            window.location.href = previousPage;
        } else {
            window.location.href = "/";
        }
    }
}

form.addEventListener('submit', submit);
