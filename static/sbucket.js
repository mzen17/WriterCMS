box = document.getElementById("status_text")
id = get_bucket_id()

del_bid = -1

back = function () {}

// Load page
async function update() {
    let title = document.getElementById("buck_name")
    box.innerText = ("You are currently logged in as " + un)

    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: "{\"username\":\"" + un + "\", \"session\":\""+ sk +"\",\"bucketid\":\"" + id + "\"}"
    }

    response = await fetch("/buckets/get", send)
    data = await response.json()

    if(!data["resp"]) {
        alert("This is an invalid bucket. Redirecting back.")
        window.location.href = "/"
    }

    let head = document.getElementById("head")
    let des = document.getElementById("des")
    console.log(data["bucket"].name)
    head.textContent = data["bucket"].name
    des.textContent = data["bucket"].description

    vis = data["bucket"].visibility

    chkbox = document.getElementById("vis")
    if (chkbox !== null) { 
        chkbox.checked = vis
    }
    var div = document.getElementById('status_box');

    var note = document.createElement("h4")
    note.innerText = "Content:"

    div.appendChild(note)

    if(data["pages"].length + data["buckets"].length < 1) {
        note.innerText = "This bucket have no pages or buckets to display ."
    } else {
        var div = document.getElementById('status_box');
        var list = document.createElement('ul')

        function pop_pg_link(pg) {
            var item = document.createElement('li')
            var link = document.createElement('a');
            link.textContent = "P: " + pg.name;

            tlink = "/bucket/"
            if(typeof linkpfx !== 'undefined') {tlink = linkpfx}
            link.href = tlink + id + "/page/" + pg.id;

            link.style="display: inline-block;"
            item.style="margin-bottom:5px;"
            item.appendChild(link);
            list.appendChild(item)
        }
        function pop_bk_link(bk) {
            var item = document.createElement('li')
            var link = document.createElement('a');

            link.textContent = "B: " + bk.name;

            tlink = "/bucket/"
            if(typeof linkpfx !== 'undefined') {tlink = linkpfx}
            link.href = tlink + bk.id;

            link.style="display: inline-block;"
            item.style="margin-bottom:5px;"
            item.appendChild(link);
            list.appendChild(item)
        }

        div.appendChild(list)

        data["pages"].forEach(pop_pg_link);
        data["buckets"].forEach(pop_bk_link);
    }
    del_bid = data["bucket"].bucket_owner_id
    console.log(del_bid)

    back = function () {
        if(del_bid != null) {
            if(typeof linkpfx == 'undefined') {linkpfx = "/bucket/"}
            console.log("NON NuLl bid?")
            window.location.href= linkpfx + del_bid
        } else {
            if(typeof linkpfx == 'undefined') {linkpfx = "/"} else {linkpfx = "/web/" + un }
            window.location.href = linkpfx
        }
    }
}
update()

// Handle creation of page
var form = document.getElementById("pg_create");
async function submit(event) {
    event.preventDefault();
    pg_name = document.getElementById("pg_title").value
    function isWhitespace(str) {
        return /^\s*$/.test(str);
      }
      
    if(pg_name !== "" && !isWhitespace(pg_name)) {
        let data = {
            "username":un, 
            "session":sk, 
            "title":pg_name, 
            "content":"",
            "bucketid":id, 
            "pageid":-1,
            "visibility":false,
            "porder":-1
        }

        send = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        }

        response = await fetch("/editor/pages/add", send)
        data = await response.json()

        if(data["resp"] == false) {
            warn_msg = document.getElementById("msg");
            warn_msg.innerText = "An error occurred. Please reload or relogin."
        } else {

            warn_msg = document.getElementById("msg");
            warn_msg.innerText = "Creating..."

            location.reload()
        }
    } else {
        warn_msg = document.getElementById("msg");
        warn_msg.innerText = "Must have title."

    }
}
form.addEventListener('submit', submit);


// Bucket Creation
var form2 = document.getElementById("bk_create");
async function submit_cbucket(event) {
    event.preventDefault();
    bk_name = document.getElementById("bkf_title").value
    function isWhitespace(str) {
        return /^\s*$/.test(str);
      }
      
    if(bk_name !== "" && !isWhitespace(bk_name)) {
        data = {"username":un, "session":sk, "bucket_name":bk_name, "bucket_owner_id":id, bucket_id:-1, visibility:false}
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
    } else {
        warn_msg = document.getElementById("msg");
        warn_msg.innerText = "Must have title."

    }
}
form2.addEventListener('submit', submit_cbucket);

async function get_img(file_field_id) {
    const formData = new FormData();

    const fileInput = document.getElementById(file_field_id);
    const allowedTypes = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"]; // Only images

    unit_str = ""
    if (fileInput.files.length == 1 && allowedTypes.includes(fileInput.files[0].type)) {
        formData.append("file", fileInput.files[0]);

        const response = await fetch("/upload_img", {
            method: "POST",
            body: formData,
        });

        data = await response.json()
        console.log(data)
        pfp_str=data["filename"]

    } else {
        alert("To update banner/background, put a IMG file and only 1 file.")
        pfp_str = ""
    }
    return pfp_str
}

// Bucket Update
async function save() {
    var bckt = document.getElementById('buck_name').value
    var chkbox = document.getElementById('vis').checked
    var tags = document.getElementById('bk_tags').value

    var description = document.getElementById('newdes').value
    var bannerIMG = await get_img("newbanner")
    var bgIMG = await get_img("newbg")
    console.log(bannerIMG)

    data = {
        "username":un, 
        "session":sk, 
        "bucket_name":bckt,
        "bucket_id":id, 
        "visibility":chkbox,

        "description": description,
        "banner":bannerIMG,
        "background":bgIMG,
        "tags":tags,
    }

    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    }

    response = await fetch("/editor/buckets/update", send)
    data = await response.json()

    if(data["resp"]) {
        location.reload();
    }else {
        alert("Something bad happened.")
    }
}

// Delete Bucket
async function del() {
    data = {"username":un, "session":sk, "bucketid":id}

    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    }

    response = await fetch("/editor/buckets/delete", send)
    data = await response.json()

    if(data["resp"]) {
        back();
    }else {
        alert("Something went wrong. Ensure that Bucket has no children. It may also be a server error.")
    }

}
