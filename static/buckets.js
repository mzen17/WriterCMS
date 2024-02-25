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

// Load page
async function update() {
    response = await fetch("/users/session_validate", send)
    data = await response.json()

    if(data["resp"] === true) {
        box.innerText = ("You are currently logged in as " + un)

        response = await fetch("/buckets/list", send)
        data = await response.json()

        if(data["buckets"].length < 1) {
            box.innerText += "\n\nYou have no buckets to display ."

        } else {
            var div = document.getElementById('status_box');
            var list = document.createElement('ul')

            function pop_link(bk) {
                var item = document.createElement('li')
                var link = document.createElement('a');

                link.textContent = bk.name;
                link.href = '/bucket/'+bk.id;

                link.style="display: inline-block;"
                item.style="margin-bottom:5px;"
                item.appendChild(link);
                list.appendChild(item)
            }

            div.appendChild(list)
            data["buckets"].forEach(pop_link);
        }






    } else {
        window.location.href="/login"

    }
}
update()

// Handle creation of form
var form = document.getElementById("bk_create");

async function submit(event) {
    event.preventDefault();
    bk_name = document.getElementById("bk_name").value

    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: "{\"username\":\"" + un + "\", \"session\":\""+ sk +"\", \"bucket_name\":\""+bk_name+"\"}"
    }


    response = await fetch("/buckets/create", send)
    data = await response.json()

    if(data["resp"] == false) {
        warn_msg = document.getElementById("msg");
        warn_msg.innerText = "An error occurred. Please reload or relogin."
    } else {

        warn_msg = document.getElementById("msg");
        warn_msg.innerText = "Creating..."

        location.reload()
    }
}

form.addEventListener('submit', submit);