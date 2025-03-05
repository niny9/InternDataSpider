from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# 读取JSON文件
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# 合并JSON数据
def merge_json(file_paths):
    merged_data = []
    for file_path in file_paths:
        data = load_json(file_path)
        merged_data.extend(data)
    return merged_data

# 保存合并后的JSON数据
def save_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 主程序
if __name__ == "__main__":
    file_paths = [
        'fulltime_recruitment_jobs.json',
        'intern_recruitment_jobs.json',
        'school_recruitment_jobs.json'
    ]
    output_file = 'merged_jobs.json'

    merged_data = merge_json(file_paths)
    save_json(merged_data, output_file)

    print(f"合并完成，结果已保存到 {output_file}")

# 加载本地数据
def load_jobs():
    with open('merged_jobs.json', 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    return jobs

# 根据查询条件过滤岗位信息
def filter_jobs(job_name, description, company_industry, company_scale, job_salary, job_type, graduation_year, degree, experience, education, working_days, duration, jobs):
    filtered_jobs = []

    for job in jobs:
        # 根据岗位名称进行过滤
        if job_name and job_name.lower() not in job.get('position', '').lower():
            continue

        # 根据岗位描述进行过滤
        if description and description.lower() not in job.get('description', '').lower():
            continue

        # 根据公司行业进行过滤
        if company_industry and company_industry.lower() not in job.get('company_industry', '').lower():
            continue

        # 根据公司规模进行过滤
        if company_scale and company_scale.lower() not in job.get('company_scale', '').lower():
            continue

        # 根据薪资待遇进行过滤
        if job_salary and job_salary.lower() not in job.get('salary', '').lower():
            continue

        # 根据职位类型进行过滤
        if job_type and job_type not in job.get('page_type', ''):
            continue

        # 根据毕业年份进行过滤（校招）
        if graduation_year and graduation_year not in job.get('graduation_requirement', ''):
            continue

        # 根据学历要求进行过滤（校招）
        if degree and degree not in job.get('degree', ''):
            continue

        # 根据工作经验进行过滤（社招）
        if experience and experience not in job.get('experience', ''):
            continue

        # 根据教育程度进行过滤（社招）
        if education and education not in job.get('degree', ''):
            continue

        # 根据每周工作天数进行过滤（实习）
        if working_days and working_days.lower() not in job.get('working_days', '').lower():
            continue

        # 根据实习时长进行过滤（实习）
        if duration and duration not in job.get('duration', ''):
            continue

        filtered_jobs.append(job)

    return filtered_jobs

@app.route('/api/search', methods=['GET'])
def search_jobs():
    job_name = request.args.get('jobName', '').strip().lower()
    description = request.args.get('description', '').strip().lower()
    company_industry = request.args.get('company_industry', '').strip().lower()
    company_scale = request.args.get('company_Scale', '').strip().lower()
    job_salary = request.args.get('salary', '').strip().lower()
    job_type = request.args.get('jobType', '').strip().lower()
    graduation_year = request.args.get('graduationYear', '').strip()
    degree = request.args.get('degree', '').strip()
    experience = request.args.get('experience', '').strip()
    education = request.args.get('education', '').strip()
    working_days = request.args.get('workingDays', '').strip().lower()
    duration = request.args.get('duration', '').strip().lower()

    jobs = load_jobs()

    # 根据条件过滤岗位
    filtered_jobs = filter_jobs(job_name, description, company_industry, company_scale, job_salary, job_type, graduation_year, degree, experience, education, working_days, duration, jobs)

    return jsonify(filtered_jobs)

if __name__ == '__main__':
    app.run(debug=True)

