from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

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
driver.get('https://www.linkedin.com/posts/iithyderabad_iithyderabad-pg-admissions-activity-7042866502886170624-CQHH/')


# keep clicking the 'show more' button until there are no more reposts to load.
# returns the list of reposts
def load_all_reposts():
    while True:
        repost_list_view = driver.find_element(By.CLASS_NAME, 'scaffold-finite-scroll')

        load_more = repost_list_view.find_elements(By.XPATH, 'div[2]/*')
        if len(load_more) > 0:
            button = repost_list_view.find_elements(By.XPATH, 'div[2]/div/button')
            if len(button) > 0:
                try:
                    button[0].click()
                except:
                    pass
            time.sleep(1)
        else:
            # No more reposts to load
            break
    return repost_list_view.find_elements(By.XPATH, 'div[1]/div')

# parse a single repost
# returns None if the repost is not a share
# returns a tuple of (name, link, like_count, comment_count) if the repost is a share
def parse_share(repost):
    big_img = repost.find_elements(By.CLASS_NAME, 'EntityPhoto-circle-3')
    if len(big_img) == 0:
        # shares and reposts have different sizes of images for the profile pic (bigger for shares)
        # share posts have EntityPhoto-circle-3, reposts have EntityPhoto-circle-0
        return
    # EntityPhoto-circle-3 exists, so this is a share

    name = repost.find_element(By.XPATH, ".//span[contains(@class, 'update-components-actor__name')]/span").text
    link = repost.find_element(By.XPATH, './/a').get_attribute('href')

    like_span = repost.find_elements(By.CLASS_NAME, 'social-details-social-counts__reactions-count')
    like_count = 0 if len(like_span) == 0 else int(like_span[0].text)

    comment_span = repost.find_elements(By.CLASS_NAME, 'social-details-social-counts__comments')
    comment_count = 0 if len(comment_span) == 0 else int(comment_span[0].text.split(' ')[0]) # remove the ' comments' text

    return name, link, like_count, comment_count


try:
    # Wait till the repost button is loaded, then click it
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, 'social-details-social-counts')]//button[contains(., 'repost')]"))
    ).click()

    # wait till the repost list view is loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'scaffold-finite-scroll'))
    )

    reposts = load_all_reposts()
    scraped_stats = []
    for repost in reposts:
        parsed = parse_share(repost)
        if parsed == None: # not a share
            continue
        name, link, like_count, comment_count = parsed
        scraped_stats.append({
            'name': name,
            'link': link.split('?')[0], # remove garbage after the link
            'like_count': like_count,
            'comment_count': comment_count,
        })

    # TODO: change scoring metric?
    scraped_stats.sort(key=lambda x: x['like_count'], reverse=True)

    # TODO: change output file? Or trigger some other action?
    with open('data.json', 'w') as f:
        json.dump(scraped_stats, f)
except Exception as e:
    # print(e)
    pass
finally:
    driver.quit()
