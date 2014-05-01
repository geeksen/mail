mail.cgi
========

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
<Directory /var/www&gt;
Options ExecCGI
&lt;/Directory&gt;
```

* sudo /etc/init.d/apache2 restart

Install mail.cgi
----------------
* cd /var/www
* git clone https://github.com/geeksen/mail.git
* cd mail

Check Perl Path
-----
* which perl
```
/usr/bin/perl
```

* (if necessary, modify the first line of source code)
* vi mail.cgi
```perl
#!/usr/bin/perl
```

Set Your Own Encryption Key
--------------------------
* vi mail.cgi
```perl
my $KEY = 'too_many_secrets';
```

Chmod
-----
* chmod a+x mail.cgi

Run
---
* Go to http://your.web.server/mail/mail.cgi

