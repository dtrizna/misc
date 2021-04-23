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

stats1 = subprocess.check_output(["netstat", "-su"]).split('\n')

time.sleep(delay)

stats2 = subprocess.check_output(["netstat", "-su"]).split('\n')

# PARSING netstat -su output;
# It changes from time to time, so I need to search for pattern in output
# and take a specific field on that line

try:

        # ONELINED FOR AND IF, please refer to documentation in OneNote

        # statsX is a list with every element as line on netstat -su output
        # this expression filters element in list that contains string in if clause
        # and takes only first word of it (actually the numeric value)

        PKT_ST = int([ s for s in stats1 if 'packets received' in s ][0].split()[0])
        PKT_END = int([ s for s in stats2 if 'packets received' in s ][0].split()[0])

        ERR_ST = int([ s for s in stats1 if 'packet receive errors' in s ][0].split()[0])
        ERR_END = int([ s for s in stats2 if 'packet receive errors' in s ][0].split()[0])

        # ---------------------------

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


except:
        line = 'Error in "netstat -su" handling.'


logdate = time.strftime("%m.%d.%Y")

with open('/var/log/udp_error_log/udp_error.log-{}'.format(logdate),'a') as file:
        file.writelines(line)
