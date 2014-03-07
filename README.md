mail.cgi
========

Enable CGI
----------
* cd /etc/apache2/mods-available
* sudo vi mime.conf
> AddHandler cgi-script .cgi

* cd /etc/apache2/sites-enabled
* sudo vi 000-default
> &lt;Directory /var/www&gt; .. Options ExecCGI .. &lt;/Directory&gt;

* sudo /etc/init.d/apache2 restart

Check Perl Path
---------------
* which perl
* update the first line of source code, if necessary

Chmod
-----
* chmod a+x mail.cgi

Run
---
* Go to http://your.web.server/mail.cgi
