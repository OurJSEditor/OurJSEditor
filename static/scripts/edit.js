var checkForm = function () {
    loginT = document.getElementById("loginT");
    form = document.getElementById("profileForm")
    if (form.username.value === "") {
        loginT.innerHTML = "Please fill the username field.<br>";
        return false;
    }
    if (form.username.value.match(/\W/) ||
        (form.username.value !== current_username && document.getElementById("available").innerHTML !== "\u2714")) {
       loginT.innerHTML = "Invalid username<br>";
       return false;
    }
    if (form.display_name.value === "") {
        form.display_name.value = form.username.value;
    }
};
var checkUsername = function() {
    var available = document.getElementById("available");
    available.innerHTML = "";
    var ans=false;

    if (current_username == document.getElementById("username").value) {
        available.innerHTML = "&#x2714;";
        return;
    }

    var req = new XMLHttpRequest();
    req.addEventListener("load", function() {
        if (this.status == 200) {
            ans = JSON.parse(this.response);
            ans = ans["username_available"];
        }
        if (ans) {
            available.innerHTML = "&#x2714;";
        }else {
            available.innerHTML = "&#x2717;";
        }
    });
    req.open("GET", "/api/users/username_available?username=" + document.getElementById("username").value);
    req.send();
};
