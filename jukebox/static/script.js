'use strict';

// Code to Create Random Session ID

const createSession = document.getElementById('createsession');
let randomID = Math.floor(Math.random() * (99999-10000+1) + 10000);
createSession.innerHTML = `Session ID: ${randomID}`;

const vetoButton = document.querySelector('vetobutton');
const removeSong = document.getElementById('song1');


