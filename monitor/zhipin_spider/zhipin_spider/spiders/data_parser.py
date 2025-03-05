import json
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from prometheus_client import Counter

# 定义监控指标
JOBS_PARSED = Counter('zhipin_jobs_parsed', 'Total number of jobs parsed')#职位解析
JOBS_PARSE_FAILED = Counter('zhipin_jobs_parse_failed', 'Total number of jobs failed to parse')
#职位解析失败率

class NewDataParser:
    def __init__(self, file_path='new_jobs.json'):
        self.file_path = file_path

    def parse_and_store(self, job: WebElement):
        try:
            item = self.parse_job(job)
            print(item)  # 打印岗位信息
            self.store_data(item)
            JOBS_PARSED.inc()
            return item
        except Exception as e:
            # 解析失败，增加失败解析数量的指标计数
            JOBS_PARSE_FAILED.inc()
            
        


        

    def parse_job(self, job: WebElement) -> dict:
        """解析单个职位信息"""
        try:
            position = job.find_element_by_css_selector('.job-name').text
        except:
            position = ""
        try:
            company = WebDriverWait(job, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.company-name > a'))
            ).text
        except:
            company = ""
        try:
            city = WebDriverWait(job, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.job-area-wrapper >.job-area'))
            ).text
        except:
            city = ""
        try:
            salary = job.find_element_by_css_selector('.salary').text
        except:
            salary = ""
        try:
            experience_li = job.find_elements_by_css_selector('.tag-list > li')
            if experience_li:
                experience_text = experience_li[0].text
                experience = experience_text
                if '天/周' in experience_text or '天/月' in experience_text:
                    jobType = "实习生"
                else:
                    jobType = "正式员工"
            else:
                experience = ""
                jobType = ""
        except:
            experience = ""
            jobType = ""
        try:
            degree = job.find_elements_by_css_selector('.tag-list > li')[1].text if len(job.find_elements_by_css_selector('.tag-list > li')) > 1 else ""
        except:
            degree = ""
        try:
            company_size_li = job.find_elements_by_css_selector('.company-tag-list > li')
            for li in company_size_li:
                if '人' in li.text:
                    companySize = li.text
                    break
            else:
                companySize = ""
        except:
            companySize = ""

        return {
            "position": position,
            "company": company,
            "city": city,
            "salary": salary,
            "experience": experience,
            "degree": degree,
            "companySize": companySize,
            "jobType": jobType
        }

    def store_data(self, item: dict):
        """将解析的数据存储到文件"""
        with open(self.file_path, 'a', encoding='utf-8') as file:
            json.dump(item, file, ensure_ascii=False)
            file.write('\n')
