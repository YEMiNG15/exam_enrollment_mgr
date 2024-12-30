import os


# 数据库文件路径默认为脚本所在目录下的database.sqlite
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
DATETIME_STR_FORMAT = "%Y-%m-%d_%H:%M:%S"
DATE_STR_FORMAT = "%Y-%m-%d"
TRANSLATION = {
    'name': '姓名',
    'phone_number': '电话号码',
    'registered_date': '注册日期',
    'title': '考试名称',
    'date': '考试日期',
    'location': '考试地点',
    'registration_date': '报名日期',
    'candidate_id': '考生ID',
    'exam_id': '考试ID',
    'Candidate': '考生',
    'Exam': '考试',
    'Registration': '报名记录'
}
