box = document.getElementById("status_text")

un = getCookie("username")
sk = getCookie("session_ck")
id = get_bucket_id()

back = function () {}

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
        console.log(data);

        head = document.getElementById("bk_title")
        head.innerText = data["bucket"].name

        var div = document.getElementById('status_box');

        var note = document.createElement("h4")
        note.innerText = "This bucket's pages."

        div.appendChild(note)

        if(data["pages"].length + data["buckets"].length < 1) {
            note.innerText = "This bucket have no pages or buckets to display ."
        } else {
            // Page sorter
            function compare_id( a, b ) {
                if ( a.id < b.id ){
                  return -1;
                }
                if ( a.id > b.id ){
                  return 1;
                }
                return 0;
              }
              data["pages"].sort( compare_id );
              data["buckets"].sort( compare_id );

            var div = document.getElementById('status_box');
            var list = document.createElement('ul')

            function pop_pg_link(pg) {
                var item = document.createElement('li')
                var link = document.createElement('a');
                console.log(pg)
                link.textContent = "P: " + pg.name;
                link.href = '/bucket/'+id +"/page/" + pg.id;

                link.style="display: inline-block;"
                item.style="margin-bottom:5px;"
                item.appendChild(link);
                list.appendChild(item)
            }
            function pop_bk_link(bk) {
                var item = document.createElement('li')
                var link = document.createElement('a');

                link.textContent = "B: " + bk.name;
                link.href = '/bucket/'+ bk.id;

                link.style="display: inline-block;"
                item.style="margin-bottom:5px;"
                item.appendChild(link);
                list.appendChild(item)
            }

            div.appendChild(list)
            data["pages"].forEach(pop_pg_link);
            data["buckets"].forEach(pop_bk_link);

        }
        console.log("/bucket/"+data["bucket"].owner_id)

        back = function () {
            if(data["bucket"].bucket_owner_id) {
                window.location.href="/bucket/" + data["bucket"].bucket_owner_id
            }else {
                window.location.href="/buckets"
            }
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

// Bucket Creation
var form2 = document.getElementById("bk_create");

async function submit_cbucket(event) {
    event.preventDefault();
    bk_name = document.getElementById("bkf_title").value
    function isWhitespace(str) {
        return /^\s*$/.test(str);
      }
      
    if(bk_name !== "" && !isWhitespace(bk_name)) {
        send = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: "{\"username\":\"" + un + "\", \"session\":\""+ sk +"\", \"bucket_name\":\""+bk_name+"\",\"bucket_id1\":\""+id+"\"}"
        }

        response = await fetch("/buckets/create", send)
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
