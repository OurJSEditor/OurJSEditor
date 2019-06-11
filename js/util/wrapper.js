import "promise-polyfill/src/polyfill";
import "whatwg-fetch";

import { decodeCookie } from "./cookie";

const HEADER = "X-CSRFToken";

const json = e => e.json();

function postJSON(endpoint, payload, csrf) {
    return fetch(endpoint, {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-type": "application/json",
            [HEADER]: csrf,
        },
        body: JSON.stringify(payload),
    }).then(json);
}

export default class Api {
    constructor (csrf) {
        this.csrf = csrf || decodeCookie(document.cookie).csrftoken;
    }

    checkUsername(username) {
        return fetch(`/api/user/username-valid/${encodeURIComponent(username)}`)
            .then(json).then(({ usernameValid }) => usernameValid);
    }

    login(username, password) {
        return postJSON("/api/user/login", { username, password }, this.csrf);
    }

    createAccount(displayName, username, password, email) {
        return postJSON("/api/user/new", email ?
            { displayName, username, password, email } :
            { displayName, username, password }, this.csrf);
    }
    
    getPrograms(src, offset, limit = 20) {
        return fetch(`${src}?offset=${offset}&limit=${limit}`).then(json).then(res => res.programs); //TODO: way of auto-encoding queryParams?
    }
}
