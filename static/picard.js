/*
 * picard.js
 * Copyright (C) 2023 Sodalicus - Paweł Krzemiński 
 *
 * Distributed under terms of the MIT license.
 */

function setVolume2() {
    let volume = document.getElementById("volume").value;
    document.getElementById("volume_span").innerHTML = volume;

    fetch("/set_volume", {
        method: "POST",
        body: JSON.stringify(volume),
        headers: {"Content-type":"application/json; charset=UTF-8"}})
    .then((response) => response.json())
    .then((response) => console.log(response));
}

function playChannel2(callingTag) {
    let channel = callingTag.id
    console.log(channel)
    fetch("/play_channel", {
        method: "POST",
        body: JSON.stringify(channel),
        headers: {"Content-type":"application/json; charset=UTF-8"}})
    .then((response) => response.json())
    .then((response) => console.log(response));
}

