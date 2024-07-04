from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

def setup_driver():
    """設定並返回Chrome WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 無頭模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def fetch_page(driver, url):
    """訪問指定的URL並返回BeautifulSoup解析的頁面內容"""
    driver.get(url)
    time.sleep(5)  # 等待頁面加載
    return BeautifulSoup(driver.page_source, 'html.parser')

def parse_jobs(soup):
    """解析頁面內容並返回職位信息的列表，包括薪水"""
    jobs = soup.find_all('div', class_='job-item')
    job_list = []
    for job in jobs:
        try:
            title = job.find('h3', class_='job-title').text.strip()
            company = job.find('div', class_='company-name').text.strip()
            location = job.find('span', class_='location').text.strip()
            salary = job.find('span', class_='salary').text.strip() if job.find('span', class_='salary') else 'N/A'
            job_list.append([title, company, location, salary])
        except AttributeError as e:
            print(f"Error parsing job: {e}")
            continue
    return job_list

def save_to_csv(job_list, filename='cakeresume_list.csv'):
    """將職位資訊保存到CSV文件"""
    df = pd.DataFrame(job_list, columns=['Title', 'Company', 'Location', 'Salary'])
    df.to_csv(filename, index=False, encoding='utf-8-sig')

def main():
    url = "https://www.cakeresume.com/jobs?location_list%5B0%5D=%E5%8F%B0%E5%8C%97%E5%B8%82%2C%20%E5%8F%B0%E7%81%A3&location_list%5B1%5D=%E6%96%B0%E5%8C%97%E5%B8%82%2C%20%E5%8F%B0%E7%81%A3&location_list%5B2%5D=%E6%96%B0%E7%AB%B9%E5%B8%82%2C%20%E5%8F%B0%E7%81%A3&profession%5B0%5D=it"
    driver = setup_driver()
    try:
        soup = fetch_page(driver, url)
        job_list = parse_jobs(soup)
        save_to_csv(job_list)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()