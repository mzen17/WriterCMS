box = document.getElementById("status_text")

un = getCookie("username")
sk = getCookie("session_ck")

bid = get_bucket_id()
pid = get_pg_id();

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

        send = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: "{\"username\":\"" + un + "\", \"session\":\""+ sk +"\"}"
        }

        response = await fetch("/bucket/"+ bid + "/get/" + pid, send)
        data = await response.json()

        head = document.getElementById("pg_title")
        head.value = data["page"].title
        
        tinymce.activeEditor.setContent(data["page"].description)
    } else {
        window.location.href="/login"

    }
}
update()

async function save() {
    head = document.getElementById("pg_title").value
    body = tinymce.activeEditor.getContent({format : 'raw'});

    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: '{"username":"' + un + '","session":"'+ sk +'","title":"' + head + '","content":"'+body+'"}'
    }
    console.log(send)
    response = await fetch("/bucket/"+ bid + "/update/" + pid, send)
    data = await response.json()

    if (data["resp"] == true) {
        console.log(body)
    }


}