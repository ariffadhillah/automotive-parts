import requests
import json
from bs4 import BeautifulSoup
import csv
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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


    # chrome_options.add_argument(
    #     "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    # )
    

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
    browser.maximize_window()

    try:
        agree_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        agree_button.click()
        print("Tombol cookie 'didomi-notice-agree-button' diklik!")
    except Exception as e:
        print(f"Tombol cookie tidak ditemukan atau tidak bisa diklik: {e}")




    # for cookie in cookies:
    #     browser.add_cookie(cookie)

    browser.refresh()
    time.sleep(10)      

    return browser



def open_to_website(browser):
    browser.get("https://www.autodoc.de/autoteile/bremsscheibe-10132/hyundai/accent/accent-ii-stufenheck-lc/18694-1-3")
    time.sleep(10)


    # Coba klik tombol dengan ID "didomi-notice-agree-button"
    try:
        agree_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        agree_button.click()
        print("Tombol cookie 'didomi-notice-agree-button' diklik!")
    except Exception as e:
        print(f"Tombol cookie tidak ditemukan atau tidak bisa diklik: {e}")


    try:
        # Tunggu sampai elemen muncul
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "seo-directory-location-main-block"))
        )

        # Ambil semua elemen dengan class "seo-directory-location-main-block"
        blocks = browser.find_elements(By.CLASS_NAME, "seo-directory-location-main-block")

        urls = []  # List untuk menyimpan URL

        # Loop untuk menelusuri setiap blok dan mencari <a> di dalamnya
        for block in blocks:
            links = block.find_elements(By.TAG_NAME, "a")  # Cari semua elemen <a> dalam block
            for link in links:
                href = link.get_attribute("href")  # Ambil nilai href
                if href and href not in urls:
                    urls.append(href)  # Simpan URL ke list

        print(f"Ditemukan {len(urls)} URL, membuka halaman satu per satu...\n")

        for idx, url in enumerate(urls, start=1):
            time.sleep(5)  # Tunggu sebelum membuka halaman
            browser.get(url)  # Buka halaman URL
            time.sleep(5)  # Tunggu halaman dimuat

            print(f"=== Page {idx} - URL: {url} ===")


            try:
                # Tunggu sampai elemen pertama muncul
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "-mb-16.dl-layout-item.dl-layout-size-xs-12"))
                )

                # Ambil elemen "-mb-16 dl-layout-item dl-layout-size-xs-12"
                elements = browser.find_elements(By.CLASS_NAME, "-mb-16.dl-layout-item.dl-layout-size-xs-12")

                for el in elements:
                    text = el.text.strip()
                    if text:
                        print(f"Title: {text}")

            except Exception as e:
                print(f"❌ Data tidak ditemukan di halaman {idx}: {url}", e)

            try:
                # Tunggu elemen kedua ("md:col-span-3 responsive-doctor-border")
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "md\\:col-span-3.responsive-doctor-border"))
                )

                # # Ambil elemen "md:col-span-3 responsive-doctor-border"
                # doctor_info = browser.find_elements(By.CLASS_NAME, "md\\:col-span-3.responsive-doctor-border")

                # for info in doctor_info:
                #     text = info.text.strip()
                #     if text:
                #         print(f"Doctor Info: {text}")


                doctor_info = browser.find_elements(By.XPATH, "//div[contains(@class, 'responsive-doctor-border')]")

                for idx, doctor in enumerate(doctor_info, start=1):
                    try:
                        link_element = doctor.find_element(By.TAG_NAME, "a")
                        href = link_element.get_attribute("href")
                        print(f"Doctor {idx} - URL: {href}")

                    except Exception as e:
                        print(f"Doctor {idx} - Tidak ada link ditemukan: {e}")


            except Exception as e:
                print(f"❌ Doctor Info tidak ditemukan di halaman {idx}: {url}", e)

            print("\n" + "=" * 50 + "\n")  # Pembatas antar halaman

    except Exception as e:
        print("Elemen tidak ditemukan:", e)



def main():
    browser = setup_browser()
    open_to_website(browser)
    time.sleep(50)
    browser.quit()

if __name__ == "__main__":
    main()