mail.cgi
========

Install Apache2
---------------
* sudo apt-get update
* sudo apt-get upgrade
* sudo apt-get install apache2

Enable CGI
----------
* sudo a2enmod cgi
* cd /etc/apache2/mods-available
* sudo vi mime.conf
```
AddHandler cgi-script .cgi
```

* cd /etc/apache2/sites-enabled
* sudo vi 000-default
```
<Directory /var/www>
Options ExecCGI ..
..
</Directory>
```

* sudo /etc/init.d/apache2 restart

Install mail.cgi
----------------
* cd /var/www
* git clone https://github.com/geeksen/mail.git
* cd mail

Set Your Own Encryption Key
---------------------------
* vi mail.cgi
```perl
my $KEY = 'too_many_secrets';
```

Chmod
-----
* chmod 705 mail.cgi

Run
---
* Go to http://your.web.server/mail/mail.cgi

