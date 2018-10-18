from netmiko import cisco
from collections import deque
import re
import sys
import getpass
import time

user = input("Please enter username: ")
passw = getpass.getpass("Enter password: ")

ASA_1 = {'device_type': 'cisco_asa', 'ip': '10.1.1.1', 'username': user, 'password': passw}
ASA_2 = {'device_type': 'cisco_asa', 'ip': '10.1.1.2', 'username': user, 'password': passw}

delay = 300
debug = False

#======================
# FUNCTIONS
#======================

# Connection handling with graceful cleanup if error
def connect(device):
        try:
                if debug:
                        print(' [*] Connecting to {}...'.format(device['ip']))
                conn = cisco.CiscoAsaSSH(**device)
                if debug:
                        print('[!] Connection successful! ')
        except Exception as e:
                print(" [-] Error during connection: {}".format(e))
                sys.exit(1)

        if conn.find_prompt():
                pass
        else:
                print("Error during connection to {}".format(str(device['ip'])))
                conn.cleanup()
                sys.exit(1)

        return conn

# Byte parsing logics
def parse_bytes(current_bpm, previous_bpm):

        bpm = current_bpm - previous_bpm
        bps = int(bpm/delay)

        if len(str(bps)) > 6:
                data = '{} Mbps'.format(bps/1000000)
        if len(str(bps)) > 3:
                data = '{} Kbps'.format(bps/1000)
        else:
                data = '{} bps'.format(bps)

        return bps,data

#=======================

session_list = []
session_list.append(connect(ASA_2))
session_list.append(connect(ASA_1))

try:

        # Creating an object for data storage
        stats = dict()
        for session in session_list:
                stats[session.ip] = dict()
                # Queue objects in both directions
                stats[session.ip]['input'] = deque()
                stats[session.ip]['output'] = deque()

        # Iterate for statistics retrieval until error or is killed/stopped
        while True:

                for session in session_list:

                        if debug:
                                print(' [*] Fetching interface statistics on {}... '.format(session.ip))

                        # For now fetch data only on 'outside' interface
                        sh_int = session.send_command('sh int outside')

                        # Search for line: "923474754 packets input, 65226059671 bytes", leave only bytes integer, add to storage
                        input_bytes = int(re.search('input,.*bytes', sh_int).group().replace('input, ','').replace(' bytes',''))
                        stats[session.ip]['input'].append(input_bytes)

                        # Search for line: "923474754 packets output, 65226059671 bytes", leave only bytes integer, add to storage
                        output_bytes = int(re.search('output,.*bytes', sh_int).group().replace('output, ','').replace(' bytes',''))
                        stats[session.ip]['output'].append(output_bytes)

                        # Calculate values only if storage is ready
                        if len(stats[session.ip]['output']) == 1 and len(stats[session.ip]['input']) == 1:
                                if debug:
                                        print(' [*] Too few data. Waiting for next iteration...')
                                continue

                        # Queue object has to have only 2 entries - previous and current
                        elif len(stats[session.ip]['output']) == 2 and len(stats[session.ip]['input']) == 2:
                                if debug:
                                        print(' [*] Calulating data...')

                                # CALCULATE stats

                                # Here previous is deleted (pop) from storage:
                                last_input_bytes = stats[session.ip]['input'].popleft()
                                in_raw,input_data = parse_bytes(input_bytes,last_input_bytes)

                                # Here previous is deleted (pop) from storage:
                                last_output_bytes = stats[session.ip]['output'].popleft()
                                out_raw,output_data = parse_bytes(output_bytes,last_output_bytes)

                                write = '''
Data collected for last {} seconds at {}
        Outside interface statistics for input: {}
        Outside interface statistics for output: {}
'''.format(delay, time.strftime('%H:%M %d.%m.%Y'),input_data,output_data)

                                raw_write = '{} {} {}\n'.format(time.strftime('%H:%M %d.%m.%Y'),in_raw,out_raw)

                        else:
                                print("[-] Something went wrong - 'stats' objects not as planned:")
                                print(stats)
                                print('[!] Exiting...')
                                for session in session_list:
                                        session.cleanup()
                                sys.exit(1)


                        if debug:
                                print(' [*] Traffic data:\n{}'.format(write))
                                print('[!] Writing to a file..')

                        # Append data to files
                        with open(r'/root/scripts/ASA_STATS/formatted_{}_{}'.format(session.ip,time.strftime('%d.%m.%Y')),'a') as file:
                                file.writelines(write)
                        with open(r'/root/scripts/ASA_STATS/raw_{}_{}'.format(session.ip,time.strftime('%d.%m.%Y')),'a') as file:
                                file.writelines(raw_write)

                write = 'Misc... Something wrong...' # To reset variable and detect if it's not rewritten.
                raw_write = 'Misc... Something wrong...' # To reset variable and detect if it's not rewritten.
                if debug:
                        print(' [*] Sleep for {} seconds'.format(delay))
                time.sleep(delay)


except KeyboardInterrupt:
        print("[!] Keyboard exception.\n[!] Cleaning out...")
        for session in session_list:
                session.cleanup()
        sys.exit(1)

except Exception as e:
        print("[!] Unplanned exception: {} \n [!] Cleaning out...".format(e))
        for session in session_list:
                session.cleanup()
        sys.exit(1)
