box = document.getElementById("status_text")

bid = get_bucket_id()
pid = get_pg_id();

// Load page
async function update() {
    box.innerText = ("You are currently logged in as " + un)
    
    let pagedata = {'username':un, 'session':sk, 'bucketid':bid, 'pageid':pid}
    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(pagedata)
    }
    response = await fetch("/pages/get", send)
    data = await response.json()

    head = document.getElementById("pg_title")
    head.value = data["page"].title
    var replacedStr = data["page"].description.replace(/\[\@\@\#%\]/g, "\"");
    tinymce.activeEditor.setContent(replacedStr)

    window.onbeforeunload = function() {
        return "Data will be lost if you leave the page, are you sure?";
    };
}

async function stick_text_to_normal_box() {
    let pagedata = {'username':un, 'session':sk, 'bucketid':bid, 'pageid':pid}
    console.log(pagedata)
    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(pagedata)
    }
    response = await fetch("/pages/get", send)
    data = await response.json()
    console.log(data)

    head = document.getElementById("pg_title")
    head.value = data["page"].title
    var replacedStr = data["page"].description.replace(/\[\@\@\#%\]/g, "\"");
    
    pagedata = document.getElementById("pg_content")
    pagedata.innerHTML = replacedStr
}

async function generate_next_handlers() {
    
}


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
