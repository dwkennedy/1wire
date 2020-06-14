#!/usr/bin/python

# test calling sendmail to deliver message
# postfix should be configured to forward mail to smarthost

from subprocess import Popen, PIPE

sender_email = "Your Fridge <root@fridge.kennedygang.com>"
receiver_email = "doug@kennedygang.com"

text = """\
From: {}
To: {}
Subject: test message

Hi,
How are you?
Real Python has many great tutorials:
www.realpython.com"""

proc = Popen(['/usr/sbin/sendmail','-t','-oi'], stdin=PIPE)

print ("called process")
proc.communicate(text.format(sender_email,receiver_email).encode('utf8')) 
print ("sent text")
proc.wait()


