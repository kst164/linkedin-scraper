from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

import sys

# chromium:
opts = webdriver.ChromeOptions()
# TODO: Change data dir (need to be logged in to linkedin for code to work, so need a persistent profile)
opts.add_argument("--user-data-dir=/home/kartheek/.config/chromium/Default")
driver = webdriver.Chrome(options=opts)

# to use firefox, comment out the above lines and uncomment the below lines:
# opts = webdriver.FirefoxOptions()
# TODO: change profile path (if using FF)
# opts.add_argument("--profile /home/kartheek/.mozilla/firefox/xxxxxxxx.default-release")
# driver = webdriver.Firefox(options=opts)

# TODO: change post link (this is just a random post I'm using for testing)
# driver.get('https://www.linkedin.com/posts/sankhojyoti-halder-9272781aa_elitecommunity-elitecisosglobal-ciso-activity-7046783423721398273-x_OM/')
driver.get(sys.argv[1])


def load_all_comments():
    while True:
        load_more_container = driver.find_elements(By.CLASS_NAME, 'comments-comments-list__show-previous-container')
        if len(load_more_container) > 0:
            button = load_more_container[0].find_elements(By.TAG_NAME, 'button')
            if len(button) > 0:
                try:
                    button[0].click()
                except:
                    pass
            time.sleep(1)
        else:
            break

try:
    # Wait till the repost button is loaded, then click it
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'comments-comments-list__show-previous-container'))
    ).click()

    load_all_comments()
    link_tags = driver.find_elements(By.CLASS_NAME, 'comments-post-meta__actor-link')
    user_links = {link.get_attribute('href') for link in link_tags}
    print(len(user_links))
    # print(json.dumps(list(user_links), indent=4))
except Exception as e:
    print(e)
    pass
finally:
    driver.quit()
