from utils import *

def init_selenium_driver():
    options = chromeopts()
    driver = build_driver(options)
    return build_driver(options)

def get_chrome_pid():
    for id in psutil.pids():
        p = psutil.Process(id)
        if (p.name() == 'Google Chrome' ):
            pid = id
        else:
            pid = np.NaN
    return pid

def create_memory_df():
    columns=['logtime','mem_avail','mem_used','mem_percent', 'chrome_percent', 'postcount']
    return pd.DataFrame(columns=columns)

def create_log_dir():
    ts = time.strftime('%m%d_%H%M')
    os.mkdir(f'logs/test/{ts}') 
    return ts


logging.info("start")

driver = init_selenium_driver()
driver.get('https://www.google.com')

mem_df = create_memory_df()
ts = create_log_dir()
pid = get_chrome_pid()

time.sleep(60)

to_del = []
scrapeLimit = 1000
loop = 0
totalPosts = 0
memoryLimit = 10

say('Begin scrolling')
try:
    html = driver.find_element(By.TAG_NAME, "html")
    base = psutil.virtual_memory().percent
    base_diff = 0
    max_posinset = 0
    posinset_inner, posinset_html, = {}, {}
    
    while loop <= 2 and len(posinset_inner) < 970:
        while len(posinset_inner) < scrapeLimit:
            min_posinset = max_posinset
            posts = driver.find_elements(By.CSS_SELECTOR, 'div[aria-posinset]') 
            
            max_posinset = len(posts)
            logging.info('min / max:', min_posinset, '/', max_posinset)
            scraped_list = []
            for idx, post_element in enumerate(posts[min_posinset:max_posinset]): 
                try:
                    posinset_value = int(post_element.get_attribute("aria-posinset"))
                    scraped_list.append(posinset_value)
                    innertext, outerhtml = scrapePage(post_element)

                    posinset_inner.update({posinset_value:innertext})
                    posinset_html.update({posinset_value:outerhtml})

                    to_del.append(post_element)
                    
                except Exception as e:
                    logging.error('Observed error:', e)
                    continue

                if not innertext:
                    innertext, outerhtml = parse_single_post(innertext, outerhtml, html, post_element)

            logging.info('Scraped posts:', scraped_list)    
            logging.info("** length of current scraped posts:", totalPosts + len(posinset_inner))
            mem = build_memory_stats(pid, (len(posinset_inner) + ((loop) * 1000)))

            base_diff = mem[3] - base 
            mem_df.loc[len(mem_df)] = mem

            time.sleep(4)
            say('scroll down')
            scrollPage(html, 4, 'down')
            time.sleep(2)

            if len(to_del) >= 20:
                to_del = delete_post(to_del, driver)
                max_posinset = 0
                time.sleep(60)

        logging.warning(f'*** SCRAPE LIMIT REACHED - {scrapeLimit} POSTS')
        say('Scrape Limit Reached')
        
        pickleDump(posinset_inner, 'innertext', ts, loop)
        pickleDump(posinset_html, 'outerhtml', ts, loop)
        loop = loop + 1
        totalPosts = loop * 1000
        posinset_inner, posinset_html = {}, {}
        time.sleep(30)

    time.sleep(4)
    scrollPage(html, 4, 'down')
    time.sleep(2)
    
except Exception as error: 
    logging.error('ERROR:', error)

build_figs(mem_df, 'test', ts)
mem_df.to_csv(f'logs/test/{ts}/memory_log.csv', index=False)

logging.info('start:', ts)
logging.info('finish:', time.strftime('%m%d_%H%M'))
logging.info('postcount:', len(posinset_inner))

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
