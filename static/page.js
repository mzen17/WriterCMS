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

    oV = document.getElementById("order")
    oV.value = data["page"].porder

    vis = document.getElementById("vis")
    if (vis !== null) {
        vis.checked = data["page"].public
    }

    nav = data["nav"]

    var replacedStr = data["page"].description.replace(/\[\@\@\#%\]/g, "\"");
    tinymce.activeEditor.setContent(replacedStr)

    window.onbeforeunload = function() {
        return "Data will be lost if you leave the page, are you sure?";
    };
}

// A function for view-only page
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

    backfrontAreas = document.getElementsByClassName("backfront")
    function appendBackfront(div) {
        console.log(data["nav"].front)
        username = get_username()

        if ("back" in data["nav"]) {            
            var button = document.createElement("button");
            button.innerHTML = "Previous Page <";        
            button.style="margin-right:20px"
            button.onclick = function() {
                window.location.href = ("/web/" + get_username() + "/bucket/" + bid + "/page/" + data["nav"].back)         
            }
            div.append(button)
        }

        var button = document.createElement("button");
        button.innerHTML = "Table of Contents";        
        button.style="margin-right:20px"
        button.onclick = function() {
            window.location.href = ("/web/" + get_username() + "/bucket/" + bid)
        }
        div.append(button)
             
        if ("front" in data["nav"]) {
            
            var button = document.createElement("button");
            button.innerHTML = "> Next Page";
            
            button.onclick = function() {
                window.location.href = ("/web/" + get_username() + "/bucket/" + bid + "/page/" + data["nav"].front)         
            }

            div.append(button)
        }

    }

    for(var area of backfrontAreas) {
        appendBackfront(area)
    }    
}

async function save() {
    head = document.getElementById("pg_title").value
    body = tinymce.activeEditor.getContent({format : 'raw'});
    var replacedStr = body.replace(/"/g, '[@@#%]');

    visibility = document.getElementById("vis").checked
    porder = document.getElementById("order").value
    if (porder.replace(" ", "") === "") {
        porder = -1
    }

    let data = {
        "username":un, 
        "session":sk, 
        "title":head, 
        "content":replacedStr, 
        "bucketid":bid, 
        "pageid":pid, 
        "visibility":visibility, 
        "porder": porder
    }

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
