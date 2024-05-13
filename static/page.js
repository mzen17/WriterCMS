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
        let pagedata = {'username':un, 'session':sk, 'bucketid':bid, 'pageid':pid}
        send = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(pagedata)
        }
        console.log(send)

        response = await fetch("/pages/get", send)
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

window.onbeforeunload = function() {
    return "Data will be lost if you leave the page, are you sure?";
};

async function save() {
    head = document.getElementById("pg_title").value
    body = tinymce.activeEditor.getContent({format : 'raw'});
    var replacedStr = body.replace(/"/g, '[@@#%]');

    let data = {"username":un, "session":sk, "title":head, "content":replacedStr, "bucketid":bid, "pageid":pid}

    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    }

    response = await fetch("/editor/pages/update", send)
    data = await response.json()

    if (data["resp"] == true) {
        window.onbeforeunload = function() {
            
        };
        
        window.location.href=("/bucket/" + bid)
    } else {
        alert("An error occured. Please save your content somewhere else and try again later.")
    }
}

async function del() {
    let confirm = window.confirm("Deleting this page is irreversable! Do you still want to delete?")

    if (confirm) {
        let data = {"username":un, "session":sk, "bucketid":bid, "pageid":pid}

        send = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        }
    
        response = await fetch("/editor/pages/delete", send)
        data = await response.json()
    
        if (data["resp"] == true) {            
            window.onbeforeunload = function() {};
            window.location.href=("/bucket/" + bid)
        }
    }
}
