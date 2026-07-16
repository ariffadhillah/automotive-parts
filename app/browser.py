
import time
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from seleniumbase import Driver



def setup_browser():
    # Konfigurasi Chrome Options
    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-extensions")

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    ]


    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")


    proxy_list = [
        "67.43.227.227:18213",
        "67.43.228.251:14791",
        "213.183.56.99:80",
        "200.174.198.86:8888",
        "123.30.154.171:7777",
    ]

    random_proxy = random.choice(proxy_list)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"--proxy-server={random_proxy}")
        # Inisialisasi browser
    browser = webdriver.Chrome(options=chrome_options)
    browser.maximize_window()



    # Buka halaman awal
    browser = Driver(uc=True)
    url = "https://www.autodoc.de"
    # browser.get("https://www.doctolib.fr/")
    time.sleep(5)  # Tunggu halaman terbuka
    browser.uc_open_with_reconnect(url, 10)
    browser.uc_gui_click_captcha()
    try:
        browser.uc_gui_click_captcha()
    except Exception as e:
        print(f"Tidak ada captcha yang perlu diklik: {e}")
        
    try:
        agree_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        agree_button.click()
        print("Tombol cookie 'didomi-notice-agree-button' diklik!")
    except Exception as e:
        print(f"Tombol cookie tidak ditemukan atau tidak bisa diklik: {e}")

    browser.refresh()
    time.sleep(10)      

    return browser
