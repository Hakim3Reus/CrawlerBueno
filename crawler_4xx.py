import csv
import time
from urllib.parse import urljoin, urlparse

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

visited = set()
errors = []

def is_valid_url(url, base_netloc):
    parsed = urlparse(url)
    return parsed.netloc == base_netloc or parsed.netloc == ''

def check_url_status(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if 400 <= response.status_code < 500:
            return response.status_code
    except requests.RequestException:
        return 499 
    return None

def crawl(driver, base_url, current_url):
    if current_url in visited:
        return
    visited.add(current_url)

    try:
        driver.get(current_url)
        time.sleep(1)  # TIEMPO PARA EVITAR BLOQUEOS 

        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue

            absolute_url = urljoin(current_url, href)

            if is_valid_url(absolute_url, urlparse(base_url).netloc):
                status = check_url_status(absolute_url)
                if status:
                    errors.append({
                        "error_url": absolute_url,
                        "status_code": status,
                        "origin_page": current_url
                    })
                if absolute_url not in visited:
                    crawl(driver, base_url, absolute_url)
    except Exception as e:
        print(f"Error accedint a {current_url}: {e}")

def save_report(filepath="informe_errors.csv"):
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["error_url", "status_code", "origin_page"])
        writer.writeheader()
        for err in errors:
            writer.writerow(err)

def main():
    start_url = "https://www.vidalibarraquer.net"  # URL DE LA PAGIONA
    driver = webdriver.Chrome()  
    try:
        crawl(driver, start_url, start_url)
    finally:
        driver.quit()
        save_report()
        print(f"Informe generat amb {len(errors)} errors 4XX.")
    
if __name__ == "__main__":
    main()
