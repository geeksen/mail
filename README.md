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
* git clone https://github.com/geeksen/mail.git
* cd mail

Check Perl Path
---------------
* which perl
* if necessary, modify the first line of source code
** vi mail.cgi
*> #!/usr/local/bin/perl

Chmod
-----
* chmod a+x mail.cgi

Run
---
* Go to http://your.web.server/mail.cgi
