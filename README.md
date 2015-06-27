# Cloduflare-Nginx-UpdateIPs [![Build Status](https://travis-ci.org/Matt3o12/cloudflare-nginx-updateips.svg?branch=master)](https://travis-ci.org/Matt3o12/cloudflare-nginx-updateips) #

Cloduflare-Nginx-UpdateIPs collects all of cloudflare IPs and formats them so that nginx understands it. You should run this script periodically so that nginx is up-to-date with CloudFlare's IPs and your server logs won't miss the real visitor's IP address. 

## Installation & Usage ##

Installing it is pretty straightforward. The only requirement is python's [requests][requests-pypi] libaray. To install it, just run:

    pip install requests

Then, clone this repo and run:

    python updateIPs.py > /etc/nginx/cloudflare.conf

You may have to replace `/etc/nginx` with `/usr/local/etc/nginx` or `/usr/local/nginx/conf` depending on your installation. For more information checkout [nginx's manual][nginx-manual]. 

If you don't have git installed, you can also download the most recent [tarball][master-tarball] or [zipfile][master-zip].

This script works under `python` `2.7`, `3.3`, and `3.4`. It may work under a more recent version. If you're not sure, open a new issue and I will test it :)

### Using Docker ###

If you have docker installed, it is as simple as running:

    docker run --rm matt3o12/cloudflare-nginx-updateips > nginx_config_path/conf.d/cloudflare.conf

## Motivation ##

I wrote this script because I was annoyed that apache has `mod_cloudflare` which automatically restores the visitors IP address. I wanted a similar thing for nginx and decided to write this script which automatically produces an appropriate config file for nginx with the most recent IP addresses.

## Contribution ##
If you plan to contribute to this script, please make sure you run all tests before submitting a pull requests. It'd also be nice if you add additional tests so that your contribution is less likely to break.  

    python -m unittest test_updateIPs

In order to run the tests, you will need to install [mock][mock-pypi] if you're on python 2.7. Two of the tests are integration tests. Make sure you are connected to the internet and your firewall allows you to access cloudflare.com on port 443 (HTTPS) or these tests will fail.
 
## License ##
This software is released under the MIT Lincense.

The license file is located in this directory under LICENSE
or online at [http://opensource.org/licenses/MIT]()

[requests-pypi]: https://pypi.python.org/pypi/requests
[mock-pypi]: https://pypi.python.org/pypi/mock
[master-zip]: https://github.com/Matt3o12/cloudflare-nginx-updateips/archive/master.zip
[master-tarball]: https://github.com/Matt3o12/cloudflare-nginx-updateips/archive/master.tar.gz
[nginx-manual]: http://nginx.org/en/docs/beginners_guide.html

