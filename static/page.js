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
        var replacedStr = data["page"].description.replace(/\[\@\@\#%\]/g, "\"");
        tinymce.activeEditor.setContent(replacedStr)
    } else {
        window.location.href="/login"

    }
}
update()

async function save() {
    head = document.getElementById("pg_title").value
    body = tinymce.activeEditor.getContent({format : 'raw'});
    var replacedStr = body.replace(/"/g, '[@@#%]');
    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: '{"username":"' + un + '","session":"'+ sk + '","title":"' + head + '","content":"' + replacedStr + '"}'
    }

    console.log(replacedStr.length)

    response = await fetch("/bucket/"+ bid + "/update/" + pid, send)
    data = await response.json()

    if (data["resp"] == true) {
        window.location.href=("/bucket/"+bid)
    } else {
        alert("An error occured. Please save your content somewhere else and try again later.")
    }


}