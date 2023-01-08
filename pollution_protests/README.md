# Pollution Protests

- namespace: c3t/cowtryouts
- type: custom
- category: Web Security
- points: 1000

## Description

The well known Pollution Protest website has been operating for a few years now, protesting against mass environmental pollution. 
However, in recent times, it appears that the admin of Pollution Protest has been bribed by big oil to modify and remove posts from users. All posts have mysteriously disappeared, with a single post remaining from the admin.

You decide that you need to take this matter into your own hands, and want to show that the admin can't take away the people's voice. Can you modify the admin post to "hack the planet"?

## Details

You have been provided with an account as `user:user` over at the Pollution Protest frontend.
{{link_as("http", "/", "Pollution Protest message board")}}

Thankfully, the Pollution Protest REST API is publicly available. 
{{link_as("api", "/", "Pollution Protest REST API")}}


There is also source code available for the REST API and the frontend server.

{{link_as("http", "/static/source.js", "REST API source")}}

{{link_as("http", "/static/frontend.py", "frontend source")}}

Once you are able to change the admin post, be sure to check out {{link_as("http", "/checker", "the checker")}} for the flag.

## Hints

- There are two servers running. One is a REST API server, and the other is just a client/UI server. Only one of these needs to be attacked.
- What parts of the REST API authenticates the user? Read the source code.
- You really don't need the python server source. All you need is the request.

## Learning Objective

- Cadets learn about prototype pollution in js.

## Tags

- flask

## Attributes

- author: Daniel Chung
- event: FirstieTryoutsAY23-1
- organization: C3T
