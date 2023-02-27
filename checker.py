import requests
import urllib3
import tqdm
import os


from bs4 import BeautifulSoup as bs
from multiprocessing import Pool


requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'

HEADERS = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) snap Chromium/83.0.4103.61 Chrome/83.0.4103.61 Safari/537.36"
        }
LOGIN = os.environ.get("UBT_LOG")
PASSWORD = os.environ.get("UBT_PASS")

class ubt_ne():
    def __init__(self, ip):
        self.ip = f"https://{ip}"
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def get(self, req = ""):
        # print(f"get --- {self.ip}/{req}")
        response = self.session.get(f"{self.ip}/{req}", verify=False, timeout=10)
        return response
    
    def post(self, req = "", data = ""):
        # print(f"post --- {self.ip}/{req}")
        response = self.session.post(f"{self.ip}/{req}", data=data, verify=False, timeout=10)
        return  response
        
    def auth(self):
        try:
            response = self.get()
            response = self.get("login?link_to=%2F")
            payload = {
                "fakeusernameremembered": "",
                "fakepasswordremembered": "",
                "link_to" : "/",
                "in-log-it-login": LOGIN,
                "in-log-it-pwd": PASSWORD,
                "in-log-ib-signin": "Sign-In",
            }
            self.session.headers.update({"Connection": "keep-alive"})
            response = self.post(data=payload, req="login")
            response = self.get(req="consensus_banner")
            payload = {
                "link_to": "/",
                "in-cob-ib-accept": "Accept",
            }
            self.post(req="consensus_banner", data=payload)
            return response
        except:
            raise ConnectionError
    
    def get_licence_info(self):
        try:
            response = self.get("admin_net/license_info")
            soup = bs(response.text, "lxml")
            license_string = soup.findAll("textarea", {"class" : "license-textarea"})[1].text.strip()
            return license_string
        except:
            return "Didn't read status"
  

def writeToFile(line):
    ip = line.split(",")[0].strip()
    license = license_status(ip)
    with open('out.csv', 'a', encoding='UTF-8') as outfile:
        outfile.write(f'{line.strip()},{license}\n')      


def license_status(ip):
    try:
        ne = ubt_ne(ip)
        ne.auth()
        license_string = ne.get_licence_info()
        return license_string
    except ConnectionError:
        return "ConnectionError"


if __name__ == "__main__":
    with open('ip.csv', 'r', encoding='UTF-8') as infile:
        lines = infile.readlines()
        
    with open('out.csv', 'w', encoding='UTF-8') as outfile:
        outfile.write(f'{lines[0].strip()},License\n')

    pool = Pool(processes=50)
    for _ in tqdm.tqdm(pool.imap_unordered(writeToFile, lines[1:]), total=len(lines)):
        pass
    
