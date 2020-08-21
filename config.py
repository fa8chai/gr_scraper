from selenium import webdriver

DIRECTORY = 'reports'

SEARCH = 'poetry'
EMAIL = ''
PASSWORD = ''


BASE_URL = "https://www.goodreads.com/"


def get_chrome_web_driver(options):
    return webdriver.Chrome('./chromedriver', chrome_options=options)

def get_web_driver_options():
    return webdriver.ChromeOptions()

def set_ignore_certificate_error(options):
    options.add_argument('--ignore-certificate-errors')

def set_browser_as_incognito(options):
    options.add_argument('--incognito')

def disable_popup(options):
    chrome_prefs = {}
    options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = { "popups": 1 }


