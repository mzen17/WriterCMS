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

async function updateProfile(e) {
    e.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById("newpfp");
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
        alert("To update PFP, put a IMG file and only 1 file.")
        pfp_str = ""
    }
    console.log(pfp_str)
    let newBio = document.getElementById('newbio').value

    // create the image str (commented out for now)
    json_data = {
        "old_username":un,
        "username":"",// <- this is legacy; remove later with fastapi fmodel
        "session":sk,
        "pfp":pfp_str,
        "bio":newBio
    }
    send = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(json_data)
    }

    response = await fetch("/users/update", send)    
    data = await response.json()

    console.log(data)
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
    // attach listener to form
    form = document.getElementById("updateProfileForm")
    form.addEventListener('submit', updateProfile);
}

update()