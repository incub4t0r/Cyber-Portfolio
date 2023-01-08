# ninja | CSAW21 Quals

Hey guys come checkout this website i made to test my ninja-coding skills.

http://web.chal.csaw.io:5000/

## TL;DR 

Found out site had xss, also had ssti, blocks `:- _ ,config ,os, RUNCMD, base`, use request arguments to create variables and pass them in outside the raw string and use subclasses to access functions.

## Work

On first look, we have a webpage with a form that takes in a string and returns it. The first thing to try is to check for XSS with `{{7*7}}` which returns `49` inside a dialog box, and now we know that we are running Flask and Python.

While attempting a few other things, I found that the site was vulnerable to SSTI. I tried a few things, but the site blocked the following characters:
```
Sorry, the following keywords/characters are not allowed :- _ ,config ,os, RUNCMD, base
```

This became a little bit more complicated, but we can use filter bypasses to get around this. I found a great article on Medium that explains how to do this:
- https://medium.com/@nyomanpradipta120/jinja2-ssti-filter-bypasses-a8d3eb7b000f

Here I spent about an hour reading up on SSTI and Jinja2 with the following resources:
- https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/README.md#jinja2
- https://pequalsnp-team.github.io/cheatsheet/flask-jinja2-ssti

After about 40 variations of a raw string, I found the one string that worked and got the flag.

## Final String

`GET /submit?cls=__class__&sub=__subclasses__&value={{''[request.args.cls].mro()[2][request.args.sub]()[40]('flag.txt').read()}}`

## How does it work?

- I sent a `GET` request to the webpage, with `/submit?` followed directly by user defined variables instead of the normal `&value=`.
- This allows us to define methods such as `__class__` and `__subclasses__` without being filtered out because it is not in the raw string of `value`.
- Inside the raw string defined through `{{}}`, we use `request.args` to call our user defined variables. Usually it would be something more like
`{{ ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() }}`, which is shown [here](https://cobalt.io/blog/a-pentesters-guide-to-server-side-template-injection-ssti). `__class__` is defined through `cls`, and we can use `mro()` instead of `__mro__`
- Python indexing allows us to call the next method without using a `.` because `[request.args.sub] == .__subclasses__.`.
- I tested out `\tmp\flag.txt\` and `~\flag.txt`, the only one that worked was `flag.txt` (i guess the flag is in the same directory as the flask app)
- Combining everything, we get `GET /submit?cls=__class__&sub=__subclasses__&value={{''[request.args.cls].mro()[2][request.args.sub]()[40]('flag.txt').read()}}`

## Flag

flag{m0mmy_s33_1m_4_r34l_n1nj4}
