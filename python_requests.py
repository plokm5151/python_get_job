import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

def get_job_data():
    base_url = 'https://www.104.com.tw/jobs/search/'
    params = {
        'ro': '1',
        'jobcat': '2007000000',
        'expansionType': 'area,spec,com,job,wf,wktm',
        'area': '6001001000,6001002000,6001006000',
        'order': '17',
        'asc': '0',
        'mode': 's',
        'jobsource': 'index_s',
        'langFlag': '0',
        'langStatus': '0',
        'recommendJob': '1',
        'hotJob': '1',
        'page': '1'
    }

    res = requests.get(base_url, params=params)
    soup = BeautifulSoup(res.text, "html.parser")
    page = 1

    job_list = []

    while page <= 20:  # Limit to first 20 pages
        for job in soup.find_all('article', class_="b-block--top-bord job-list-item b-clearfix js-job-item"):
            job_data = {}
            job_data["職缺名稱"] = job['data-job-name']  # Job Title
            job_data["職缺連結"] = 'https:' + job.a['href']  # Job Link
            job_data["公司名稱"] = job['data-cust-name']  # Company Name
            job_data["工作地區"] = job.select('ul.b-list-inline.b-clearfix.job-list-intro.b-content li')[0].text  # Job Location
            
            salary_info = job.find('div', class_="job-list-tag b-content")

            # Handle salary information
            if salary_info.select('span') and salary_info.span.text == "待遇面議":
                e = salary_info.span.text
            else:
                e = salary_info.a.text
            
            job_data["薪資待遇"] = e
            job_data["計薪方式"] = e[:2]  # Payment Method
            salary = ''
            for char in e:
                if char.isdigit() or char == '~':
                    salary += char
            
            if '~' in salary:
                low_salary = salary[:salary.find('~')]
                high_salary = salary[salary.find('~') + 1:]
            else:
                low_salary = salary
                high_salary = ''  # Default value if no '~' symbol
            
            job_data["薪資下限"] = int(low_salary) if low_salary.isdigit() else 40000
            job_data["薪資上限"] = int(high_salary) if high_salary.isdigit() else 40000

            job_list.append(job_data)
        
        page += 1
        params['page'] = str(page)
        res = requests.get(base_url, params=params)
        soup = BeautifulSoup(res.text, "html.parser")

    return job_list

def analyze_job_data(job_list):
    df = pd.DataFrame(job_list)
    total_jobs = len(df)
    max_salary = df["薪資上限"].max()
    min_salary = df["薪資下限"].min()
    avg_salary = df[["薪資下限", "薪資上限"]].mean().mean()

    return total_jobs, max_salary, min_salary, avg_salary

def save_to_excel(df, filename):
    if not os.path.exists(filename):
        wb = Workbook()
        ws = wb.active
        ws.title = "104職缺資料"
        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)
        wb.save(filename)
    else:
        with pd.ExcelWriter(filename, mode='a', if_sheet_exists='new') as writer:
            df.to_excel(writer, sheet_name='104職缺資料', index=False)

if __name__ == "__main__":
    job_list = get_job_data()

    total_jobs, max_salary, min_salary, avg_salary = analyze_job_data(job_list)
    
    # Notify data scraping completion
    print("Data scraping completed")

    # User input options
    #user_input = input("Enter option (1: Print data, 2: Save to Excel): ")

    current_date = datetime.now().strftime("%Y-%m-%d")

    print(f"Execution Date: {current_date}")
    print(f"Total Jobs: {total_jobs}")
    print(f"Highest Salary: {max_salary}")
    print(f"Lowest Salary: {min_salary}")

    df = pd.DataFrame(job_list)
    filename = f"{current_date}_104_job_data.xlsx"
    save_to_excel(df, filename)
    print(f"Data saved to {filename}")
