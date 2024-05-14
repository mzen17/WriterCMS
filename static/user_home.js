box = document.getElementById("status_text")

// Load page
async function update() {
    if(guest_mode) {
        box.innerText = ("You are on guest mode")
    } else {
        box.innerText = ("You are currently logged in as " + un + ".")
    }

    response = await fetch("/users/list", send)
    data = await response.json()

    if(data["resp"].length < 1) {
        box.innerText += "\n\nThere are no public users."
    } else {
        var div = document.getElementById('status_box');
        var list = document.createElement('ul')

        function pop_link(user) {
            var item = document.createElement('li')
            var link = document.createElement('a');

            link.textContent = user.name;
            link.href = '/web/'+user.name;

            link.style="display: inline-block;"
            item.style="margin-bottom:5px;"
            item.appendChild(link);
            list.appendChild(item)
        }

        div.appendChild(list)
        data["resp"].forEach(pop_link);
    }
}
update()