from utils import *

import os


say('test')

print("start")

options = chromeopts()
driver = build_driver(options)

url = 'https://www.facebook.com'

driver.get(url)
time.sleep(25)

groups = pd.read_csv('outputs/01/group_urls.csv')

url2 = groups.iloc[0]['href']
groupName = groups.iloc[0]['groupName']

repl = {"(": "", 
        ")": "", 
        "&amp;": "and", 
        "/": "",
        ",": "",
        '"': "",
        "'": "",
        ".": "",
        " ": ""}

groupName = replace_all(groupName, repl)
ts = time.strftime('%m%d_%H%M')
os.mkdir(f'logs/{groupName}/{ts}') 

chrono = '?sorting_setting=CHRONOLOGICAL_LISTINGS'
driver.get(url2+chrono)

time.sleep(10)

mem_df = pd.DataFrame(columns=['logtime','mem_avail','mem_used','mem_percent', 'chrome_percent', 'chrome_vms', 'chrome_rss'])

try:
    for scroll in range(230):
        mem = build_memory_stats()
        mem_df.loc[len(mem_df)] = mem
        
        time.sleep(2)
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        # try:
        #     links = driver.find_element(By.LINK_TEXT, "See more")
        #     for link in links:
        #         link.click()
        # except NoSuchElementException:
        #     print('No "See More" links found')
        #     pass
        print(scroll)
except WebDriverException: 
    build_figs(mem_df, groupName, ts)
    mem_df.to_csv(f'logs/{groupName}/{ts}/memory_log.csv', index=False)

build_figs(mem_df, groupName, ts)
mem_df.to_csv(f'logs/{groupName}/{ts}/memory_log.csv', index=False)

time.sleep(rand.uniform(2,3))

# below is for extracting elements from the dom whilst scrolling etc, will need to be embedded into the try above

posts = driver.find_elements(By.CSS_SELECTOR, "div[aria-describedby")

print()
print(len(posts))

for i in range(0,len(posts)):
    with open(f"outputs/02/{ts}_output_outerHTML.txt", "a") as f:
        print(posts[i].get_attribute('outerHTML'), file = f)
        print(':::', file=f)

print()

driver.quit() 