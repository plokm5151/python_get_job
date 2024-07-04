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
    jobs = soup.find_all('article', class_='js-job-item')
    job_list = []
    for job in jobs:
        try:
            title = job.find('a', class_='js-job-link').text.strip()
            company = job.get('data-cust-name')
            location = job.find('ul', class_='b-list-inline b-clearfix job-list-intro b-content').find_all('li')[0].text.strip()
            salary = job.find('span', class_='b-tag--default').text.strip() if job.find('span', class_='b-tag--default') else 'N/A'
            job_list.append([title, company, location, salary])
        except AttributeError as e:
            print(f"Error parsing job: {e}")
            continue
    return job_list

def save_to_csv(job_list, filename='job_list.csv'):
    """將職位信息保存到CSV文件"""
    df = pd.DataFrame(job_list, columns=['Title', 'Company', 'Location', 'Salary'])
    df.to_csv(filename, index=False, encoding='utf-8-sig')

def main():
    url = "https://www.104.com.tw/jobs/search/?ro=0&jobcat=2007000000&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&area=6001001000%2C6001002000%2C6001006000&order=17&asc=0&page=4&mode=s&jobsource=index_s&langFlag=0&langStatus=0&recommendJob=1&hotJob=1"
    driver = setup_driver()
    try:
        soup = fetch_page(driver, url)
        job_list = parse_jobs(soup)
        save_to_csv(job_list)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
