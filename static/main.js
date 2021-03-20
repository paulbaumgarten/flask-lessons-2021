"use strict";

var mostRecent = 0;

function getDisplayName() {
    fetch("/whoami").then(function(response) {
        response.json().then(function(data) {
            document.querySelector(".hello").innerHTML = "Hello, "+data.displayName+'.';
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

function getNewMessages() {
    fetch("/getmessages?since="+mostRecent).then( response => {
        response.json().then( data => {
            console.log(data);
            if (data.length > 0) {
                let html = "";
                for (let message of data) {
                    let dt = new Date(message.dateTime * 1000);
                    let dt_display = dt.toLocaleDateString() + " " + dt.toLocaleTimeString();
                    let item = `
                    <div class='messageGrid'>
                        <div class='messageAvatar'><img src='/getavatar/${message.userid}'></div>
                        <div class='messageName'>${message.displayName} ${dt_display}</div>
                        <div class='messageContent'>${message.message}</div>
                    </div>
                    `;
                    html = html + item;
                    if (message.id > mostRecent) {
                        mostRecent = message.id;
                    }
                }
                document.querySelector("#chatcontent").innerHTML += html;
                document.querySelector(".container").scrollTop = document.querySelector(".container").scrollHeight;
            }
        });
    });
}

function onClickOutside(e) {
    document.querySelector('.rightClickMenu').style.display = "none";
    document.removeEventListener("click", onClickOutside);
}

function rightClickSelect(e) {
    alert('pop');
}

function rightClickPopup(e) {
    e.preventDefault();
    document.querySelector('.rightClickMenu').style.display = "block";
    document.querySelector('.rightClickMenu').style.top = e.pageY + "px";
    document.querySelector('.rightClickMenu').style.left = e.pageX + "px";
    document.addEventListener("click", onClickOutside);
}

// Our main function...
function main() {
    // Get out signin name and display it
    getDisplayName(); 
    // Send message when button clicked
    document.querySelector("#messagebutton").addEventListener("click", sendMessage);
    // Send message when enter key pressed
    document.querySelector('#messagetext').addEventListener('keydown', checkMessageForEnter);
    // Setup timer to check for and retrieve any messages every 2.5 seconds
    document.addEventListener("contextmenu", rightClickPopup);
    setInterval(getNewMessages, 2500);
}

// Once everything has finished loading, run the main() function
window.onload=main;