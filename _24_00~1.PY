import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime

element_for_Total_Play_speed = '''
<a class="no-link-chev btnBanner" href="/personaliza?150#internet" promo-name="150 megas 2p" promo-id="1" target="_blank">
    <img class="d-none d-md-block w-100" src="/assetsv2/img/home/sliders/Banner1.png">
    <img class="d-block d-md-none" src="/assetsv2/img/home/sliders/Banner1_mobile.png">
</a>'''

# the regular expression pattern to extract out the number of Mbps (megas):
# pattern = r'promo-name="(\d+ megas)'  # this one is a string
pattern = r'promo-name="(\d+)'  # this is an integer

# search for the pattern in the string
match = re.search(pattern, element_for_Total_Play_speed)

# check if a match was found
if match:
    extracted_text = match.group(1)
    # print(extracted_text)
else:
    extracted_text = "No internet speed found."

# constants:
PROMISED_SPEEDS_DOWN = extracted_text
PROMISED_SPEEDS_UP = 10

# print(
#     f"\nThis is the first print statement and shows the integer of the extracted text, which is then converted to PROMISED_DOWNLOAD_SPEEDS: {int(PROMISED_DOWNLOAD_SPEEDS)}")

TWITTER_EMAIL = "YOUR_EMAIL"
TWITTER_PASSWORD = "YOUR_PASSWORD"

URL_FOR_SPEEDTEST = "https://www.speedtest.net/"


# ChromeDriverManager is handled by the webdriver_manager.chrome


class InternetSpeedTwitterBot:
    def __init__(self, PROMISED_SPEEDS_DOWN, PROMISED_SPEEDS_UP):
        # driver = init_driver()  #try this 1st
        self.driver = self.init_driver()
        self.PROMISED_SPEEDS_DOWN = PROMISED_SPEEDS_DOWN
        self.PROMISED_SPEEDS_UP = PROMISED_SPEEDS_UP

        self.open_website(URL_FOR_SPEEDTEST)
        self.tweet_at_provider()

    def init_driver(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        self.log_message("webdriver initialized.")
        return driver

    # my function to log messages:
    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{timestamp} - {message}")

    def print_test_for_megas_speed(self, PROMISED_SPEEDS_DOWN, PROMISED_SPEEDS_UP):
        self.log_message(
            f"The Promised Download speed which is stated on Comcast's Website is: {PROMISED_SPEEDS_DOWN} (Mbps)")
        self.log_message(
            f"The Promised Upload speed which is stated on Comcast's Website is: {PROMISED_SPEEDS_UP} (Mbps)")

    def open_website(self, url):
        self.driver.get(URL_FOR_SPEEDTEST)
        self.log_message(f"Successfully opened the website: {URL_FOR_SPEEDTEST}")

        self.print_test_for_megas_speed(self.PROMISED_SPEEDS_DOWN, self.PROMISED_SPEEDS_UP)

        time.sleep(2)

        self.press_go_button_and_get_internet_speed()

    def press_go_button_and_get_internet_speed(self):
        ACTUAL_DOWNLOAD_SPEED = ""
        ACTUAL_UPLOAD_SPEED = ""

        XPATH_for_speed_url = '//*[@id="container"]/div/div[3]/div/div/div/div[2]/div[3]/div[1]/a/span[4]'
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, XPATH_for_speed_url))
        )
        self.speed_button = self.driver.find_element(By.XPATH, XPATH_for_speed_url)
        self.speed_button.click()  # clicks on the Go button to generate the speeds
        print("The Go button was pushed to start the Internet Speed Test.")
        print(f"\nPlease wait for the Speed Check to complete :)")

        time.sleep(77)  # wait for the speed test to complete

        # trying to close a potential popup or ad after the speed test
        xpath_for_ad_close_button = '//*[@id="container"]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[3]/div/div/div[1]/div/div/div[2]/div[2]/a'
        backup_xpath_for_ad_close_button = '//*[@id="container"]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[8]/div/a/svg/use'
        final_backup_xpath = '/html/body/div[3]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[8]/div/a/svg/use'

        for xpath in [xpath_for_ad_close_button, backup_xpath_for_ad_close_button, final_backup_xpath]:
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                ad_close_button = self.driver.find_element(By.XPATH, xpath)
                ad_close_button_text = ad_close_button.text
                match = re.search(r'\b\d{9,13}\b', ad_close_button_text)
                if match:
                    result_id_number = match.group()
                    print(f"\nYour extracted Result ID number: {result_id_number}")
                self.driver.execute_script("arguments[0].click();", ad_close_button)
                print(f"\nClicked on the ad close button using XPath: {xpath}")
                break  # Exit the loop if click is successful
            except NoSuchElementException:
                print(f"Ad close button not found using XPath: {xpath}")
            except ElementClickInterceptedException:
                print(f"Element click intercepted using XPath: {xpath}")

        # Extracting actual download and upload speeds
        download_speed_xpath = '/html/body/div[3]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div[1]/div/div[2]/span'
        upload_speed_xpath = '/html/body/div[3]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div[2]/div/div[2]/span'

        try:
            download_speed_element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, download_speed_xpath))
            )
            ACTUAL_DOWNLOAD_SPEED = download_speed_element.text
            upload_speed_element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, upload_speed_xpath))
            )
            ACTUAL_UPLOAD_SPEED = upload_speed_element.text

            print(f"\nYour download speed is currently: {ACTUAL_DOWNLOAD_SPEED} Mbps")
            print(f"\nYour upload speed is currently: {ACTUAL_UPLOAD_SPEED} Mbps")
        except NoSuchElementException:
            print("Could not find the speed result elements.")
        except TimeoutException:
            print("Timed out waiting for the speed result elements.")

    def tweet_at_provider(self):
        pass


# creating an instance of internetspeedtwitterbot:
TwitterBot = InternetSpeedTwitterBot(PROMISED_SPEEDS_DOWN, PROMISED_SPEEDS_UP)

# we can now call the methods on the instance that was created just above

# TwitterBot.open_website(URL_FOR_SPEEDTEST)

TwitterBot.tweet_at_provider()

time.sleep(3)

#this is the end of the Internet Speed detection:

# starting the Twitter posting functionality:


import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

TWITTER_EMAIL = "g4hyatt@gmail.com"
TWITTER_PASSWORD = "zjiwel$.:168gfgccv"
twitter_url = "https://twitter.com/"
search_keyword_within_twitter = "Comcast"

ACTUAL_DOWNLOAD_SPEED = 150
ACTUAL_UPLOAD_SPEED = 25

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{timestamp} - {message}")

def init_driver():
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    log_message("webdriver initialized.")
    return driver

def login_twitter(driver, email, password):
    start_time = time.time()
    driver.get(twitter_url)
    log_message("Twitter page loaded.")

    wait = WebDriverWait(driver, 10)
    try:
        sign_in_button_xpath = "//a[@href='/login']"
        sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, sign_in_button_xpath)))
        sign_in_button.click()
        log_message("Sign-in button clicked.")

        selectors = [
            (By.XPATH, "//input[@name='session[username_or_email]']"),
            (By.CSS_SELECTOR, "input[autocomplete='username']"),
            (By.CSS_SELECTOR, "#react-root > div > div > div > main > div > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox > div.css-175oi2r.r-16y2uox.r-1jgb5lz.r-13qz1uu > div > div.css-175oi2r.r-1f1sjgu.r-mk0yit.r-13qz1uu > label > div > div.css-175oi2r.r-18u37iz.r-16y2uox.r-1wbh5a2.r-1wzrnnt.r-1udh08x.r-xd6kpl.r-1pn2ns4.r-ttdzmv > div > input"),
            (By.XPATH, "//*[@id='react-root']/div/div/div/main/div/div/div/div[2]/div[2]/div/div[5]/label/div/div[2]/div/input"),
            (By.XPATH, "/html/body/div/div/div/div/main/div/div/div/div[2]/div[2]/div/div[5]/label/div/div[2]/div/input"),
            (By.XPATH, "//input[@autocapitalize='sentences']")
        ]

        email_field = None
        for by, value in selectors:
            try:
                email_field = wait.until(EC.presence_of_element_located((by, value)))
                if email_field:
                    log_message("Email field found.")
                    break
            except TimeoutException:
                log_message(f"Email field not found using {by}='{value}'")

        if not email_field:
            raise Exception("Email field not found after trying all selectors.")

        email_field.send_keys(email)
        log_message("Email entered.")
        email_field.send_keys(Keys.RETURN)
        log_message("Email submitted.")

        password_selectors = [
            (By.NAME, 'password'),
            (By.CSS_SELECTOR, 'input[type="password"][autocomplete="current-password"]'),
            (By.CSS_SELECTOR, '.r-30o5oe'),
            (By.XPATH, "//input[@autocomplete='current-password']"),
            (By.XPATH, "//input[@type='password']")
        ]

        password_field = None
        for by, value in password_selectors:
            try:
                password_field = wait.until(EC.presence_of_element_located((by, value)))
                if password_field:
                    log_message("Password field found.")
                    break
            except TimeoutException:
                log_message(f"Password field not found with {by}='{value}'")

        if not password_field:
            raise Exception("Password field not found after trying all selectors.")

        password_field.send_keys(password)
        log_message("Password entered.")
        password_field.send_keys(Keys.RETURN)
        log_message("Login submitted.")

        end_time = time.time()
        total_time = end_time - start_time
        log_message(f"Login completed in {total_time:.2f} seconds.")

    except Exception as e:
        log_message(f"An error occurred during login: {str(e)}")

def navigate_to_twitter_explore(driver):
    wait = WebDriverWait(driver, 10)
    explore_button = None
    explore_selectors = [
        (By.CSS_SELECTOR, "#react-root > div > div > div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010.r-18u37iz > header > div > div > div > div:nth-child(1) > div.css-175oi2r.r-15zivkp.r-1bymd8e.r-13qz1uu.r-1awozwy > nav > a:nth-child(2) > div > div > svg"),
        (By.CSS_SELECTOR, "#react-root > div > div > div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010.r-18u37iz > header > div > div > div > div:nth-child(1) > div.css-175oi2r.r-15zivkp.r-1bymd8e.r-13qz1uu.r-1awozwy > nav > a:nth-child(2) > div > div"),
        (By.CSS_SELECTOR, "#react-root > div > div > div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010.r-18u37iz > header > div > div > div > div:nth-child(1) > div.css-175oi2r.r-15zivkp.r-1bymd8e.r-13qz1uu.r-1awozwy > nav > a:nth-child(2)"),
        (By.XPATH, "//a[@href='/explore']"),
        (By.XPATH, "//*[contains(@aria-label, 'Explore')]")
    ]

    for selector in explore_selectors:
        try:
            explore_button = wait.until(EC.element_to_be_clickable(selector))
            if explore_button:
                log_message("Explore button found.")
                explore_button.click()
                log_message("Navigated to Explore.")
                break
        except TimeoutException:
            log_message(f"Explore button not found using {selector[0]}='{selector[1]}'")

    if not explore_button:
        raise Exception("Explore button not found after trying all selectors.")

def search_twitter(driver, query):
    wait = WebDriverWait(driver, 10)
    search_xpath = "//input[@aria-label='Search query']"
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    log_message(f"Searched for {query}.")


def prepare_tweet(driver, message):
    wait = WebDriverWait(driver, 10)
    try:
        # Click the post button to open the tweet box
        post_button_xpath = "//a[@aria-label='Post']"
        post_button = wait.until(EC.element_to_be_clickable((By.XPATH, post_button_xpath)))
        post_button.click()
        log_message("Post button clicked.")

        # Layered catch mechanism for tweet box selection
        tweet_box_selectors = [
            "div[data-offset-key='1q64k-0-0']",
            "#layers > div:nth-child(2) > div > div > div > div > div > div.css-175oi2r.r-1ny4l3l.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv.r-1habvwh > div.css-175oi2r.r-1wbh5a2.r-htvplk.r-1udh08x.r-1867qdf.r-rsyp9y.r-1pjcn9w.r-1potc6q > div > div > div > div:nth-child(3) > div.css-175oi2r.r-kemksi.r-1h8ys4a.r-1moyyf3.r-1pp923h > div:nth-child(1) > div > div > div > div.css-175oi2r.r-18u37iz.r-184en5c > div.css-175oi2r.r-1iusvr4.r-16y2uox.r-1777fci.r-1h8ys4a.r-1bylmt5.r-13tjlyg.r-7qyjyx.r-1ftll1t > div > div > div > div > div > div > div > div > div > div > div > label > div.css-175oi2r.r-1wbh5a2.r-16y2uox > div > div > div > div > div > div.DraftEditor-editorContainer > div > div > div > div",
            "//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[1]/div/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div/div/div/div/label/div[1]/div/div/div/div/div/div[2]/div/div/div/div",
            "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[1]/div/div/div/div[1]/div[2]/div/div/div/div/div/div/div/div/div/div/div/label/div[1]/div/div/div/div/div/div[2]/div/div/div/div"
        ]

        tweet_box = None
        for selector in tweet_box_selectors:
            try:
                if selector.startswith(("//", "/html")):
                    tweet_box = wait.until(EC.visibility_of_element_located((By.XPATH, selector)))
                else:
                    tweet_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                if tweet_box:
                    log_message("Tweet box found.")
                    break
            except TimeoutException:
                log_message(f"Tweet box not found using selector: {selector}")

        if not tweet_box:
            raise Exception("Tweet box not found after trying all selectors.")

        # Scroll the tweet box into view
        driver.execute_script("arguments[0].scrollIntoView();", tweet_box)

        tweet_box.send_keys(message)
        log_message("Message typed in the tweet box.")

        # Do not submit the tweet, only type the message into the tweet box
        # tweet_box.send_keys(Keys.RETURN)  # This line should remain commented to prevent posting

    except Exception as e:
        log_message(f"An error occurred while preparing the tweet: {str(e)}")



def main():
    driver = init_driver()
    login_twitter(driver, TWITTER_EMAIL, TWITTER_PASSWORD)
    navigate_to_twitter_explore(driver)
    search_twitter(driver, search_keyword_within_twitter)
    prepare_tweet(driver, f"Thank you for these speeds: {ACTUAL_DOWNLOAD_SPEED} Mbps Download and {ACTUAL_UPLOAD_SPEED} Mbps Upload")
    log_message("Browser will remain open until manually closed.")
    input("Press Enter to close the browser...")
    driver.quit()

if __name__ == "__main__":
    main()
