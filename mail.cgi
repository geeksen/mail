#!/usr/bin/perl

# //////
# --@-@
#     >  Geeksen's Lab.
# ____/  http://www.geeksen.com/
#
# Copyright (c) 2014 Terry Geeksen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

use strict;
use warnings;

use CGI qw/:param :header :upload/;
use Encode;

# Conf
my $LOCALE = 'en';           # ko, en ..
my $TIMEZONE = '+0900';      # +0900, KST, GMT ..
my $WIDTH = 770;
my $PAGESIZE = 10;
my $PAGELINK = 10;

# Hashes
my %m;
my %l;
#my %s;

# CGI
my $q;

my $script = $ENV{'SCRIPT_NAME'};
my $domain = $ENV{'SERVER_NAME'};

my $N;
my $M;

my ($num, $mode, $type, $back, $page, $time, $email, $userid, $passwd, $pop3_server, $mimepart);

my $buf = '';
my $total = 0;

&Main;

sub Main {
    $q = new CGI;

    $num = $q->param('num');
    $mode = $q->param('mode');
    $type = $q->param('type');
    $back = int($q->param('back'));
    $page = int($q->param('page'));
    $time = time();
    $email = '';
    $userid = $q->cookie(-name=>'mUSERID');
    $passwd = unpack('u', $q->cookie(-name=>'mPASSWD'));
    $pop3_server = $q->cookie(-name=>'mSERVER');
    $mimepart = $q->param('mimepart');

    if ($back > -1) { $back++; }

    if ($q->param('userid') ne '') {
        $userid = $q->param('userid');
        $passwd = $q->param('passwd');
        $pop3_server = $q->param('pop3_server');
    }

    if ($userid =~ /@/) { $email = $userid; }
    else { $email = $userid . '@' . $pop3_server; }

    &mLocale;

       if ($mode eq 'list')     { &List;     }
    elsif ($mode eq 'read')     { &Read;     }
    elsif ($mode eq 'delete')   { &Delete;   }
    elsif ($mode eq 'form')     { &Form;     }
    elsif ($mode eq 'send')     { &Send;     }
    elsif ($mode eq 'download') { &Download; }
    elsif ($mode eq 'logout')   { &Logout;   }
    else  { &LoginForm; }
}

sub List {
    my ($cookie1, $cookie2, $cookie3);
    my ($i, $j, $totalpage, $first, $last);

    &mUSER;
    &mPASS;
    &mSTAT;

    $totalpage = int(($total - 1) / $PAGESIZE) + 1;
    if ($page == 0) { $page = 1; }
    if ($totalpage == 0) { $totalpage = 1; }
    if ($page > $totalpage) { $page = $totalpage; }

    if ($q->param('userid') ne '') {
        $cookie1 = $q->cookie(
            -name=>'mUSERID',
            -value=>$userid,
            -path=>'/',
            -domain=>$domain,
        );
        $cookie2 = $q->cookie(
            -name=>'mPASSWD',
            -value=>pack('u', $passwd),
            -path=>'/',
            -domain=>$domain,
        );
        $cookie3 = $q->cookie(
            -name=>'mSERVER',
            -value=>$pop3_server,
            -path=>'/',
            -domain=>$domain,
        );

        print $q->header(
            -charset=>'utf-8',
            -cookie=>[$cookie1, $cookie2, $cookie3],
        );
    }
    else { print $q->header(-charset=>'utf-8'); }

    &Head($email);
    print <<EOT;
  <tr>
    <td class=td_right><a href='$script?mode=logout'>$l{'logout'}</a></td>
  </tr>
</table>

<script type='text/javascript'>
function CheckAll() {
  is_checked = null;
  for(i = 0; i < document.forms[0].elements.length; i++) {
    if(document.forms[0].elements[i].name.indexOf('mail_') == 0 &&
      document.forms[0].elements[i].type.toUpperCase() == 'CHECKBOX') {
      is_checked = document.forms[0].elements[i].checked;
      document.forms[0].elements[i].checked = !is_checked;
    }
  }
}
</script>

<form method=post action='$script'>
<table border=0 width='$WIDTH'>
  <tr>
    <td>
EOT

    print "      <a href='$script?mode=form&amp;type=compose";
    print "&amp;page=$page'>$l{'compose'}</a>\n";

    print <<EOT;
    </td>
    <td class=td_right>
        $l{'total'} : $total, $l{'page'} : $page / $totalpage
    </td>
  </tr>
</table>

<table border=0 width='$WIDTH' cellpadding=4>
  <tr>
    <th>
      <input type=checkbox name=mark1 onClick='CheckAll();'>
      $l{'no'}
      <input type=hidden name=mode value='delete'>
      <input type=hidden name=page value='$page'>
    </th>
    <th>$l{'from'}</th>
    <th>$l{'subject'}</th>
    <th>$l{'date'}</th>
  </tr>
EOT

    $first = $total - ($page - 1) * $PAGESIZE;
    if ($first > $PAGESIZE) { $last = $first - $PAGESIZE + 1; }
    else { $last = 1; }

    for ($i = $first; $i >= $last; $i--) {
        &mTOP($i);

        if (($i % 2) == 0) {
            print <<EOT;
  <tr>
    <td class='list_bg1'>
      <input type=checkbox name=mail_$i value='1'> $i $m{'priority'}
    </td>
    <td class='list_bg1'>$m{'from'}</td>
    <td class='list_bg1'>
      <a href='$script?mode=read&amp;num=$i&amp;page=$page'>$m{'subject'}</a>
    </td>
    <td class='list_bg1'>$m{'date'}</td>
  </tr>
EOT
        }
        else {
            print <<EOT;
  <tr>
    <td class='list_bg2'>
      <input type=checkbox name=mail_$i value='1'>
      $i $m{'priority'}
    </td>
    <td class='list_bg2'>$m{'from'}</td>
    <td class='list_bg2'>
      <a href='$script?mode=read&amp;num=$i&amp;page=$page'>$m{'subject'}</a>
    </td>
    <td class='list_bg2'>$m{'date'}</td>
  </tr>
EOT
        }
    }
    &mQUIT;

    print <<EOT;
  <tr>
    <td><input type=checkbox name=mark2 onClick='CheckAll();'></td>
    <td class=td_center colspan=3>
EOT

    $i = int(($page - 1) / $PAGELINK) * $PAGELINK + 1;
    if ($i > $PAGELINK) {
        print  "      [<a href='$script?mode=list'>1</a>]\n";
        printf "      [<a href='$script?mode=list&amp;page=%d'>", $i - 1;
        print  "$l{'prev'}</a>]\n";
    }
    for ($j = 0; $i <= $totalpage && $j < $PAGELINK; $i++, $j++) {
        if ($i == $page) {
            print "      [$i]\n";
        }
        else {
            print "      [<a href='$script?mode=list&amp;page=$i'>$i</a>]\n";
        }
    }
    if ($i <= $totalpage) {
        print "      [<a href='$script?mode=list&amp;page=$i'>";
        print "$l{'next'}</a>]\n";
        print "      [<a href='$script?mode=list&amp;page=$totalpage'>";
        print "$totalpage</a>]\n";
    }

    print <<EOT;
    </td>
  </tr>
</table>

<table border=0 width='$WIDTH'>
  <tr>
    <td><hr></td>
  </tr>
</table>

<table border=0 width='$WIDTH'>
  <tr>
    <td><input type=submit value='$l{'delete_submit'}'></td>
    <td class=td_right>
EOT

    print "      <a href='$script?mode=list&amp;page=$page&amp;time=$time'>";
    print "$l{'reload'}</a> |\n";

    if ($page > 1) {
        printf "    <a href='$script?mode=list&amp;page=%d'>", $page - 1;
        print  "$l{'prev'}</a> |\n";
    }
    else { print "      $l{'prev'} |\n"; }

    if ($page < $totalpage) {
        printf "    <a href='$script?mode=list&amp;page=%d'>", $page + 1;
        print  "$l{'next'}</a>\n";
    }
    else { print "      $l{'next'}\n"; }

    print "    </td>\n  </tr>\n</table>\n";
    &Tail;
}

sub Read {
    my ($i);
    my ($attachment_name, $attachment_type);
    my ($attachment_size, $attachment_content_id);

    &mUSER;
    &mPASS;
    &mSTAT;
    &mRETR($num, $mimepart);
    &mQUIT;

    print $q->header(-charset=>'utf-8');
    &Head($m{'subject'});
    print <<EOT;
  <tr>
    <td class=td_right><a href='$script?mode=logout'>$l{'logout'}</a></td>
  </tr>
</table>

<form method=post action='$script'>
<table border=0 width='$WIDTH'>
  <tr>
    <td>
EOT

    print "      <a href='$script?mode=form&amp;type=compose";
    print "&amp;page=$page'>$l{'compose'}</a> |\n";
    print "      <a href='$script?mode=form&amp;type=reply&amp;num=$num";
    print "&amp;page=$page&amp;mimepart=$mimepart'>$l{'reply'}</a> |\n";
    print "      <a href='$script?mode=form&amp;type=reply_all&amp;num=$num";
    print "&amp;page=$page&amp;mimepart=$mimepart'>$l{'reply_all'}</a> |\n";
    print "      <a href='$script?mode=form&amp;type=forward&amp;num=$num";
    print "&amp;page=$page&amp;mimepart=$mimepart'>$l{'forward'}</a> |\n";
    print "      <a href='$script?mode=form&amp;type=forward_attach";
    print "&amp;num=$num&amp;page=$page&amp;mimepart=$mimepart'>";
    print "$l{'forward_attach'}</a> |\n";
    print "      <a href='$script?mode=read&amp;type=headers&amp;num=$num";
    print "&amp;page=$page&amp;mimepart=$mimepart&amp;back=$back'>";
    print "$l{'headers'}</a> |\n";

    if ($mimepart eq '') {
        print "      <a href='$script?mode=delete&amp;num=$num&amp;page=$page";
        print "&amp;time=$time&amp;back=-1'>$l{'delete'}</a>\n";
    }
    else { print "      $l{'delete'}\n"; }

    print <<EOT;
    </td>
    <td class=td_right>
EOT

    if ($num < $total) {
        printf "      <a href='$script?mode=read&amp;num=%d", $num + 1;
        print  "&amp;page=$page&amp;back=$back'>$l{'prev'}</a> |\n";
    }
    else { print "      $l{'prev'} |\n"; }

    if ($num > 1) {
        printf "      <a href='$script?mode=read&amp;num=%d", $num - 1;
        print  "&amp;page=$page&amp;back=$back'>$l{'next'}</a> |\n";
    }
    else { print "      $l{'next'} |\n"; }

    if ($back == -1) {
        print "      <a href='$script?mode=list&amp;page=$page";
        print "&amp;time=$time'>$l{'list'}</a>\n";
    }
    else {
        print "      <a href='JavaScript:history.go(-$back);'>";
        print "$l{'list'}</a>\n";
    }

    print <<EOT;
    </td>
  </tr>
</table>

<table border=0 width='$WIDTH'>
  <tr>
    <td><hr></td>
  </tr>
</table>

<table border=0 width='$WIDTH' cellpadding=4>
  <tr>
    <th class=th_150>$l{'no'}</th>
    <td>$num / $total</td>
  </tr>
  <tr>
    <th>$l{'from'}</th>
    <td>$m{'from'}</td>
  </tr>
  <tr>
    <th>$l{'to'}</th>
    <td>$m{'to'}</td>
  </tr>
EOT

    if ($m{'cc'} ne '') {
        print <<EOT;
  <tr>
    <th>$l{'cc'}</th>
    <td>$m{'cc'}</td>
  </tr>
EOT
    }

    print <<EOT;
  <tr>
    <th>$l{'date'}</th>
    <td>$m{'date'}</td>
  </tr>
  <tr>
    <th>$l{'subject'}</th>
    <td>$m{'subject'}</td>
  </tr>
EOT

    if ($m{'attachment_count'} > 0) {
        print <<EOT;
  <tr>
    <th>$l{'attachment'}</th>
    <td>
EOT

        for ($i = 0; $i < $m{'attachment_count'}; $i++) {
            $attachment_name = $m{'attachment'}->[$i]->{'name'};
            $attachment_size = &mSize($m{'attachment'}->[$i]->{'size'});
            $attachment_type = $m{'attachment'}->[$i]->{'type'};
            $attachment_content_id = $m{'attachment'}->[$i]->{'content_id'};

            if ($attachment_content_id eq '') {
                if ($attachment_type =~ /message\/rfc822/i) {
                    print "<a href='$script?mode=read&amp;num=$num";
                    print "&amp;page=$page&amp;mimepart=$mimepart\.$i";
                    print "&amp;back=$back'>$attachment_name</a>";
                    print "($attachment_size) ";
                }
                else {
                    $attachment_name =~ s/ /%20/g;
                    print "<a href='$script?mode=download&amp;num=$num";
                    print "&amp;mimepart=$mimepart&amp;time=$time";
                    print "&amp;attachment=$i/$attachment_name'>";
                    $attachment_name =~ s/%20/ /g;
                    print "$attachment_name</a>($attachment_size) ";
                }
            }
        }
        print "  </td>\n  </tr>\n";
    }

    print <<EOT;
</table>

<table border=0 width='$WIDTH'>
  <tr>
    <td><hr></td>
  </tr>
</table>

<table border=0 width='$WIDTH'>
  <tr>
EOT

    if ($type ne 'headers') {
        print "  <td class='mail_body'>\n";
    }
    else { print "  <td>\n"; }

    if ($type eq 'headers') {
        print "<pre>" . &mEncodeHTML($m{'headers'}) . "</pre>";
    }
    else { print $m{'body'}; }

    print <<EOT;
    </td>
  </tr>
</table>

<table border=0 width='$WIDTH'>
  <tr>
    <td><hr></td>
  </tr>
</table>

<table border=0 width='$WIDTH'>
  <tr>
    <td>
EOT

    print "      <a href='$script?mode=form&amp;type=compose";
    print "&amp;page=$page'>$l{'compose'}</a> |\n";
    print "      <a href='$script?mode=form&amp;type=reply&amp;num=$num";
    print "&amp;page=$page&amp;mimepart=$mimepart'>$l{'reply'}</a> |\n";
    print "      <a href='$script?mode=form&amp;type=reply_all&amp;num=$num";
    print "&amp;page=$page&amp;mimepart=$mimepart'>$l{'reply_all'}</a> |\n";
    print "      <a href='$script?mode=form&amp;type=forward&amp;num=$num";
    print "&amp;page=$page&amp;mimepart=$mimepart'>$l{'forward'}</a> |\n";
    print "      <a href='$script?mode=form&amp;type=forward_attach";
    print "&amp;num=$num&amp;page=$page&amp;mimepart=$mimepart'>";
    print "$l{'forward_attach'}</a> |\n";
    print "      <a href='$script?mode=read&amp;type=headers&amp;num=$num";
    print "&amp;page=$page&amp;mimepart=$mimepart&amp;back=$back'>";
    print "$l{'headers'}</a> |\n";

    if ($mimepart eq '') {
        print "      <a href='$script?mode=delete&amp;num=$num";
        print "&amp;page=$page&amp;time=$time&amp;back=-1'>";
        print "$l{'delete'}</a>\n";
    }
    else { print "      $l{'delete'}\n"; }

    print <<EOT;
    </td>
    <td class=td_right>
EOT

    if ($num < $total) {
        printf "      <a href='$script?mode=read&amp;num=%d", $num + 1;
        print  "&amp;page=$page&amp;back=$back'>$l{'prev'}</a> |\n";
    }
    else { print "      $l{'prev'} |\n"; }

    if ($num > 1) {
        printf "      <a href='$script?mode=read&amp;num=%d", $num - 1;
        print  "&amp;page=$page&amp;back=$back'>$l{'next'}</a> |\n";
    }
    else { print "      $l{'next'} |\n"; }

    if ($back == -1) {
        print "      <a href='$script?mode=list&amp;page=$page";
        print "&amp;time=$time'>$l{'list'}</a>\n";
    }
    else {
        print "      <a href='JavaScript:history.go(-$back);'>";
        print "$l{'list'}</a>\n";
    }

    print <<EOT;
    </td>
  </tr>
</table>
EOT
    &Tail;
}

sub Delete {
    my ($i);
    my ($name);

    &mUSER;
    &mPASS;
    &mSTAT;
    if ($num > 0) { &mDELE($num); }
    else {
        for ($i = 1; $i <= $total; $i++) {
            $name = 'mail_' . $i;
            if ($q->param($name) == 1) { &mDELE($i); }
        }
    }
    &mQUIT;

    print $q->header(-charset=>'utf-8');
    if ($num > 1) {
        $num--;
        &Reload("$script?mode=read&amp;num=$num" .
            "&amp;page=$page&amp;time=$time&amp;back=-1");
    }
    else { &Reload("$script?mode=list&amp;page=$page"); }
}

sub Form {
    my ($to, $cc, $subject, $body, $i);
    my ($attachment_name, $attachment_type);
    my ($attachment_size, $attachment_content_id);
    my (@tmp);

    $to = $q->param('to');
    $subject = $q->param('subject');

    if ($type ne 'compose') {
        &mUSER;
        &mPASS;
        &mRETR($num, $mimepart);
        &mQUIT;

        $body = $m{'body'};
        $body =~ s/<br>/\r\n/gi;
        $body =~ s/<\/?[!A-Za-z]+[^>]*\>//gi;
        $body =~ s/\r\n\r\n/\r\n/g;
        $body =~ s/\r\n/\r\n>\ /g;
    }

    if ($type =~ /reply/) {
        $to = $m{'from'};
        $cc = $m{'to'} . ', ' . $m{'cc'};

        @tmp = split(/[,;]/, $cc);
        $cc = '';

        for ($i = 0; $i <= $#tmp; $i++) {
            if ($tmp[$i] =~ /$email/) { next; }
            if ($i > 0 && $cc ne '') { $cc .= ', '; }
            if ($tmp[$i] =~ /@/) { $cc .= $tmp[$i]; }
        }
        if ($type eq 'reply') { $cc = ''; }

        $subject = $m{'subject'};
        $subject =~ s/^RE://i;
        $subject = 'RE:' . $subject;
    }
    elsif ($type =~ /forward/) {
        $subject = $m{'subject'};
        $subject =~ s/^FW://i;
        $subject = 'FW:' . $subject;
    }

    print $q->header(-charset=>'utf-8');
    &Head($l{$type});
    print <<EOT;
  <tr>
    <td class=td_right><a href='$script?mode=logout'>$l{'logout'}</a></td>
  </tr>
</table>

<form method=post action='$script' enctype='multipart/form-data'>
<table border=0>
  <tr>
    <th class=th_150>$l{'sender'}</th>
    <td>
      <input type=text name=from size=40 value='<$email>'>
      <input type=hidden name=mode value='send'>
      <input type=hidden name=type value='$type'>
      <input type=hidden name=num value='$num'>
      <input type=hidden name=page value='$page'>
    </td>
  </tr>
  <tr>
    <th>$l{'receiver'}</th>
    <td><input type=text name=to size=40 value='$to'></td>
  </tr>
  <tr>
    <th>$l{'cc'}</th>
    <td><input type=text name=cc size=40 value='$cc'></td>
  </tr>
  <tr>
    <th>$l{'bcc'}</th>
    <td><input type=text name=bcc size=40></td>
  </tr>
  <tr>
    <th>$l{'subject'}</th>
    <td><input type=text name=subject size=40 value='$subject'></td>
  </tr>
  <tr>
    <th>$l{'smtp_server'}</th>
    <td><input type=text name=smtp_server size=40 value='$pop3_server'></td>
  </tr>
  <tr>
    <td colspan=2><textarea name=body rows=20 cols=75>
EOT

    if ($type =~ /reply/ || $type eq 'forward') {
        print "\n\n";
        print "> ---------- $l{'original_message'} ----------\n";
        print "> $l{'from'} : $m{'from'}\n";
        print "> $l{'to'} : $m{'to'}\n";
        if ($m{'cc'} ne '') { print "> $l{'cc'} : $m{'cc'}\n"; }
        print "> $l{'date'} : $m{'date'}\n";
        print "> $l{'subject'} : $m{'subject'}\n>\n> ";
        print $body;
    }
    elsif ($type eq 'forward_attach') {
        print $l{'original_message_included'};
    }

    print <<EOT;
</textarea>
    </td>
  </tr>
  <tr>
    <th>$l{'attachment'}</th>
    <td><input type=file name=file1 size=40></td>
  </tr>
  <tr>
    <th>$l{'attachment'}</th>
    <td><input type=file name=file2 size=40></td>
  </tr>
  <tr>
    <th>$l{'attachment'}</th>
    <td><input type=file name=file3 size=40></td>
  </tr>
EOT

    if ($type eq 'forward' && $m{'attachment_count'} > 0) {
        print <<EOT;
  <tr>
    <th>$l{'attachment'}</th>
    <td>
EOT

        for ($i = 0; $i < $m{'attachment_count'}; $i++) {
            $attachment_name = $m{'attachment'}->[$i]->{'name'};
            $attachment_size = &mSize($m{'attachment'}->[$i]->{'size'});
            $attachment_type = $m{'attachment'}->[$i]->{'type'};
            $attachment_content_id = $m{'attachment'}->[$i]->{'content_id'};

            if ($attachment_content_id eq '') {
                print "<input type=checkbox name=attachment value='$i'";
                print " checked>";
                if ($attachment_type =~ /message\/rfc822/i) {
                    print "<a href='$script?mode=read&amp;num=$num";
                    print "&amp;page=$page&amp;mimepart=$mimepart\.$i";
                    print "&amp;back=$back'>$attachment_name";
                    print "($attachment_size)</a> ";
                }
                else {
                    $attachment_name =~ s/ /%20/g;
                    print "<a href='$script?mode=download&amp;num=$num";
                    print "&amp;mimepart=$mimepart&amp;time=$time";
                    print "&amp;attachment=$i/$attachment_name'>";
                    $attachment_name =~ s/%20/ /g;
                    print "$attachment_name($attachment_size)</a> ";
                }
            }
            else {
                print "<input type=hidden name=attachment value='$i'>";
            }
        }
        print "  </td>\n  </tr>\n";
    }

    if ($type eq 'forward_attach') {
        print "  <tr>  <th>$l{'attachment'}</th>\n";
        print "  <td><input type=checkbox name=attachment value='0' checked>";
        print "$m{'subject'}(" . &mSize($m{'headers'}) . ")</td>\n  </tr>\n";
    }

    print <<EOT;
  <tr>
    <td colspan=2><hr></td>
  </tr>
  <tr>
    <td><input type=submit value='$l{'send_submit'}'></td>
    <td class=td_right>
      <a href='javascript:history.back();'>$l{'cancel'}</a>
    </td>
  </tr>
</table>
EOT
    &Tail;
}

sub Send {
    my ($host, $sin, $buf, $auth);
    my ($encoding, $boundary, $boundary_alternative);
    my ($from, $to, $cc, $bcc, $subject, $date, $smtp_server, $body);
    my ($filehandle, $filehandle1, $filehandle2, $filehandle3);
    my ($filetype, $filename, $file, $tmp, $i);
    my ($attachment_name, $attachment_type);
    my (@to, @cc, @bcc, @attachment);

    $from = $q->param('from');
    $to = $q->param('to');
    $cc = $q->param('cc');
    $bcc = $q->param('bcc');
    $subject = $q->param('subject');
    $date = &mGetDate;
    $smtp_server = $q->param('smtp_server');
    $body = $q->param('body');
    @attachment = $q->param('attachment');
    $filehandle1 = $q->param('file1');
    $filehandle2 = $q->param('file2');
    $filehandle3 = $q->param('file3');
    $boundary = 'MultiPart_Boundary_' . $time;
    $boundary_alternative = 'MultiPart_Alternative_Boundary_' . $time;

    if ($from eq '')    { &Error($l{'from_error'}); }
    if ($to eq '')      { &Error($l{'to_error'}); }
    if ($subject eq '') { $subject = $l{'subject_unspecified'}; }
    if ($body eq '')    { &Error($l{'body_error'}); }
    if ($smtp_server eq '')    { &Error($l{'smtp_server_error'}); }

    if ($to  ne '') { @to  = split(/[,;]/, $to);  }
    if ($cc  ne '') { @cc  = split(/[,;]/, $cc);  }
    if ($bcc ne '') { @bcc = split(/[,;]/, $bcc); }

    if ($subject =~ /[\xA1-\xFE]/) {
        $subject = &mEncodeBase64($subject);
        $subject =~ s/[\n\r]//g;
        $subject = '=?utf-8?B?' . $subject . '?=';
    }

    $encoding = '7bit';
    $body =~ s/\r\n\./\r\n \./g;
    if ($body =~ /[\xA1-\xFE]/) {
        $encoding = 'base64';
        $body = &mEncodeBase64($body);
    }

    if ($num > 0) {
        &mUSER;
        &mPASS;
        &mRETR($num, $mimepart);
        &mQUIT;
    }

    socket($N, 2, 1, 6);

    $host = gethostbyname($smtp_server);
    $sin = pack('S n a4 x8', 2, 25, $host);
    if (!connect($N, $sin)) { &Error($l{'connect_error'}); }

    select($N);
    $| = 1;

    select(STDOUT);
    binmode($N);

    $buf = <$N>;
    if ($buf =~ /^[45]/) { &Error($buf); }

    $auth = 0;
    print $N "EHLO $smtp_server\r\n";
    while (1) {
        $buf = <$N>;
        if ($buf =~ /^[45]/) { &Error($buf); }
        if ($buf =~ /250-AUTH/i) { $auth = 1; }
        if ($buf =~ /^250 /) { last; }
    }

    if ($auth == 1) {
        print $N "AUTH LOGIN\r\n";
        $buf = <$N>;
        if ($buf =~ /^[45]/) { &Error($buf); }

        print $N &mEncodeBase64($userid);
        $buf = <$N>;
        if ($buf =~ /^[45]/) { &Error($buf); }

        print $N &mEncodeBase64($passwd);
        $buf = <$N>;
        if ($buf =~ /^[45]/) { &Error($buf); }
    }

    print $N "MAIL FROM: $from\r\n";
    $buf = <$N>;
    if ($buf =~ /^[45]/) { &Error($buf); }

    if ($to ne '') {
        foreach $tmp (@to) {
            if ($tmp =~ /@/) {
                print $N "RCPT TO: $tmp\r\n";
                $buf = <$N>;
                if ($buf =~ /^[45]/) { &Error($buf); }
            }
        }
    }

    if ($cc ne '') {
        foreach $tmp (@cc) {
            if ($tmp =~ /@/) {
                print $N "RCPT TO: $tmp\r\n";
                $buf = <$N>;
                if ($buf =~ /^[45]/) { &Error($buf); }
            }
        }
    }

    if ($bcc ne '') {
        foreach $tmp (@bcc) {
            if ($tmp =~ /@/) {
                print $N "RCPT TO: $tmp\r\n";
                $buf = <$N>;
                if ($buf =~ /^[45]/) { &Error($buf); }
            }
        }
    }

    print $N "DATA\r\n";
    $buf = <$N>;
    if ($buf =~ /^[45]/) { &Error($buf); }

    print $N "Reply-to: $from\r\n";
    print $N "From: $from\r\n";

    if ($to  ne '') { print $N "To: $to\r\n";   }
    if ($cc  ne '') { print $N "CC: $cc\r\n";   }
    if ($bcc ne '') { print $N "BCC: $bcc\r\n"; }

    print $N "Subject: $subject\r\n";
    print $N "Date: $date\r\n";
    print $N "MIME-Version: 1.0\r\n";
    print $N "X-Mailer: http://$ENV{'SERVER_NAME'}$script\r\n";
    print $N "X-Sender-IP: $ENV{'REMOTE_ADDR'}\r\n";

    if ($#attachment > -1 ||
        $filehandle1 ne '' || $filehandle2 ne '' || $filehandle3 ne '') {
        print $N "Content-Type: multipart/mixed;";
        print $N " boundary=\"$boundary\"\r\n\r\n";
    }
    else {
        print $N "Content-Type: text/plain; charset=utf-8\r\n";
        print $N "Content-Transfer-Encoding: $encoding\r\n\r\n";
    }

    if ($#attachment > -1 ||
        $filehandle1 ne '' || $filehandle2 ne '' || $filehandle3 ne '') {
        print $N "--$boundary\r\n";
        print $N "Content-Type: text/plain; charset=utf-8\r\n";
        print $N "Content-Transfer-Encoding: $encoding\r\n\r\n";
        print $N "$body\r\n\r\n";

        foreach $filehandle ($filehandle1, $filehandle2, $filehandle3) {
            if ($filehandle eq '') { next; }

            $tmp = ''; $file = '';
            while (read($filehandle, $tmp, 1024)) { $file .= $tmp; }
            $filetype = $q->uploadInfo($filehandle)->{'Content-Type'};
            $filename = $q->uploadInfo($filehandle)->{'Content-Disposition'};
            close($filehandle);

            if ($filetype eq '') { $filetype = 'application/octet-stream'; }
            if ($filename =~ /.*filename=(.*)/i) {
                $filename = $1;
                $filename =~ s/[\r";]//g;
            }

            $file = &mEncodeBase64($file);

            $filename =~ s/.*\\//g;
            $filename =~ s/.*\///g;
            if ($filename =~ /[\xA1-\xFE]/) {
                $filename = &mEncodeBase64($filename);
                $filename =~ s/[\n\r]//g;
                $filename = '=?utf-8?B?' . $filename . '?=';
            }

            print $N "--$boundary\r\n";
            print $N "Content-Type: $filetype; name=\"$filename\"\r\n";
            print $N "Content-Transfer-Encoding: base64\r\n";
            print $N "Content-Disposition: attachment;";
            print $N " filename=\"$filename\"\r\n\r\n";
            print $N "$file\r\n\r\n";
        }

        if ($type eq 'forward') {
            for ($i = 0; $i < $m{'attachment_count'}; $i++) {
                if (grep(/^$i$/, @attachment) > 0) {
                    $attachment_name = $m{'attachment'}->[$i]->{'name'};
                    $attachment_type = $m{'attachment'}->[$i]->{'type'};

                    print $N "--$boundary\r\n";
                    print $N "Content-Type: $attachment_type;";
                    print $N " name=\"$attachment_name\"\r\n";
                    print $N "Content-Transfer-Encoding: base64\r\n";
                    print $N "Content-Disposition: attachment;";
                    print $N " filename=\"$attachment_name\"\r\n\r\n";
                    print $N &mEncodeBase64($m{'attachment'}->[$i]->{'body'});
                    print $N "\r\n\r\n";
                }
            }
        }
        elsif ($type eq 'forward_attach') {
            print $N "--$boundary\r\n";
            print $N "Content-Type: message/rfc822; charset=utf-8\r\n";
            print $N "Content-Transfer-Encoding: 7bit\r\n\r\n";
            print $N "$m{'headers'}\r\n\r\n";
        }
        print $N "--$boundary--\r\n";
    }
    else {
        print $N "$body\r\n";
    }

    print $N "\r\n.\r\n";
    $buf = <$N>;
    if ($buf =~ /^[45]/) { &Error($buf); }
    print $N "QUIT\r\n";
    close($N);

    print $q->header(-charset=>'utf-8');
    if ($userid ne '') { &Reload("$script?mode=list&amp;page=$page"); }
    else { &Reload('/'); }
}

sub Download {
    my ($attachment) = $q->param('attachment');
    my ($tmp, $attachment_num, $attachment_name);
    my ($attachment_type, $attachment_size);

    &mUSER;
    &mPASS;
    &mRETR($num, $mimepart);
    &mQUIT;

    ($attachment_num, $attachment_name) = split(/\//, $attachment);
    $attachment_type =  $m{'attachment'}->[$attachment_num]->{'type'};
    $attachment_type =~ s/\s//g;
    $attachment_size =  $m{'attachment'}->[$attachment_num]->{'size'};
    binmode(STDOUT);

    if ($attachment_name =~ /\.png$/i) {
        $attachment_type = 'image/png';
    }
    elsif ($attachment_name =~ /\.gif$/i) {
        $attachment_type = 'image/gif';
    }
    elsif ($attachment_name =~ /\.jpg$/i) {
        $attachment_type = 'image/jpeg';
    }
    elsif ($attachment_name =~ /\.txt$/i) {
        $attachment_type = 'text/plain';
    }
    elsif ($attachment_name =~ /\.htm*$/i) {
        $attachment_type = 'text/html';
    }

    if ($attachment_type =~ /image\/png/i ||
        $attachment_type =~ /image\/gif/i ||
        $attachment_type =~ /image\/jpeg/i ||
        $attachment_type =~ /text\/plain/i ||
        $attachment_type =~ /text\/html/i) {
        print "Content-Disposition: inline; filename=\"$attachment_name\"\n";
    }
    else {
        print "Content-Disposition: attachment;";
        print " filename=\"$attachment_name\"\n";
    }

    print "Content-Transfer-Encoding: binary\n";
    print "Accept-Ranges: bytes\n";
    print "Content-Length: $attachment_size\n";
    print "Connection: close\n";
    print "Content-Type: $attachment_type\n\n";
    print $m{'attachment'}->[$attachment_num]->{'body'};
}

sub Logout {
    my ($cookie1, $cookie2, $cookie3);

    $cookie1 = $q->cookie(
        -name=>'mUSERID',
        -value=>'',
        -path=>'/',
        -domain=>$domain,
    );
    $cookie2 = $q->cookie(
        -name=>'mPASSWD',
        -value=>'',
        -path=>'/',
        -domain=>$domain,
    );
    $cookie3 = $q->cookie(
        -name=>'mSERVER',
        -value=>'',
        -path=>'/',
        -domain=>$domain,
    );

    print $q->header(
        -charset=>'utf-8',
        -cookie=>[$cookie1, $cookie2, $cookie3],
    );
    &Reload($script);
}

sub LoginForm {
    print $q->header(-charset=>'utf-8');
    &Head($l{'login_title'});
    print <<EOT;
  <tr>
    <td class=td_right><a href='http://www.geeksen.com'>Home</a></td>
  </tr>
</table>

<form method=post action='$script'>
<table border=0>
  <tr>
    <td>$l{'userid'}</td>
    <td>
      <input type=text name=userid value='test\@geeksen.com' size=20>
      <input type=hidden name=mode value='list'>
    </td>
  </tr>
  <tr>
    <td>$l{'passwd'}</td>
    <td><input type=password name=passwd size=20></td>
  </tr>
  <tr>
    <td>$l{'pop3_server'}</td>
    <td>
      <input type=text name=pop3_server value='geeksen.com' size=20>
      <input type=submit value='$l{'login_submit'}'></td>
  </tr>
</table>

<table border=0 width='$WIDTH'>
  <tr>
    <td><hr></td>
  </tr>
</table>

<table border=0 width='$WIDTH'>
  <tr>
    <td class=td_right>
      <a href='http://www.geeksen.com/'>Download Source</a>
    </td>
  </tr>
</table>
EOT
    &Tail;
}

sub Head {
    my $title = $_[0];

    print <<EOT;
<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01//EN'
  'http://www.w3.org/TR/html4/strict.dtd'>

<html>
<head>
  <title>Geeksen Mail</title>
  <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
  <style type='text/css'>
    body, td {
      background-color:#ffffff; color:#666666;
      font-size:9pt; font-family:tahoma, geneva, sans-serif;
    }
    th {
      background-color:#666666; color:#ffffff;
      font-size:9pt; font-family:tahoma, geneva, sans-serif;
    }
    input, select { font-size:9pt; font-family:tahoma, geneva, sans-serif; }
    img { border:0px; }
    hr { height:1px; }
    .th_150 { width:150px; }
    .td_right { text-align:right; }
    .td_center { text-align:center; }
    .large { color:#666666; font-size:14pt; font-family:tahoma, geneva, sans-serif; }
    .list_bg1 { background-color:#ffffff; }
    .list_bg2 { background-color:#eeeeee; }
    .mail_body {
EOT

    if ($m{'bgcolor'} ne '') {
        print "      background-color:$m{'bgcolor'};\n";
    }
    if ($m{'background'} ne '') {
        print "      background-image:url($m{'background'});\n";
    }

    print <<EOT;
    }

    a:link { color:#0066cc; text-decoration:none; }
    a:active { color:#0066cc; text-decoration:none; }
    a:visited { color:#0066cc; text-decoration:none; }
    a:hover { color:#0066cc; text-decoration:underline; }
  </style>
</head>

<body>

<table border=0 width='$WIDTH'>
  <tr>
    <td class='large'>$title</td>
  </tr>
EOT
}

sub Tail {
    print <<EOT;

</form>
</body>
</html>
EOT
}

sub Error {
    my $message = $_[0];

    print $q->header(-charset=>'utf-8');
    &Head($message);
    print "</table>\n</body>\n</html>";

    exit;
}

sub Reload {
    my $url = $_[0];

    print "<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN'>";
    print "\n\n";
    print "<html>\n<head>\n";
    print "  <title>Reload</title>\n";
    print "  <meta http-equiv='refresh' content='0;url=$url'>\n";
    print "</head>\n<body>\n</body>\n</html>";
}

sub mUSER {
    my ($host, $sin, $tmp);

    if ($userid eq '') { &Error($l{'userid_error'}); }
    if ($passwd eq '') { &Error($l{'passwd_error'}); }
    if ($pop3_server eq '') { &Error($l{'pop3_server_error'}); }

    socket($M, 2, 1, 6);

    $host = gethostbyname($pop3_server);
    $sin = pack('S n a4 x8', 2, 110, $host);
    if (!connect($M, $sin)) { &Error($l{'connect_error'}); }

    select($M);
    $| = 1;

    select(STDOUT);
    binmode($M);

    $buf = <$M>;
    if ($buf =~ /^-ERR/) { &Error($buf); }

    print $M "USER $userid\r\n";
    $buf = <$M>;
    if ($buf =~ /^-ERR/) { &Error($buf); }
}

sub mPASS {
    print $M "PASS $passwd\r\n";
    $buf = <$M>;
    if ($buf =~ /^-ERR/) { &Error($buf); }
}

sub mSTAT {
    print $M "STAT\r\n";
    $buf = <$M>;
    $buf =~ /^\+OK\s+(\d+)\s+/i;
    $total = $1;
}

#sub mLIST {
#    if ($total > 0) {
#        print $M "LIST\r\n";
#        $buf = <$M>;
#        if ($buf =~ /^-ERR/) { &Error($buf); }
#
#        while (1) {
#            $buf = <$M>;
#            if ($buf =~ /^\.\s*$/) { last; }
#            $buf =~ /(\d+) (\d+)/;
#            $s{$1} = &mSize($2);
#        }
#    }
#
#    return %s;
#}

sub mTOP {
    my $mNUM = $_[0];
    my ($TMP, $flag, $tmp, $i);
    my ($from, $date, $subject, $charset, $content_type, $priority);
    my (@tmp);

    print $M "TOP $mNUM 0\r\n";
    $buf = <$M>;
    if ($buf =~ /^-ERR/) { &Error($buf); }

    $TMP = <$M>;
    while (1) {
        $buf = <$M>;
        if ($buf =~ /^\.\s*$/) { last; }
        $TMP .= $buf;
    }

    $from = '';
    $subject = '';
    $date = '';
    $priority = '';
    @tmp = split(/\n/, $TMP);

    $charset = '';
    foreach $tmp (@tmp) {
        if ($tmp =~ /^From:\s*(.*)$/i ||
            ($flag eq 'from' && $tmp =~ /^\s(.*)$/)) {
            $from .= " $1";
            $flag = 'from';
        }
        elsif ($tmp =~ /^Subject:\s*(.*)$/i ||
            ($flag eq 'subject' && $tmp =~ /^\s(.*)$/)) {
            $subject .= " $1";
            $flag = 'subject';
            if ($subject =~ /=\?(.*)\?[BQ]+\?.*\?=/i) {
                $charset = $1;
                $charset =~ s/[\r";]//g;
                $flag = '';
            }
        }
        elsif ($tmp =~ /^Content-Type:\s*(.*)$/i ||
            ($flag eq 'type' && $tmp =~ /^\s(.*)$/)) {
            $content_type .= " $1";
            $flag = 'type';
            $content_type =~ s/\s//g;
            if ($content_type =~ /^.*charset=(.*)/i) {
                $charset = $1;
                $charset =~ s/[\r"]//g;
                $charset =~ s/;\s.*$//g;
                $content_type =~ s/;\s.*$//g;
                $flag = '';
            }
        }
        elsif ($tmp =~ /^Date:\s*(.*)$/i) {
            $date = $1;
            $flag = '';
        }
        elsif ($tmp =~ /^X-Priority:\s*(.*)$/i) {
            $i = int($1);
            if ($i == 1) { $priority = '!'; }
            elsif ($i == 2) { $priority = '!'; }
            $flag = '';
        }
        else { $flag = ''; }
    }

    $from = &mDecodeHeader($from);
    $subject = &mDecodeHeader($subject);
    $date = &mFormatDate($date);

    $m{'from'} = $from;
    $m{'subject'} = $subject;
    $m{'date'} = $date;
    $m{'priority'} = $priority;

    foreach $tmp (keys(%m)) {
        $m{$tmp} =  &mEncodeUTF8($charset, $m{$tmp});
        $m{$tmp} =  &mEncodeHTML($m{$tmp});
        $m{$tmp} =~ s/[\n\r]//g;
        $m{$tmp} =~ s/^\s//;
    }
    if ($m{'subject'} eq '') { $m{'subject'} = $l{'subject_unspecified'}; }

    return %m;
}

sub mRETR {
    my ($mNUM, $mMIMEPART) = @_;
    my ($TMP, $tmp, $i, $j);
    my ($flag, $flag_mimepart);
    my ($from, $to, $cc, $subject, $date, $body);
    my ($headers, $charset, $boundary);
    my ($content_type, $content_encoding);
    my ($part, $part_name, $part_type, $part_body, $part_size);
    my ($part_charset, $part_boundary, $part_encoding);
    my ($part_disposition, $part_content_id);
    my ($attachment_count, $bgcolor, $background);
    my (@tmp, @part, @mimepart);

    print $M "RETR $mNUM\r\n";
    $buf = <$M>;
    if ($buf =~ /^-ERR/) { &Error($buf); }

    $TMP = <$M>;
    while (1) {
        $buf = <$M>;
        if ($buf =~ /^\.\s*$/) { last; }
        $TMP .= $buf;
    }

    $flag_mimepart = 0;
    @mimepart = split(/\./, $mMIMEPART);
    @mimepart = splice(@mimepart, 1, $#mimepart);

    while (1) {
        $headers = $TMP;
        @tmp = split(/\n/, $TMP);

        $TMP = '';
        $flag = '';

        $from = '';
        $to = '';
        $cc = '';
        $subject = '';
        $charset = '';
        $date = '';
        $body = '';
        $content_type = '';

        foreach $tmp (@tmp) {
            if ($tmp eq "\r") { $flag = 'body'; }

            if ($flag ne 'body') {
                if ($tmp =~ /^From:\s*(.*)$/i ||
                    ($flag eq 'from' && $tmp =~ /^\s(.*)$/)) {
                    $from .= " $1";
                    $flag = 'from';
                }
                elsif ($tmp =~ /^To:\s*(.*)$/i ||
                    ($flag eq 'to' && $tmp =~ /^\s(.*)$/)) {
                    $to .= " $1";
                    $flag = 'to';
                }
                elsif ($tmp =~ /^CC:\s*(.*)$/i ||
                    ($flag eq 'cc' && $tmp =~ /^\s(.*)$/)) {
                    $cc .= " $1";
                    $flag = 'cc';
                }
                elsif ($tmp =~ /^Date:\s*(.*)$/i) {
                    $date = $1;
                    $flag = '';
                }
                elsif ($tmp =~ /^Subject:\s*(.*)$/i ||
                    ($flag eq 'subject' && $tmp =~ /^\s(.*)$/)) {
                    $subject .= " $1";
                    $flag = 'subject';
                    if ($subject =~ /=\?(.*)\?[BQ]+\?.*\?=/i) {
                        $charset = $1;
                        $charset =~ s/[\r";]//g;
                        $flag = '';
                    }
                }
                elsif ($tmp =~ /^Content-Type:\s*(.*)$/i ||
                    ($flag eq 'type' && $tmp =~ /^\s(.*)$/)) {
                    $content_type .= " $1";
                    $flag = 'type';
                    $content_type =~ s/\s//g;
                    if ($content_type =~ /^.*charset=(.*)/i) {
                        $charset = $1;
                        $charset =~ s/[\r"]//g;
                        $charset =~ s/;\s.*$//g;
                        $content_type =~ s/;\s.*$//g;
                        $flag = '';
                    }
                    elsif ($content_type =~ /^.*boundary=(.*)/i) {
                        $boundary = $1;
                        $boundary =~ s/[\r";]//g;
                        $content_type =~ s/;\s.*$//g;
                        $flag = '';
                    }
                }
                elsif ($tmp =~ /^Content-Transfer-Encoding:\s(.*)$/i) {
                    $content_encoding = $1;
                }
                else { $flag = ''; }
            }
            else { $TMP .= "$tmp\n"; }
        }

        $from = &mDecodeHeader($from);
        $to = &mDecodeHeader($to);
        $cc = &mDecodeHeader($cc);
        $subject = &mDecodeHeader($subject);
        $date = &mFormatDate($date);

        if ($content_type eq '') { $content_type = 'text/plain'; }

        $i = 0;
        if ($content_type =~ /text\/plain/i ||
            $content_type =~ /text\/html/i) {
            $body = &mDecodeBody($content_encoding, $TMP);
        }
        elsif ($content_type =~ /multipart\//i) {
            @tmp = split(/\n/, $TMP);
            $TMP = '';
            $j = 0;
            $#part = -1;

            # We don't use split here. Sometimes, Boundary and
            # alternavtie boundary are almost identical.
            foreach $tmp (@tmp) {
                if ($tmp eq "--$boundary--\r") { last; }
                elsif ($tmp eq "--$boundary\r") { $j++; }
                else { $part[$j] .= "$tmp\n"; }
            }
            @part = splice(@part, 1, $#part);

            foreach $part (@part) {
                $TMP = '';
                $flag = '';
                $part_name = '';
                $part_type = '';
                $part_body = '';
                $part_size = '';
                $part_charset = '';
                $part_boundary = '';
                $part_encoding = '';
                $part_disposition = '';
                $part_content_id = '';

                if ($part =~ /^\r\n/) { $part =~ s/\r\n//; }
                @tmp = split(/\n/, $part);
                foreach $tmp (@tmp) {
                    if ($tmp eq "\r") { $flag = 'body'; }

                    if ($flag ne 'body') {
                        if ($tmp =~ /^Content-Type:\s*(.*)$/i ||
                            ($flag eq 'type' && $tmp =~ /^\s(.*)$/)) {
                            $part_type .= " $1";
                            $flag = 'type';
                            $part_type =~ s/\s//g;
                            if ($part_type =~ /^.*charset=(.*)/i) {
                                $part_charset = $1;
                                $part_charset =~ s/[\r"]//g;
                                $part_charset =~ s/;\s.*$//g;
                                $part_type =~ s/;\s.*$//g;
                                $flag = '';
                            }
                            elsif ($part_type =~ /^.*boundary=(.*)/i) {
                                $part_boundary = $1;
                                $part_boundary =~ s/[\r";]//g;
                                $part_type =~ s/;\s.*$//g;
                                $flag = '';
                            }
                            elsif ($part_type =~ /^.*name=(.*)/i) {
                                $part_name = $1;
                                $part_name =~ s/[\r";]//g;
                                $part_type =~ s/;\s.*$//g;
                                $flag = '';
                            }
                        }
                        elsif ($tmp =~ /^Content-Transfer-Encoding:\s(.*)$/i) {
                            $part_encoding = $1;
                        }
                        elsif ($tmp =~ /^Content-Disposition:\s*(.*)$/i ||
                            ($flag eq 'disposition' &&
                            $tmp =~ /^\s(.*)$/)) {
                            $part_disposition .= " $1";
                            $flag = 'disposition';
                            $part_disposition =~ s/\s//g;
                            if ($part_disposition =~ /.*name=(.*)/i) {
                                $part_name = $1;
                                $part_name =~ s/[\r";]//g;
                                $flag = '';
                            }
                        }
                        elsif ($tmp =~ /^Content-ID:\s*(.*)$/i) {
                            $part_content_id = $1;
                            if ($part_content_id =~ /<(.*)>/) {
                                $part_content_id = $1;
                            }
                        }
                    }
                    else { $TMP .= "$tmp\n"; }
                }

                if ($part_type eq '') { $part_type = 'text/plain'; }

                if ($part_charset eq '') {
                    $part_charset = $charset;
                }
                else {
                    $charset = $part_charset;
                }

                if ($TMP =~ /^\r\n/) { $TMP =~ s/\r\n//; }
                if ($part_name eq '') {
                    if ($part_type =~ /text\/plain/i ||
                        $part_type =~ /text\/html/i) {
                        $part_body = &mDecodeBody($part_encoding, $TMP);
                        if (length($body) < length($part_body)) {
                            $body = $part_body;
                            $content_type = $part_type;
                        }
                    }
                    elsif ($part_type =~ /multipart\//i) {
                        @tmp = split(/\n/, $TMP);
                        $TMP = '';
                        foreach $tmp (@tmp) {
                            if ($tmp eq "--$part_boundary--\r") { last; }
                            elsif ($tmp eq "--$part_boundary\r") { $j++; }
                            else { $part[$j] .= "$tmp\n"; }
                        }
                    }
                    elsif ($part_type =~ /message\/rfc822/i) {
                        @tmp = split(/\n/, $TMP);
                        $flag = '';
                        foreach $tmp (@tmp) {
                            if ($tmp eq "\r") { last; }

                            if ($tmp =~ /^Subject:\s*(.*)$/i ||
                                ($flag eq 'subject' && $tmp =~ /^\s(.*)$/)) {
                                $part_name .= " $1";
                                $flag = 'subject';
                                if ($part_name =~ /=\?(.*)\?[BQ]\?.*\?=/i) {
                                    $part_charset = $1;
                                    $part_charset =~ s/[\r";]//g;
                                    $flag = '';
                                }
                            }
                            elsif ($tmp =~ /^Content-Type:\s*(.*)$/i ||
                                ($flag eq 'type' && $tmp =~ /^\s(.*)$/)) {
                                $part_type .= " $1";
                                $flag = 'type';
                                $part_type =~ s/\s//g;
                                if ($part_type =~ /^.*charset=(.*)/i) {
                                    $part_charset = $1;
                                    $part_charset =~ s/[\r"]//g;
                                    $part_charset =~ s/;\s.*$//g;
                                    $part_type =~ s/;\s.*$//g;
                                    $flag = '';
                                }
                            }
                            else { $flag = ''; }
                        }

                        $part_name = &mDecodeHeader($part_name);
                        $part_name = &mEncodeUTF8($part_charset, $part_name);
                        $part_name = &mEncodeHTML($part_name);
                        if ($part_name eq '') {
                            $part_name = $l{'subject_unspecified'};
                        }

                        $m{'attachment'}->[$i]->{'name'} = $part_name;
                        $m{'attachment'}->[$i]->{'type'} = 'message/rfc822';
                        $m{'attachment'}->[$i]->{'body'} = $TMP;
                        $m{'attachment'}->[$i]->{'size'} = length($TMP);
                        $m{'attachment'}->[$i]->{'encoding'} = $part_encoding;
                        $m{'attachment'}->[$i]->{'content_id'} = '';
                        $i++;
                    }
                }
                else {
                    $part_name = &mDecodeHeader($part_name);
                    $part_name = &mEncodeUTF8($part_charset, $part_name);
                    $part_body = &mDecodeBody($part_encoding, $TMP);
                    $part_size = length($part_body);
                    if ($part_name eq '') {
                        $part_name = $l{'name_unspecified'};
                    }

                    $m{'attachment'}->[$i]->{'name'} = $part_name;
                    $m{'attachment'}->[$i]->{'type'} = $part_type;
                    $m{'attachment'}->[$i]->{'body'} = $part_body;
                    $m{'attachment'}->[$i]->{'size'} = $part_size;
                    $m{'attachment'}->[$i]->{'encoding'} = $part_encoding;
                    $m{'attachment'}->[$i]->{'content_id'} = $part_content_id;
                    $i++;
                }
            }
        }

        if ($flag_mimepart <= $#mimepart) {
            $TMP = $m{'attachment'}->[$mimepart[$flag_mimepart]]->{'body'};
            $flag_mimepart++;
        }
        else { last; }
    }

    $attachment_count = $i;

    $bgcolor = '#ffffff';
    if ($content_type =~ /text\/html/i) {
        $body =~ s/=["']+mailto:([A-Za-z0-9-_\.]+@[A-Za-z0-9-_\.]+)["']+/='$script\?mode=form&amp;type=compose&amp;to=$1'/gi;
        $body =~ s/=["']+$script\?mode=form&amp;type=compose&amp;to=(.*)\?subject=(.*)["']+/='$script\?mode=form&amp;type=compose&amp;to=$1&amp;subject=$2'/gi;

        $background = '';
        for ($i = 0; $i < $attachment_count; $i++) {
            $part_content_id = $m{'attachment'}->[$i]->{'content_id'};

            if ($part_content_id ne '') {
                $part_name =  $m{'attachment'}->[$i]->{'name'};
                $part_name =~ s/ /%20/g;
                $part_name =  "$script?mode=download&amp;num=$mNUM&amp;mimepart=$mMIMEPART&amp;time=$time&amp;attachment=$i/" . $part_name;

                if ($body =~ /<body(?:.|\n)*background=["']?cid:$part_content_id/i) {
                    $background = $part_name;
                    $body =~ s/background=["']?cid:$part_content_id//g;
                }
                $body =~ s/cid:$part_content_id/$part_name/g;
            }
        }

        if ($body =~ /<body[.\n]*bgcolor=["']*([#A-Za-z0-9]+)[\s"'>]*/i) {
            $bgcolor = $1;
        }

        $body =~ s/<\/?(base|html|head|meta|link|body)[^>]*>//gi;
    }
    else {
        $body =  &mEncodeHTML($body);
        $body =~ s/\r?\n/<br>\r\n/g;
    }

    $body =~ s/(?:<|&lt;)([A-Za-z0-9-\._]+@[A-Za-z0-9-\.]+)(?:>|&gt;)/&lt;<a href='$script\?mode=form&amp;type=compose&amp;to=$1'>$1<\/a>&gt;/gi;
    #$body =~ s/(?:[^"'=])((?:http|https|ftp)+:\/\/[A-Za-z0-9-\.\/:]+[A-Za-z0-9#%&\+-\.\/:;\?=@]+)/<a href='$1' target='_blank'>$1<\/a>/gi;

    $body =~ s/<script/<noscript/gi;
    $body =~ s/<\/script>/<\/noscript>/gi;
    $body =~ s/<title/<\!--title/gi;
    $body =~ s/<\/title>/<\/title-->/gi;
    $body =~ s/<style/<\!--style/gi;
    $body =~ s/<\/style>/<\/style-->/gi;
    $body =~ s/document\.cookie/document_cookie/g;

    $m{'from'} = &mEncodeUTF8($charset, $from);
    $m{'to'} = &mEncodeUTF8($charset, $to);
    $m{'cc'} = &mEncodeUTF8($charset, $cc);
    $m{'subject'} = &mEncodeUTF8($charset, $subject);
    $m{'date'} = $date;
    $m{'body'} = &mEncodeUTF8($charset, $body);
    $m{'headers'} = &mEncodeUTF8($charset, $headers);
    $m{'bgcolor'} = $bgcolor;
    $m{'background'} = $background;
    $m{'attachment_count'} = $attachment_count;

    if ($m{'subject'} eq '') { $m{'subject'} = $l{'subject_unspecified'}; }

    foreach $tmp (keys(%m)) {
        if ($tmp =~ /(?:from|to|cc|date|subject)/) {
            $m{$tmp} =  &mEncodeHTML($m{$tmp});
            $m{$tmp} =~ s/[\n\r]//g;
            $m{$tmp} =~ s/^\s//;
        }
    }

    return %m;
}

sub mDELE {
    my $mNUM = $_[0];

    print $M "DELE $mNUM\r\n";
    $buf = <$M>;
    if ($buf =~ /^-ERR/) { &Error($buf); }
}

sub mQUIT {
    print $M "QUIT\r\n";
    $buf = <$M>;
    if ($buf =~ /^-ERR/) { &Error($buf); }

    close($M);
}

sub mDecodeHeader {
    my $str = $_[0];
    my ($tmp);
    my (@tmp);

    if ($str =~ /=\?(.*)\?[BQ]\?(.*)\?=/i) {
        @tmp = split(/\s/, $str);
        $str = '';

        foreach $tmp (@tmp) {
            if ($tmp =~ /=\?.*\?B\?(.*)\?=/i) {
                $str .= &mDecodeBase64($1);
            }
            elsif ($tmp =~ /=\?.*\?Q\?(.*)\?=/i) {
                $str .=  &mDecodeQuotedPrintable($1);
            }
            else { $str .= " $tmp"; }
        }
    }

    return $str;
}

sub mDecodeBody {
    my ($encoding, $str) = @_;

    if ($encoding =~ /base64/i) {
        return &mDecodeBase64($str);
    }
    elsif ($encoding =~ /quoted-printable/i) {
        return &mDecodeQuotedPrintable($str);
    }
    return $str;
}

sub mEncodeBase64 {
    my $str1 = $_[0];
    my ($str2, $padding);

    while ($str1 =~ /(.{1,45})/gs) {
        $str2 .= substr(pack('u', $1), 1);
        chop($str2);
    }
    $str2 =~ tr/` -_/AA-Za-z0-9+\//;

    $padding = (3 - length($str1) % 3) % 3;
    if ($padding) { $str2 =~ s/.{$padding}$/'=' x $padding/e; }
    $str2 =~ s/(.{1,76})/$1\r\n/g;

    return $str2;
}

sub mDecodeBase64 {
    my $str1 = $_[0];
    my ($str2, $tmp, $i);

    for ($i = 0; $i < (length($str1) % 4); $i++) { chop($str1); }
    $str1 =~ tr/A-Za-z0-9+=\///cd;
    $str1 =~ s/=+$//;
    $str1 =~ tr/A-Za-z0-9+\// -_/;
    while ($str1 =~ /(.{1,60})/gs) {
        $tmp = chr(32 + length($1) * 3 / 4);
        $str2 .= unpack("u", $tmp . $1 );
    }

    return $str2;
}

sub mDecodeQuotedPrintable {
    my $str1 = $_[0];
    my ($str2);

    $str1 =~ s/\s+(\r?\n)/$1/g;
    $str1 =~ s/=\r?\n//g;
    $str2 = $str1;
    $str2 =~ s/=([\da-fA-F]{2})/pack('C', hex($1))/ge;

    return $str2;
}

sub mEncodeUTF8 {
    my ($charset, $str) = @_;

    if ($charset ne '' && $charset ne 'utf-8') {
        return encode('utf-8', decode($charset, $str));
    }
    return $str;
}

sub mEncodeHTML {
    my $str = $_[0];
    $str =~ s/</&lt;/g;
    $str =~ s/>/&gt;/g;
    return $str;
}

#sub mDecodeHTML {
#    my $str = $_[0];
#    $str =~ s/&lt;/</gi;
#    $str =~ s/&gt;/>/gi;
#    return $str;
#}

sub mGetDate {
    my %months = (
        '01', 'Jan',
        '02', 'Feb',
        '03', 'Mar',
        '04', 'Apr',
        '05', 'May',
        '06', 'Jun',
        '07', 'Jul',
        '08', 'Aug',
        '09', 'Sep',
        '10', 'Oct',
        '11', 'Nov',
        '12', 'Dec',
    );
    my @weeks = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');
    my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday) = localtime();

    $year += 1900;
    $mon  += 1;
    if ($mon  < 10) { $mon  = "0$mon";  }
    if ($mday < 10) { $mday = "0$mday"; }
    if ($hour < 10) { $hour = "0$hour"; }
    if ($min  < 10) { $min  = "0$min";  }
    if ($sec  < 10) { $sec  = "0$sec";  }

    return "$weeks[$wday], $mday $months{$mon} $year $hour:$min:$sec" .
        " $TIMEZONE";
}

sub mFormatDate {
    my $time = $_[0];
    my ($day, $month, $year, $hour_min, $gmt_interval);
    my %months = (
        'Jan', '01',
        'Feb', '02',
        'Mar', '03',
        'Apr', '04',
        'May', '05',
        'Jun', '06',
        'Jul', '07',
        'Aug', '08',
        'Sep', '09',
        'Oct', '10',
        'Nov', '11',
        'Dec', '12',
    );

    if ($time eq '') { return ''; }
    if ($time =~ /\,\s+/) { $time =~ s/.*\,\s+//; }
    ($day, $month, $year, $hour_min, $gmt_interval) = split(/\ /, $time);
    if ($day < 10) { $day = '0' . int($day); }

    return "$year-$months{$month}-$day $hour_min $gmt_interval";
}

sub mSize {
    my $size = $_[0];

    if ($size >= 1048576) { return int($size / 1048576) . 'M'; }
    elsif ($size >= 1024) { return int($size / 1024) . 'K';    }
    else { return '1K'; }
}

sub mLocale {
    if ($LOCALE eq 'ko') {
        $l{'login_title'} = '로그인';

        $l{'userid'} = '아이디';
        $l{'passwd'} = '비밀번호';
        $l{'pop3_server'} = '받는 메일서버';

        $l{'logout'} = '로그아웃';
        $l{'compose'} = '편지쓰기';
        $l{'reply'} = '회신';
        $l{'reply_all'} = '전체회신';
        $l{'forward'} = '전달';
        $l{'forward_attach'} = '첨부하여 전달';
        $l{'headers'} = '원본';
        $l{'delete'} = '삭제';

        $l{'total'} = '메시지';
        $l{'page'} = '페이지';
        $l{'no'} = '번호';
        $l{'from'} = '보낸 사람';
        $l{'to'} = '받은 사람';
        $l{'sender'} = '보내는 사람';
        $l{'receiver'} = '받는 사람';
        $l{'cc'} = '참조';
        $l{'bcc'} = '숨은참조';
        $l{'date'} = '날짜';
        $l{'subject'} = '제목';
        $l{'smtp_server'} = '보내는 메일서버';
        $l{'attachment'} = '첨부파일';
        $l{'original_message'} = '원본 메시지';
        $l{'original_message_included'} = '원본 메시지가 첨부되었습니다.';

        $l{'reload'} = '새로고침';
        $l{'prev'} = '이전';
        $l{'next'} = '다음';
        $l{'list'} = '목록';

        $l{'login_submit'} = '로그인';
        $l{'delete_submit'} = '선택한 메일 삭제';
        $l{'send_submit'} = '   보내기   ';
        $l{'cancel'} = '취소';

        $l{'userid_error'} = '아이디가 필요합니다.';
        $l{'passwd_error'} = '비밀번호가 필요합니다.';
        $l{'pop3_server_error'} = '받는 메일서버가 필요합니다.';
        $l{'from_error'} = '보내는 사람의 이메일이 필요합니다.';
        $l{'to_error'} = '받는 사람이 필요합니다.';
        $l{'smtp_server_error'} = '보내는 메일서버가 필요합니다.';
        $l{'body_error'} = '내용이 필요합니다.';
        $l{'connect_error'} = '서버에 접속할 수 없습니다.';

        $l{'name_unspecified'} = '이름없음';
        $l{'subject_unspecified'} = '제목없음';
    }
    elsif ($LOCALE eq 'en') {
        $l{'login_title'} = 'Login';

        $l{'userid'} = 'UserID';
        $l{'passwd'} = 'Passwd';
        $l{'pop3_server'} = 'POP3 Server';

        $l{'logout'} = 'Logout';
        $l{'compose'} = 'Compose';
        $l{'reply'} = 'Reply';
        $l{'reply_all'} = 'Reply All';
        $l{'forward'} = 'Forward';
        $l{'forward_attach'} = 'Forward As Attachment';
        $l{'headers'} = 'Headers';
        $l{'delete'} = 'Delete';

        $l{'total'} = 'Total';
        $l{'page'} = 'Page';
        $l{'no'} = 'No.';
        $l{'from'} = 'From';
        $l{'to'} = 'To';
        $l{'sender'} = 'From';
        $l{'receiver'} = 'To';
        $l{'cc'} = 'CC';
        $l{'bcc'} = 'BCC';
        $l{'date'} = 'Date';
        $l{'subject'} = 'Subject';
        $l{'smtp_server'} = 'SMTP Server';
        $l{'attachment'} = 'Attachment';
        $l{'original_message'} = 'Original Message';
        $l{'original_message_included'} = 'Original Message Included.';

        $l{'reload'} = 'Reload';
        $l{'prev'} = 'Prev';
        $l{'next'} = 'Next';
        $l{'list'} = 'List';

        $l{'login_submit'} = 'Login';
        $l{'delete_submit'} = 'Delete Marked';
        $l{'send_submit'} = '    Send    ';
        $l{'cancel'} = 'Cancel';

        $l{'userid_error'} = 'UserID Must Be Specified.';
        $l{'passwd_error'} = 'Passwd Must Be Specified.';
        $l{'pop3_server_error'} = 'POP3 Server Must Be Specified.';
        $l{'from_error'} = 'From Must Be Specified.';
        $l{'to_error'} = 'To Must Be Specified.';
        $l{'smtp_server_error'} = 'SMTP Server Must Be Specified.';
        $l{'body_error'} = 'Body Must Be Specified.';
        $l{'connect_error'} = 'Could NOT Connect To Server.';

        $l{'name_unspecified'} = 'Unspecified';
        $l{'subject_unspecified'} = 'Unspecified';
    }

    return %l;
}
