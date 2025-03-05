from bs4 import BeautifulSoup
from prometheus_client import Counter

# 定义普罗米修斯指标
PARSE_SUCCESS = Counter('parser_success_total', 'Total number of successfully parsed jobs')
PARSE_FAILURE = Counter('parser_failures_total', 'Total number of failed parses')

def parse_internship_page(page_source):
    """
    解析实习页面数据
    :param page_source: 页面的HTML源代码
    :return: 解析后的实习信息列表
    """
    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        job_cards = soup.find_all('div', class_='job-card-item')
        internship_jobs = []

        for card in job_cards:
            try:
                job_name = card.find('span', class_='job-name').text.strip()
                job_salary = card.find('span', class_='job-salary').text.strip()
                company_name = card.find('span', class_='company-name').text.strip()
                company_info_items = card.find_all('div', class_='company-info-item')
                company_industry = company_info_items[0].text.strip() if company_info_items else ''
                company_scale = company_info_items[1].text.strip() if len(company_info_items) > 1 else ''

                job_info_items = card.find_all('div', class_='job-info-item')
                working_days = ''
                duration = ''
                other_info = []  # Initialize list for unclassified information
                for item in job_info_items:
                    text = item.get_text(strip=True)
                    if '天/周' in text:
                        working_days = text
                    elif '最少' in text:
                        duration = text
                    elif text and not any(key in text for key in ['助力简历加分', 'HR刚处理简历']):
                        other_info.append(text)  # Collect unclassified information

                description = ', '.join(other_info)  # Combine unclassified information

                job = {
                    'position': job_name,
                    'salary': job_salary,
                    'company': company_name,
                    'company_industry': company_industry,
                    'company_scale': company_scale,
                    'description': description,  # Use description instead of location
                    'working_days': working_days,
                    'duration': duration
                }
                internship_jobs.append(job)
                PARSE_SUCCESS.inc()  # 每成功解析一个岗位，增加一次
            except Exception as e:
                PARSE_FAILURE.inc()  # 解析单个岗位失败时增加
                print(f"Failed to parse a job card: {e}")

        return internship_jobs
    except Exception as e:
        PARSE_FAILURE.inc()  # 整个页面解析失败时增加
        raise e

def parse_fulltime_page(page_source):
    """
    解析社招页面数据
    :param page_source: 页面的HTML源代码
    :return: 解析后的社招信息列表
    """
    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        job_cards = soup.find_all('div', class_='job-card-item')
        fulltime_jobs = []

        for card in job_cards:
            try:
                job_name = card.find('span', class_='job-name').text.strip()
                job_salary = card.find('span', class_='job-salary').text.strip()
                company_name = card.find('span', class_='company-name').text.strip()
                company_info_items = card.find_all('div', class_='company-info-item')
                company_industry = company_info_items[0].text.strip() if company_info_items else ''
                company_scale = company_info_items[1].text.strip() if len(company_info_items) > 1 else ''

                job_info_items = card.find_all('div', class_='job-info-item')
                experience = ''
                education = ''
                job_tags = []
                other_info = []  # Initialize list for unclassified information
                for item in job_info_items:
                    text = item.get_text(strip=True)
                    if '年' in text:
                        experience = text
                    elif '专科' in text or '本科' in text:
                        education = text
                    elif text:
                        job_tags.append(text)
                        other_info.append(text)  # Collect unclassified information

                description = ', '.join(other_info)  # Combine unclassified information

                job = {
                    'position': job_name,
                    'salary': job_salary,
                    'company': company_name,
                    'company_industry': company_industry,
                    'company_scale': company_scale,
                    'description': description,  # Use description instead of location
                    'experience': experience,
                    'degree': education,
                    #'job_tags': job_tags
                }
                fulltime_jobs.append(job)
                PARSE_SUCCESS.inc()  # 每成功解析一个岗位，增加一次
            except Exception as e:
                PARSE_FAILURE.inc()  # 解析单个岗位失败时增加
                print(f"Failed to parse a job card: {e}")

        return fulltime_jobs
    except Exception as e:
        PARSE_FAILURE.inc()  # 整个页面解析失败时增加
        raise e

def parse_school_recruitment_page(page_source):
    """
    解析校招页面数据
    :param page_source: 页面的HTML源代码
    :return: 解析后的校招信息列表
    """
    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        job_cards = soup.find_all('div', class_='job-card-item')
        school_recruitment_jobs = []

        for card in job_cards:
            try:
                job_name = card.find('span', class_='job-name').text.strip()
                job_salary = card.find('span', class_='job-salary').text.strip()
                company_name = card.find('span', class_='company-name').text.strip()
                company_info_items = card.find_all('div', class_='company-info-item')
                company_industry = company_info_items[0].text.strip() if company_info_items else ''
                company_scale = company_info_items[1].text.strip() if len(company_info_items) > 1 else ''

                job_info_items = card.find_all('div', class_='job-info-item')
                graduation_requirement = ''
                education = ''
                other_info = []  # Initialize list for unclassified information
                for item in job_info_items:
                    text = item.get_text(strip=True)
                    if '毕业不限' in text:
                        graduation_requirement = text
                    elif '专科' in text or '本科' in text:
                        education = text
                    elif text and 'HR刚处理简历' not in text:
                        other_info.append(text)  # Collect unclassified information

                description = ', '.join(other_info)  # Combine unclassified information

                job = {
                    'position': job_name,
                    'salary': job_salary,
                    'company': company_name,
                    'company_industry': company_industry,
                    'company_scale': company_scale,
                    'description': description,  # Use description instead of location
                    'graduation_requirement': graduation_requirement,
                    'degree': education
                }
                school_recruitment_jobs.append(job)
                PARSE_SUCCESS.inc()  # 每成功解析一个岗位，增加一次
            except Exception as e:
                PARSE_FAILURE.inc()  # 解析单个岗位失败时增加
                print(f"Failed to parse a job card: {e}")

        return school_recruitment_jobs
    except Exception as e:
        PARSE_FAILURE.inc()  # 整个页面解析失败时增加
        raise e

def parse_page(page_type, page_source):
    """
    根据页面类型调用相应的解析函数
    :param page_type: 页面类型，如 'school_recruitment', 'intern_recruitment', 'fulltime_recruitment'
    :param page_source: 页面的HTML源代码
    :return: 解析后的求职信息列表
    """
    try:
        if page_type == 'school_recruitment':
            return parse_school_recruitment_page(page_source)
        elif page_type == 'intern_recruitment':
            return parse_internship_page(page_source)
        elif page_type == 'fulltime_recruitment':
            return parse_fulltime_page(page_source)
        else:
            return []
    except Exception as e:
        PARSE_FAILURE.inc()  # 整个页面解析失败时增加
        raise e
