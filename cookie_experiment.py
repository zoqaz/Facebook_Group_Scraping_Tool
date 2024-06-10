from requests.cookies import RequestsCookieJar
import json
import time

# def is_logged_in(self) -> bool:
#         try:
#             self.get('https://facebook.com/settings')
#             return True
#         except:
#             return False

# def parse_cookie_file(filename: str) -> RequestsCookieJar:
#     jar = RequestsCookieJar()

#     with open(filename, mode='rt') as file:
#         data = file.read()

#     try:
#         data = json.loads(data)
#         if type(data) is list:
#             for c in data:
#                 expires = c.get("expirationDate") or c.get("Expires raw")
#                 if expires:
#                     expires = int(expires)
#                 if "Name raw" in c:
#                     # Cookie Quick Manager JSON format
#                     host = c["Host raw"].replace("https://", "").strip("/")
#                     jar.set(
#                         c["Name raw"],
#                         c["Content raw"],
#                         domain=host,
#                         path=c["Path raw"],
#                         expires=expires,
#                     )
#                 else:
#                     # EditThisCookie JSON format
#                     jar.set(
#                         c["name"],
#                         c["value"],
#                         domain=c["domain"],
#                         path=c["path"],
#                         secure=c["secure"],
#                         expires=expires,
#                     )
#         elif type(data) is dict:
#             for k, v in data.items():
#                 if type(v) is dict:
#                     jar.set(k, v["value"])
#                 else:
#                     jar.set(k, v)
#     except json.decoder.JSONDecodeError:
#         # Netscape format
#         for i, line in enumerate(data.splitlines()):
#             line = line.strip()
#             if line == "" or line.startswith('#'):
#                 continue

#             try:
#                 domain, _, path, secure, expires, name, value = line.split('\t')
#             except Exception as e:
#                 raise exceptions.InvalidCookies(f"Can't parse line {i + 1}: '{line}'")
#             secure = secure.lower() == 'true'
#             expires = None if expires == '0' else int(expires)

#             jar.set(name, value, domain=domain, path=path, secure=secure, expires=expires)

#     return jar

# def set_cookies(cookies):
#     if isinstance(cookies, str):
#         if cookies == "from_browser":
#             try:
#                 import browser_cookie3

#                 cookies = browser_cookie3.load(domain_name='.facebook.com')
#             except:
#                 raise ModuleNotFoundError(
#                     "browser_cookie3 must be installed to use browser cookies"
#                 )
#         else:
#             try:
#                 cookies = parse_cookie_file(cookies)
#             except ValueError as e:
#                 raise exceptions.InvalidCookies(f"Cookies are in an invalid format: {e}")
#     elif isinstance(cookies, dict):
#         cookies = cookiejar_from_dict(cookies)
#     if cookies is not None:
#         cookie_names = [c.name for c in cookies]
#         missing_cookies = [c for c in ['c_user', 'xs'] if c not in cookie_names]
#         if missing_cookies:
#             raise exceptions.InvalidCookies(f"Missing cookies with name(s): {missing_cookies}")
#         _scraper.session.cookies.update(cookies)
#         if not _scraper.is_logged_in():
#             raise exceptions.InvalidCookies(f"Cookies are not valid")
        
from selenium import webdriver

with open('/Users/zo-mac/Documents/repos/aus_fb_prop_scrape/www.facebook.com_cookies.json', 'r', newline='') as inputdata:
    cookies = json.load(inputdata)
curcookie = cookies[0]

curcookie['sameSite'] = 'Strict'   

driver=webdriver.Chrome()
time.sleep(2)
driver.get("https://www.facebook.com")
time.sleep(4)
driver.add_cookie(curcookie)
print('complete')
time.sleep(10)



