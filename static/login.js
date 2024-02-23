var form = document.getElementById("login");

function submit(event) {
    event.preventDefault();
    warn_msg = document.getElementById("msg");
    warn_msg.innerText = "YEET!" 
}
console.log("SETUP")

form.addEventListener('submit', submit);
