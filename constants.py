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
SUBMENUS = {
    'main': ['考生管理', '考试管理', '报名管理', '重置数据库', '退出程序'],
    'Candidate': ['添加考生', '列出所有考生', '查询考生', '更新考生信息', '删除考生', '帮助', '回退到主菜单', '退出程序'],
    'Exam': ['添加考试', '列出所有考试', '查询考试', '更新考试信息', '删除考试', '帮助', '回退到主菜单', '退出程序'],
    'Registration': ['添加报名', '列出所有报名', '查询报名', '更新报名信息', '删除报名', '帮助', '回退到主菜单', '退出程序']
}
HELP_DOC = {
    'Candidate': """
    对考生进行增删改查操作，字符串格式要求为"字段1=值1,字段2=值2,..."。
    对于添加操作，允许的字段有name(姓名), phone_number(电话号码)，registered_date_str(注册日期)，其中name和phone_number为必填字段。
    对于查询和删除操作，允许的字段有id(考生ID), name(姓名), phone_number(电话号码)。
    对于更新操作，允许的字段有name(姓名), phone_number(电话号码)，registered_date_str(注册日期)。
    registered_date_str的格式为"YYYY-MM-DD_HH:MM:SS"。
    """,
    'Exam': """
    对考试进行增删改查操作，字符串格式要求为"字段1=值1,字段2=值2,..."。
    对于添加操作，允许的字段有title(考试名称), location(考试地点)，date_str(考试日期)，其中title和location为必填字段。
    对于查询和删除操作，允许的字段有id(考试ID), title(考试名称), location(考试地点)。
    对于更新操作，允许的字段有title(考试名称), location(考试地点)，date_str(考试日期)。
    date_str的格式为"YYYY-MM-DD"。
    """,
    'Registration': """
    对报名记录进行增删改查操作，字符串格式要求为"字段1=值1,字段2=值2,..."。
    对于添加操作，需要提供考生和考试的查询字符串，参考考生和考试的查询字符串格式。
    对于查询和删除操作，允许的字段有id(报名ID), candidate_id(考生ID), exam_id(考试ID)。
    对于更新操作，允许的字段有registration_date_str(报名日期)。
    registration_date_str的格式为"YYYY-MM-DD_HH:MM:SS"。
    """
}
