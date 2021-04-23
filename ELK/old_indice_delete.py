#!/usr/bin/env python

import subprocess, time, datetime

today = datetime.date.today()
remove_date = today - datetime.timedelta(days=90)
date =  remove_date.strftime("%Y %m %d").split()

cmd = "curl -XDELETE http://localhost:9200/netflow-{}.{}.{}*".format(date[0], date[1], date[2])

print "\nCommand that will be sent to ES:\n {}".format(cmd)

call = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(output, error) = call.communicate()

print "\n\nOutput is:\n {}".format(output)
print "\nError is : (if there's statistics about connection - it is OK!)\n {}".format(error)
