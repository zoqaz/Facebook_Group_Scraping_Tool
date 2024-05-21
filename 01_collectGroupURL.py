from utils import *

print("start")

options = chromeopts()
driver = build_driver(options)

pw = pd.read_csv('pw.csv',header=None)
url = 'https://www.facebook.com'

driver.get(url)
time.sleep(3)

### LOGIN TO FB
typing_func(driver, By.NAME, pw.iloc[0][0], 'email')
time.sleep(rand.uniform(0.5, 2.8))
typing_func(driver, By.NAME, pw.iloc[0][1], 'pass')
time.sleep(rand.uniform(9.5, 11))
driver.find_element(By.NAME, "email").send_keys(Keys.RETURN)

time.sleep(rand.uniform(9.5, 11))

# get_url = driver.current_url

# while "login" in get_url:  
#     time.sleep(5)
#     typing_func(driver, By.NAME, pw.iloc[0][1], 'pass')
#     time.sleep(6)
#     driver.find_element(By.NAME, "pass").send_keys(Keys.RETURN)
#     time.sleep(10)
#     get_url = driver.current_url

# print(get_url)
#driver.find_element_by_name('pass').send_keys(pw.iloc[0][1])

typing_func(driver, By.XPATH, 'Groups', "//input[@type='search']")
time.sleep(rand.uniform(0.5, 2.8))
driver.find_element(By.XPATH, "//input[@type='search']").send_keys(Keys.RETURN)

time.sleep(rand.uniform(15, 20))

driver.find_element(By.CSS_SELECTOR, "a[aria-label='See all']").click()

time.sleep(rand.uniform(3.3,5.3))

for scroll in range(6):
    time.sleep(1)
    # Scroll down to bottom
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

links = driver.find_elements(By.TAG_NAME, 'a')

time.sleep(rand.uniform(2,3))

df = pd.DataFrame(columns=['href','groupName'])

for i in range(0, len(links)):
    #if 'HREF="HTTPS://WWW.FACEBOOK.COM/GROUPS/' in links[i].get_attribute('outerHTML').upper():
    if 'role="presentation"' in links[i].get_attribute('outerHTML'):
        groups = parseHTML(links[i].get_attribute('outerHTML'))
        new_row = {'href': groups[0], 'groupName': groups[1]}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

df.to_csv('outputs/01/group_urls.csv')

time.sleep(20)

driver.close()

print("end")