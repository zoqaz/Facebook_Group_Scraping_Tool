from utils import *

def init_selenium_driver():
    options = chromeopts()
    return build_driver(options)

def get_chrome_pid():
    for id in psutil.pids():
        p = psutil.Process(id)
        if (p.name() == 'Google Chrome' ):
            pid = id
        else:
            pass
    if pid is None:
        logging.error("Google Chrome process not found.")
    return pid

def parse_args():
    parser = argparse.ArgumentParser(description="Script parameters")
    parser.add_argument('--delete_limit', type=int, default=20, help='Number of posts to scrape before deleting them from the feed')
    parser.add_argument('--scrape_limit', type=int, default=3950, help='Total number of posts to scrape')
    return parser.parse_args()

def create_memory_df():
    columns=['logtime','mem_avail','mem_used','mem_percent', 'chrome_percent', 'postcount']
    return pd.DataFrame(columns=columns)

def create_log_dir():
    ts = time.strftime('%m%d_%H%M')
    os.mkdir(f'logs/test/{ts}') 
    return ts

def main():
    args = parse_args()

    DELETE_LIMIT = args.delete_limit
    SCRAPE_LIMIT = args.scrape_limit
    totalPosts = 0
    to_del = []
    posinset_inner, posinset_html, = {}, {}

    driver = init_selenium_driver()
    driver.get('https://www.facebook.com')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "html")))
    
    time.sleep(5)

    WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.NAME, "email")))
    WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.NAME, "pass")))

    time.sleep(10)

    sort = '/?sorting_setting=CHRONOLOGICAL_LISTINGS'
    driver.get(f'https://www.facebook.com/groups/117412174975402{sort}')

    mem_df = create_memory_df()
    ts = create_log_dir()
    pid = get_chrome_pid()
    max_posinset = 0

    try:
        html = driver.find_element(By.TAG_NAME, "html")
        base = psutil.virtual_memory().percent 

        while len(posinset_inner) < SCRAPE_LIMIT:
            min_posinset = max_posinset
            posts = driver.find_elements(By.CSS_SELECTOR, 'div[aria-posinset]') 
            
            max_posinset = len(posts)
            # logging.info(f'min & max: {min_posinset} & {max_posinset}')
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
                    logging.error(f'Observed error: {e}')
                    continue
                if not innertext:
                    innertext, outerhtml = parse_single_post(innertext, outerhtml, html, post_element)

            logging.info(f'Scraped posts: {scraped_list}')    
            logging.info(f'** length of current scraped posts: {totalPosts + len(posinset_inner)}')
            mem = build_memory_stats(pid, len(posinset_inner))

            base_diff = mem[3] - base 
            mem_df.loc[len(mem_df)] = mem

            time.sleep(4)
            say('scroll down')
            scrollPage(html, 4, 'down')
            time.sleep(2)

            if len(to_del) >= 20:
                to_del = delete_post(to_del, driver)
                max_posinset = 0
                time.sleep(10)

        logging.warning(f'*** SCRAPE LIMIT REACHED AT {time.strftime("%m%d_%H%M")}')
        
        pickleDump(posinset_inner, 'innertext', ts)
        pickleDump(posinset_html, 'outerhtml', ts)
        time.sleep(30)

        time.sleep(4)
        scrollPage(html, 4, 'down')
        time.sleep(2)
        
    except Exception as error: 
        logging.error(f'ERROR: {error}')

    build_figs(mem_df, 'test', ts)
    mem_df.to_csv(f'logs/test/{ts}/memory_log.csv', index=False)

    logging.info(f'start: {ts}')
    logging.info(f'finish: {time.strftime("%m%d_%H%M")}')
    logging.info(f'postcount: {len(posinset_inner)}')

    driver.quit()

if __name__ == '__main__':
    logging.info("start")

    main()

    time.sleep(60)
