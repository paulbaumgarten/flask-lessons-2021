"use strict";


function getDisplayName() {
    fetch("/whoami").then(function(response) {
        response.json().then(function(data) {
            document.querySelector(".hello").innerHTML = "Hello, "+data.name+'.';
        })
    });
}

function sendMessage(e) {
    // Get the message content
    let form = new FormData();
    form.append("message", document.querySelector("#messagetext").value)
    let fetchParameters = { 
        method : 'post',
        body : form 
    };
    fetch("/newmessage", fetchParameters).then(function(response) {
        response.json().then(function(data) {
            console.log(data);
        })
    }).catch(function(e){
        console.log("ERROR");
        console.log(e);
    });
    // Clear the textbox and put the cursor back in it
    document.querySelector('#messagetext').value = '';
    document.querySelector('#messagetext').focus();
}

function checkMessageForEnter(e) {
    if(e.keyCode == 13){
        sendMessage(null);
    }
}

// Our main function...
function main() {
    // Get out signin name and display it
    getDisplayName(); 
    // Send message when button clicked
    document.querySelector("#messagebutton").addEventListener("click", sendMessage);
    // Send message when enter key pressed
    document.querySelector('#messagetext').addEventListener('keydown', checkMessageForEnter);

    // Setup timer to check for and retrieve any messages
}

// Once everything has finished loading, run the main() function
window.onload=main;