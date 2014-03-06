mail.cgi
========

Enable CGI
----------
* cd /etc/apache2/mods-available
* sudo vi mime.conf
* AddHandler cgi-script .cgi
* cd /etc/apache2/sites-enabled
* sudo vi 000-default

> <Directory /var/www>
Options +ExecCGI
</Directory> 

* sudo /etc/init.d/apache2 restart

Chmod
-----
* chmod a+x mail.cgi

Run
---
* Open browser and access http://your.web.server/mail.cgi


