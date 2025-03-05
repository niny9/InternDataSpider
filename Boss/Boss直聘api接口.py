from flask import Flask, request, jsonify
import json
import re
from urllib.parse import unquote
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# 加载本地 JSON 数据
def load_jobs():
    with open('F:/monitor+mysql/Boss/new_jobs.json', 'r', encoding='utf-8') as f:
        jobs = [json.loads(line) for line in f]
    return jobs


# 提取薪资数字部分并计算中位数
def get_salary_value(salary_str):
    # 去除薪资字符串中的任何附加信息（例如 “·14薪”）
    salary_str = re.sub(r'·.*$', '', salary_str)  # 去除“·14薪”或类似附加信息
    salary_str = salary_str.replace('K', '').strip()  # 去掉“K”并去除空格
    salary_range = salary_str.split('-')  # 如果是区间形式，按"-"拆分
    if len(salary_range) == 2:
        # 计算薪资区间的中位数
        try:
            min_salary = int(salary_range[0].strip()) * 1000
            max_salary = int(salary_range[1].strip()) * 1000
            return (min_salary + max_salary) // 2  # 返回中位数
        except ValueError:
            return None
    elif len(salary_range) == 1:
        # 处理单个薪资数值
        try:
            return int(salary_range[0].strip()) * 1000
        except ValueError:
            return None
    return None


# 根据查询条件过滤岗位信息
def filter_jobs(position, city, experience, degree, salary, companySize, jobType, jobs):
    filtered_jobs = []

    for job in jobs:
        # 转换为小写进行部分匹配
        job_position = job['position'].lower()
        job_city = job['city'].lower()
        job_experience = job['experience'].lower()
        job_degree = job['degree'].lower()
        job_salary = job['salary']
        job_companySize = job['companySize'].lower()
        job_jobType = job['jobType'].lower()

        # 去除前端传递的薪资范围中的单位（如“K”）
        salary_range = salary.replace('K', '').strip()
        salary_values = salary_range.split('-')

        salary_min = get_salary_value(salary_values[0]) if salary else None
        salary_max = get_salary_value(salary_values[1]) if len(salary_values) > 1 else salary_min

        # 处理岗位的薪资
        salary_value = get_salary_value(job_salary)

        if salary_value and (salary_min <= salary_value <= salary_max if salary_min and salary_max else True):
            salary_match = True
        else:
            salary_match = False

        # 对比条件进行筛选
        if (not position or position in job_position) and \
                (not city or city in job_city) and \
                (not experience or experience == job_experience) and \
                (not degree or degree == job_degree) and \
                (not companySize or companySize == job_companySize) and \
                (not jobType or jobType == job_jobType) and \
                salary_match:
            filtered_jobs.append(job)

    return filtered_jobs


@app.route('/api/search', methods=['GET'])
def search_jobs():
    # 获取前端传来的查询参数
    position = unquote(request.args.get('position', '').strip().lower())
    city = unquote(request.args.get('city', '').strip().lower())
    experience = unquote(request.args.get('experience', '').strip().lower())
    degree = unquote(request.args.get('degree', '').strip().lower())
    salary = unquote(request.args.get('salary', '').strip())
    companySize = unquote(request.args.get('companySize', '').strip().lower())
    jobType = unquote(request.args.get('jobType', '').strip().lower())

    print(
        f"Received parameters: position={position}, city={city}, salary={salary}, experience={experience}, degree={degree}, companySize={companySize}, jobType={jobType}")

    # 加载本地 JSON 数据
    jobs = load_jobs()

    # 根据查询条件过滤岗位信息
    filtered_jobs = filter_jobs(position,city,experience,degree,salary,companySize,jobType,jobs)

    # 返回过滤后的岗位信息
    return jsonify(filtered_jobs)

if __name__ == '__main__':
    app.run(debug=True)




