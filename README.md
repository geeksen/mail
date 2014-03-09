mail.cgi
========

Enable CGI
----------
* sudo a2enmod cgi
* cd /etc/apache2/mods-available
* sudo vi mime.conf
> AddHandler cgi-script .cgi

* cd /etc/apache2/sites-enabled
* sudo vi 000-default
> &lt;Directory /var/www&gt; .. Options ExecCGI .. &lt;/Directory&gt;

* sudo /etc/init.d/apache2 restart

Install mail.cgi
----------------
* cd /var/www
* git clone https://github.com/geeksen/mail.git
* cd mail

Check
-----
* which perl
> /usr/local/bin/perl

* (modify the first line of source code, if necessary)
* vi mail.cgi
> #!/usr/local/bin/perl

* perl -c mail.cgi


Chmod
-----
* chmod a+x mail.cgi

Run
---
* Go to http://your.web.server/mail/mail.cgi

