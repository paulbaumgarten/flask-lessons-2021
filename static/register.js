"use strict";

function validateRegistrationForm(e) {
    let userName = document.querySelector("[name='userid']").value;
    let displayName = document.querySelector("[name='displayName']").value;
    let email = document.querySelector("[name='email']").value;
    let password = document.querySelector("[name='password']").value;
    let password2 = document.querySelector("[name='password2']").value;
    console.log(userName);
    if (userName.length == 0) {
        alert("Username can not be empty");
        e.preventDefault()
    }
    if (displayName.length == 0) {
        alert("Display name can not be empty");
        e.preventDefault()
    }
    if (email.length == 0) {
        alert("Email can not be empty");
        e.preventDefault()
    }
    if (password.length == 0) {
        alert("Password can not be empty");
        e.preventDefault()
    }
    if (password != password2){
        alert("Passwords don't match");
        e.preventDefault()
    }
}

document.querySelector('#registrationForm').onsubmit = validateRegistrationForm;
