const express = require('express');
const bodyParser = require('body-parser');
const _ = require('lodash');
const app = express();

const users = [
    { name: 'user', password: 'user' },
    { name: 'admin', password: Math.random().toString(32), canModify: true },
];
const initMessage = {"text": "Pollution isn't real", "username":"admin", "id": 0}

let messages = [];
messages.push(initMessage)
let lastId = 1;

function findUser(auth) {
    return users.find((u) =>
        u.name === auth.name &&
        u.password === auth.password);
}
///////////////////////////////////////////////////////////////////////////////

app.use(bodyParser.json());

// api endpoint to get all messages (open to anyone)
app.get('/', (req, res) => {
    console.log(messages);
    res.send(messages);
});

// api endpoint to post new message (restricted for users only).
app.put('/', (req, res) => {
    const user = findUser(req.body.auth || {});

    if (!user) {
        res.status(403).send({ ok: false, error: 'Access denied' });
        return;
    }

    const message = {};
    _.merge(message, req.body.message, {
        username: user.name,
        id: lastId++,
    }); 

    messages.push(message);
    res.send({ ok: true });
});

// modify message by id (restricted for admin only)
app.post('/', (req, res) => {
    const user = findUser(req.body.auth || {});
    if (!user || !user.canModify) {
        res.status(403).send({ok:false, error:"Access denied"});
        return;
    }
    console.log(messages.find((m) => m.id == req.body.messageId).text = req.body.messageText)
    res.send({ ok: true });
});

app.listen(3000);
console.log('Listening on port 3000...');
