box = document.getElementById("status_text")

// Load page
async function update() {
    if( typeof guest_mode !== 'undefined' && guest_mode ){
        box.innerText = "You are on guest mode."
    } else {
        box.innerText = ("You are currently logged in as " + un)
    }

    data = {"username":un, "session":sk}
    console.log(un + "  "+ sk)
    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body:JSON.stringify(data)
    }

    response = await fetch("/buckets/list", send)
    data = await response.json()
    console.log(data)

    if(data["buckets"].length < 1) {
        box.innerText += "\n\nYou have no buckets to display."

    } else {
        var div = document.getElementById('status_box');
        var list = document.createElement('ul')

        function pop_link(bk) {
            var item = document.createElement('li')
            var link = document.createElement('a');

            link.textContent = bk.name;

            if(typeof linkpfx === 'undefined') {linkpfx="/bucket/"}
            link.href = linkpfx + bk.id;

            link.style="display: inline-block;"
            item.style="margin-bottom:5px;"
            item.appendChild(link);
            list.appendChild(item)
        }

        div.appendChild(list)
        data["buckets"].forEach(pop_link);
    }
}
update()

// Handle creation of form
var form = document.getElementById("bk_create");

async function submit(event) {
    event.preventDefault();
    bk_name = document.getElementById("bk_name").value

    data = {"username":un, "session":sk, "bucket_name":bk_name, "visibility":false, "bucket_id":-1}

    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    }


    response = await fetch("/editor/buckets/create", send)
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