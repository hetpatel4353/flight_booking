function show() {
    let v = document.getElementById("password");
    if (v.type === "password") {
        v.type = "text";
        document.getElementById("eye").innerHTML = '<i class="fa-solid fa-eye-slash"></i>'
    } else {
        v.type = "password";
        document.getElementById("eye").innerHTML = '<i class="fa-solid fa-eye"></i>'
    }
}
