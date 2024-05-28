from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import random as rand
import sys
import calendar
from bs4 import BeautifulSoup
import re
import psutil
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime as dt
import pickle 
import pprint
import logging
from webdriver_manager.chrome import ChromeDriverManager
import json
from collections import Counter

group_name = 'Fairy Floss Real Estate' 

inner_repl = {
    "Shared with Members of " + group_name: "", 
    "Top contributor": "", 
    "Shared with Public group": "", 
    "New contributor": "",
    "·": "",
    group_name: "",
    "Write a comment": "",
    "View more comments": "",
    "Message": "",
    "Like": "",
    "Comment": "",
    "Reply": ""
    }

date_repl = {
    "Shared with Members of " + group_name: "", 
    "Top contributor": "", 
    "Shared with Public group": "", 
    "New contributor": "",
    "·": ""
    }

class ColoredFormatter(logging.Formatter):
    # Define ANSI escape codes for various log levels
    COLORS = {
        'WARNING': '\x1b[33;1m',  # Yellow with bold
        'INFO': '\x1b[32m',       # Green
        'DEBUG': '\x1b[34m',      # Blue
        'ERROR': '\x1b[31m',      # Red
        'CRITICAL': '\x1b[31;1m'  # Red bold
    }

    RESET = '\x1b[0m'  # Reset color

    # Define the format for log messages
    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelname, '')}%(levelname)s - %(asctime)s - %(message)s{self.RESET}"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Set up logging
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.WARNING)

def chromeopts():
    opts = webdriver.ChromeOptions()
    opts.add_argument("start-maximized")
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument('--no-sandbox')   
    opts.add_argument('--disable-dev-shm-usage')

    opts.add_argument("disable-infobars")
    opts.add_argument("--disable-extensions")
    opts.add_argument('--disable-application-cache')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--blink-settings=imagesEnabled=false')
    opts.add_argument("--log-level=OFF")
    opts.add_argument("--disable-cache")
    opts.add_argument("--disk-cache-size=0")

    opts.add_argument("--disable-logging")
    opts.add_argument("--silent")   
    opts.add_argument("--disable-sync")
    opts.add_argument("--disable-background-networking")
    opts.add_argument("--disable-default-apps")
    opts.add_argument("--disable-hang-monitor")
    opts.add_argument("--disable-popup-blocking") 
    opts.add_argument("--disable-prompt-on-repost")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-breakpad")
    opts.add_argument("--disable-client-side-phishing-detection")
    opts.add_argument("--disable-component-update")
    opts.add_argument("--memory-pressure-off")
    opts.add_argument("--disk-cache-size=0")
    opts.add_argument("--disable-web-security")
    opts.add_argument("--disable-session-crashed-bubble")
    opts.add_argument("--disable-restore-session-state")  
    opts.add_argument("--process-per-site") 
    opts.add_argument("--single-process")  
  

    opts.add_argument("--enable-logging")  
    opts.add_argument("--v=1")  
    opts.add_argument("--log-level=0")  

    # Path where ChromeDriver logs will be saved
    opts.add_argument("--log-path=chromedriver.log")
    opts.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'performance': 'ALL'})


    # opts.add_argument('headless')     
    prefs = {"profile.default_content_setting_values.notifications" : 2,
         "credentials_enable_service": False,
         "profile.password_manager_enabled": False,
         "profile.managed_default_content_settings.images": 2}
    opts.add_experimental_option("prefs",prefs)
    opts.add_experimental_option(
        "excludeSwitches", ['enable-automation'])
    return opts

def build_driver(options):
    driv = webdriver.Chrome(options = options)
    driv.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driv.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    return driv

def typing_func(driva, method, word_arg, element):
    for c in word_arg:
        driva.find_element(method, element).send_keys(c)
        time.sleep(rand.random())

def parseHTML(chunk):
    bPos = str.find(chunk, 'href="')+len('href="') 
    ePos = str.find(chunk[bPos:], '"') 
    href = chunk[bPos:(ePos+bPos)]

    aPos = str.find(chunk,">")+1
    zPos = str.find(chunk, "</a>")
    groupName = chunk[aPos:zPos]
    return href, groupName

def strip(string):
    words = string.split()
    words = [word for word in words if "#" not in word]
    string = " ".join(words)
    clean = ""
    for c in string:
        if str.isalnum(c) or (c in [" ", ".", ","]):
            clean += c
    return clean

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
        text = strip(text)
    return text

def build_memory_stats(pid, postcount):
    mem = psutil.virtual_memory()
    pr = psutil.Process(pid)

    chromeperc = pr.memory_percent()
    # chromevms = pr.memory_info()[1] / (1024.0 ** 3)
    # chromerss = pr.memory_info()[0] / (1024.0 ** 3)

    memavail = mem.available / (1024.0 ** 3)
    memused = mem.used / (1024.0 ** 3)
    memperc = mem.percent
    logtime = time.strftime('%H:%M:%S')

    appendRow = [logtime, memavail, memused, memperc, chromeperc, postcount]
    return appendRow

def build_figs(df, folder, timestamp):
    plt.title('Overall Memory Usage')
    plt.ylabel('Memory consumption (%)')
    plt.xlabel('Post Count')
    plt.plot(df["postcount"], df["mem_percent"])
    plt.savefig(f'logs/{folder}/{timestamp}/overall_mem.png')
    plt.clf()

    plt.title('Postcount')
    plt.ylabel('Number of Posts')
    plt.xlabel('Time')
    plt.plot(df['logtime'], df['postcount'])
    plt.savefig(f'logs/{folder}/{timestamp}/postcount.png')
    plt.clf()

    plt.title('Chrome Memory Usage')
    plt.ylabel('Consumption (%)')
    plt.xlabel('Post Count')
    plt.plot(df['postcount'], df['chrome_percent'])
    plt.savefig(f'logs/{folder}/{timestamp}/chrome_mem.png')
    plt.clf()

def say(msg, voice = "Victoria"):
    os.system(f'say -v {voice} {msg}')

def pickleDump(pklfile, htmltype, ts, run):
    if htmltype == 'innertext':
        with open(f'outputs/02/{htmltype}/{ts}_posinset_inner_{run}.pkl', 'wb') as f:
            pickle.dump(pklfile, f)
    elif htmltype == 'outerhtml':
        with open(f'outputs/02/{htmltype}/{ts}_posinset_html_{run}.pkl', 'wb') as f:
            pickle.dump(pklfile, f)
    elif htmltype == 'outertext':
        with open(f'outputs/02/{htmltype}/{ts}_posinset_outer_{run}.pkl', 'wb') as f:
            pickle.dump(pklfile, f)
    else:
        logging.error('PICKLEFILE NOT DUMPED')

def scrollPage(element, num, direction):
    for i in range(num):
        if direction == 'down':
            element.send_keys(Keys.PAGE_DOWN)
        elif direction == 'up':
            element.send_keys(Keys.PAGE_UP)
        else:
            logging.error('INVALID SCROLL')

def scrapePage(element):
    el1 = element.get_attribute("innerText")
    el2 = element.get_attribute("outerHTML")
    # el3 = element.get_attribute("outerText")
    return el1, el2

def count_classes(driver):
    elements = driver.find_elements(By.XPATH, "//*")  # Select all elements in the page
    class_counts = Counter()
    for element in elements:
        classes = element.get_attribute("class")
        if classes:  # Element might have no class attribute
            for cls in classes.split():  # Handle multiple classes
                class_counts[cls] += 1
    return class_counts

def delete_post(post_list, webdriver):
    del_list = []  
    error_list = []  
    while len(post_list) > 0:
        del_posinset = post_list.pop()
        try:
            del_element = del_posinset
            del_list.append(del_element.get_attribute("aria-posinset"))
            webdriver.execute_script(
                """
                var element = arguments[0];
                var parent = element.parentNode;
                if (parent) {
                    var clone = element.cloneNode(true); 
                    parent.replaceChild(clone, element); 
                    clone.remove(); 
                }
                element = null; 
                """, del_element)
        except Exception as error:
            logging.error(error)
            continue
        time.sleep(0.5)
    logging.info('deleted posts:', del_list)
    return post_list

def parse_single_post(el1, el2, webpage, single_post):
    chck = 0
    while len(el1) == 0:
        time.sleep(1)
        scrollPage(webpage, 1, 'down')
        time.sleep(2)
        el1, el2 = scrapePage(single_post)
        time.sleep(1)
        say(str(len(el1)))
        chck = chck + 1
        if chck == 2:
            break
    return el1, el2