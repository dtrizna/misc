#!/usr/bin/env python

import subprocess
import time

# This script will calculate received UDP parcket error rate
# versus all the UDP packets this host receives (as percents)

# Almost all the UDP errors appears due to Logstash performance limitations

delay = raw_input('Please specify how long to collect statistics?\n(Note: This long will take for scipt to execute.)\nPress "Enter" for [60]: ')

if len(delay) == 0:
        delay = 60
else:
        delay = int(delay)

stats1 = subprocess.check_output(["netstat", "-su"]).split()

time.sleep(delay)

stats2 = subprocess.check_output(["netstat", "-su"]).split()

PKT_ST = int(stats1[8])
ERR_ST = int(stats1[17])

PKT_END = int(stats2[8])
ERR_END = int(stats2[17])

PKTS = PKT_END - PKT_ST
ERRS = ERR_END - ERR_ST

date = time.strftime("%H:%M %d/%m/%Y")

line = range(6)
line[0] = "----------- Statistics collected at: {}".format(date)
line[1] = "\n\nStatistics for last {} seconds:\n\tPackets received: {}".format(delay,PKTS)
line[2] = "\n\tPackets per second: {}\n\tApproximate amount of Netflow records:".format(  PKTS / delay )
line[3] = "\n\t\t\t\t\tper second: {},\n\t\t\t\t\tper minute: {}".format( PKTS * 27 / delay, PKTS * 27 * 60 / delay)
line[4] = "\n\tPacket receive Errors: {}".format(ERRS)
line[5] = "\n\tError percentage: {}%\n\n\n".format( ERRS * 100 / (PKTS + ERRS) )

logdate = time.strftime("%m.%d.%Y")

with open('/var/log/udp_error_log/udp_error.log-{}'.format(logdate),'a') as file:
        file.writelines(line)
