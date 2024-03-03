box = document.getElementById("status_text")

un = getCookie("username")
sk = getCookie("session_ck")
id = get_bucket_id()

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
            body: "{\"username\":\"" + un + "\", \"session\":\""+ sk +"\",\"bucketid\":\"" + id + "\"}"
        }

        response = await fetch("/buckets/get", send)
        data = await response.json()

        head = document.getElementById("bk_title")
        head.innerText = data["bucket"].name

        var div = document.getElementById('status_box');

        var note = document.createElement("h4")
        note.innerText = "This bucket's pages."

        div.appendChild(note)

        send = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: "{\"username\":\"" + un + "\", \"session\":\""+ sk + "\"}"
        }

        response = await fetch("/bucket/"+id +"/pages", send)
        data = await response.json()
        console.log(data)
        if(data["pages"].length < 1) {
            note.innerText = "This bucket have no pages to display ."

        } else {

            // Page sorter
            function compare_title( a, b ) {
                if ( a.title < b.title ){
                  return -1;
                }
                if ( a.title > b.title ){
                  return 1;
                }
                return 0;
              }
              
              data["pages"].sort( compare_title );
              

            var div = document.getElementById('status_box');
            var list = document.createElement('ul')

            function pop_link(pg) {
                var item = document.createElement('li')
                var link = document.createElement('a');

                link.textContent = pg.title;
                link.href = '/bucket/'+id +"/page/" + pg.id;

                link.style="display: inline-block;"
                item.style="margin-bottom:5px;"
                item.appendChild(link);
                list.appendChild(item)
            }

            div.appendChild(list)
            data["pages"].forEach(pop_link);
        }

    } else {
        window.location.href="/login"

    }
}
update()



// Handle creation of page


// Handle creation of form
var form = document.getElementById("pg_create");

async function submit(event) {
    event.preventDefault();
    pg_name = document.getElementById("pg_title").value
    function isWhitespace(str) {
        return /^\s*$/.test(str);
      }
      
    if(pg_name !== "" && !isWhitespace(pg_name)) {
        send = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: "{\"username\":\"" + un + "\", \"session\":\""+ sk +"\", \"title\":\""+pg_name+"\",\"content\":\"\"}"
        }


        response = await fetch("/bucket/"+id+"/addpage", send)
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