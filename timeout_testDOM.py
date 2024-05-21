from utils import *

logging.info("start")

options = chromeopts()
driver = build_driver(options)

url = 'https://www.google.com'

driver.get(url)

for id in psutil.pids():
    p = psutil.Process(id)
    if (p.name() == 'Google Chrome' ):
        pid = id

mem_df = pd.DataFrame(columns=['logtime','mem_avail','mem_used','mem_percent', 'chrome_percent', 'postcount'])

time.sleep(60)

ts = time.strftime('%m%d_%H%M')
os.mkdir(f'logs/test/{ts}') 
to_del = []
scrapeLimit = 1000
loop = 0
totalPosts = 0

say('Begin scrolling')
try:
    html = driver.find_element(By.TAG_NAME, "html")
    base = psutil.virtual_memory().percent
    base_diff = 0
    max_posinset = 0
    posinset_inner, posinset_html, = {}, {}
    memoryLimit = 10

    while loop <= 0 and len(posinset_inner) < 970:
        while len(posinset_inner) < scrapeLimit:
            min_posinset = max_posinset
            posts = driver.find_elements(By.CSS_SELECTOR, 'div[aria-posinset]') #"div[aria-describedby")
            
            max_posinset = len(posts)
            print()
            print('min / max:', min_posinset, '/', max_posinset)
            scraped_list = []
            for idx, post_element in enumerate(posts[min_posinset:max_posinset]): ## WHEN UPDATING MIN POSINSET, nEED TO SUBTRACT 1
                try:
                    posinset_value = int(post_element.get_attribute("aria-posinset"))
                    scraped_list.append(posinset_value)
                    innertext, outerhtml = scrapePage(post_element)

                    posinset_inner.update({posinset_value:innertext})
                    posinset_html.update({posinset_value:outerhtml})

                    to_del.append(post_element)
                except Exception as e:
                    print('Observed error:', e)
                    continue

                if len(innertext) == 0:
                    innertext, outerhtml = parse_single_post(innertext, outerhtml, html, post_element)

            print('Scraped posts:', scraped_list)    
            print("** length of current scraped posts:", totalPosts + len(posinset_inner))
            # current_classes_count = count_classes(driver)
            # print("Current classes and counts:", dict(current_classes_count))
            mem = build_memory_stats(pid, (len(posinset_inner) + ((loop) * 1000)))

            base_diff = mem[3] - base 

            mem_df.loc[len(mem_df)] = mem

            time.sleep(4)
            say('scroll down')
            scrollPage(html, 4, 'down')
            time.sleep(2)

            if len(to_del) >= 100:
                say('save outerhtml')
                dom_html = driver.execute_script("return document.documentElement.outerHTML;")
                # Write the DOM HTML to a file
                with open('full_dom.html', 'w', encoding='utf-8') as file:
                    file.write(dom_html)
                to_del = delete_post(to_del, driver)
                max_posinset = 0
                say('posts deleted')
                del_dom_html = driver.execute_script("return document.documentElement.outerHTML;")
                # Write the DOM HTML to a file
                with open('del_dom.html', 'w', encoding='utf-8') as file:
                    file.write(del_dom_html)
                time.sleep(60)

        logging.warning(f'*** SCRAPE LIMIT REACHED - {scrapeLimit} POSTS')
        say('Scrape Limit Reached')
        
        pickleDump(posinset_inner, 'innertext', ts, loop)
        pickleDump(posinset_html, 'outerhtml', ts, loop)
        loop = loop + 1
        totalPosts = loop * 1000
        posinset_inner, posinset_html, = {}, {}
        time.sleep(30)

    say('3970 posts hit')
    time.sleep(4)
    say('scroll down')
    scrollPage(html, 4, 'down')
    time.sleep(2)
    ending = input("Enter Any key to Continue")
    
except Exception as error: 
    print('ERROR:', error)
    # build_figs(mem_df, 'test', ts)
    # mem_df.to_csv(f'logs/test/{ts}/memory_log.csv', index=False)



build_figs(mem_df, 'test', ts)
mem_df.to_csv(f'logs/test/{ts}/memory_log.csv', index=False)

# pickleDump(posinset_inner, 'innertext', ts)
# pickleDump(posinset_html, 'outerhtml', ts)

print('start:', ts)
print('finish:', time.strftime('%m%d_%H%M'))
print('postcount:', len(posinset_inner))

# Write browser logs to file
browser_logs = driver.get_log('browser')
with open('browser_logs.txt', 'w') as file:
    for log in browser_logs:
        file.write(f"{log}\n")

# Write performance logs to file
performance_logs = driver.get_log('performance')
with open('performance_logs.txt', 'w') as file:
    for log in performance_logs:
        formatted_log = json.dumps(json.loads(log['message']), indent=4)
        file.write(f"{formatted_log}\n")

driver.quit()

# WebDriverException: # OR whatever memory error occurs on crash #### ***

    # for i in range(0,len(posts)):
    #     with open(f"outputs/02/outerHTML/{ts}_output_outerHTML.txt", "a") as f:
    #         print(posts[i].get_attribute('outerHTML'), file = f)
    #         print(':::', file=f)
