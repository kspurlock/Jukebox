'use strict';

const vetoButton = document.querySelectorAll('queuenumber');
const removeSong = document.getElementById('song1');
const createSession = document.getElementById('createsession');
let vetoCount = 0;

// Code to Create Random Session ID
const createID = function() {
    let randomID = Math.floor(Math.random() * (99999-10000+1) + 10000);
    createSession.innerHTML = `Session ID: ${randomID}`;
};

// Code to accumulate vetos



