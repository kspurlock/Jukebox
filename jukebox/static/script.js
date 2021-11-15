'use strict';


const vetoButton = document.querySelector('.queuenumber');
const vetoCounter = document.getElementById('vetototal');
const removeSong = document.getElementById('song1');
const createSession = document.getElementById('createsession');
const queueList = document.getElementById('queuelist');

let vetoCount = 0;

// Code to Create Random Session ID
const createID = function() {
    let randomID = Math.floor(Math.random() * (99999-10000+1) + 10000);
    createSession.innerHTML = `Session ID: ${randomID}`;
};

// Code to accumulate vetos
// Still need to give users only one vote per song
vetoButton.addEventListener('click', function() {
   
    vetoCount += 1;
    vetototal.innerHTML = `Veto Count: ${vetoCount}`;
});


const alterQueue = function() {
    $.ajax({
        url: "{{ url_for('routes.py') }}",
        type: "GET",
        data: {
            name: 'song1'
        },
    })
}