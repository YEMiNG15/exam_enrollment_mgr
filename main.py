from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import wraps
from models import Candidate, Exam, Registration
from constants import DATABASE_URL, DATABASE_PATH, TRANSLATION
import models
import os
import datetime


e_print = lambda x: print(f"[ERROR] {x}")
Base = models.Base


def init_db():
    """
    初始化数据库，创建表并插入一些示例数据
    :return: None
    """
    global Base, engine, session
    Base.metadata.create_all(engine)
    exam_0 = Exam(title='Python Exam', date=datetime.date(2021, 1, 1),
                  location = 'Online', max_candidates = 100)
    exam_1 = Exam(title='Java Exam', date=datetime.date(2021, 1, 2),
                  location='W2301', max_candidates=100)
    candidate_0 = Candidate(name='Alice', phone_number='1234567890',
                            registered_date=datetime.date(2021, 1, 1))
    candidate_1 = Candidate(name='Bob', phone_number='1234567891',
                            registered_date=datetime.date(2021, 1, 2))
    candidate_2 = Candidate(name='Alice', phone_number='1234567893',
                            registered_date=datetime.date(2021, 1, 1))
    session.add(exam_0)
    session.add(exam_1)
    session.add(candidate_0)
    session.add(candidate_1)
    session.add(candidate_2)
    session.commit()


def candidate_submenu():
    print("1. 添加考生")
    print("2. 列出所有考生")
    print("3. 查询考生")
    print("4. 更新考生信息")
    print("5. 删除考生")
    print("6. 回退到主菜单")
    print("7. 退出程序")
    return input("选择你要进行的操作: ")


    def __repr__(self):
        return f"<Candidate {self.name}-{self.phone_number}-{self.registered_date}>"


def exam_submenu():
    print("1. 添加考试")
    print("2. 列出所有考试")
    print("3. 查询考试")
    print("4. 更新考试信息")
    print("5. 删除考试")
    print("6. 回退到主菜单")
    print("7. 退出程序")
    return input("选择你要进行的操作: ")


def registration_submenu():
    print("1. 添加报名")
    print("2. 列出所有报名")
    print("3. 查询报名")
    print("4. 更新报名信息")
    print("5. 删除报名")
    print("6. 回退到主菜单")
    print("7. 退出程序")
    return input("选择你要进行的操作: ")


def select_object(obj_list):
    """
    从对象列表中选择一个对象
    :param obj_list: 对象列表
    :return: 选择的对象
    """
    print("从如下的结果中选择一个:")
    for i, obj in enumerate(obj_list):
        print(f"{i+1}. {obj}")
    return obj_list[int(input("选择: ")) - 1]


def query_str_to_dict(query_str):
    """
    将查询字符串转换为字典
    :param query_str: 查询字符串，格式为"字段1=值1,字段2=值2,..."
    :return: 查询字典，格式为{"字段1": "值1", "字段2": "值2", ...}
    """
    return {msg[0]: msg[1] for msg in [msg.split('=') for msg in query_str.split(',')]}


def sole_result(func):
    """
    修饰器，使得函数只返回用户选择的对象
    :param func: 返回由若干个对象组成的列表的函数
    :return: 返回一个只包含一个对象的列表的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        results = func(*args, **kwargs)
        if len(results) > 1:
            return [select_object(results)]
        else:
            return results
    return wrapper


@sole_result
def search_obj(obj_class, search_str):
    """
    搜索对象
    :param obj_class: 要查询的对象类，可以从Candidate, Exam, Registration中选择
    :param search_str: 查询字符串，格式为"字段1=值1,字段2=值2,..."
    :return: 查询结果，为对象列表
    """
    global session
    query_dict = query_str_to_dict(search_str)
    if not all([field in obj_class.ALLOWED_SEARCH_FIELDS for field in query_dict.keys()]):
        e_print("不合法的查询字段")
        return []
    else:
        results = session.query(obj_class).filter_by(**query_dict).all()
        return results


def list_obj(obj_class):
    """
    列出所有对象
    :param obj_class: 要列出的对象类，可以从Candidate, Exam, Registration中选择
    :return: None
    """
    global session
    results = session.query(obj_class).all()
    print(f"{TRANSLATION[obj_class.__name__]}列表:")
    for i in range(len(results)):
        print(f"{i+1}. {results[i]}")


def add_obj(obj_class, query_str):
    """
    添加对象
    :param obj_class: 要添加的对象类，可以从Candidate, Exam, Registration中选择
    :param query_str: 查询字符串，格式为"字段1=值1,字段2=值2,..."
    :return: None
    """
    global session
    query_dict = query_str_to_dict(query_str)
    new_obj = obj_class(**query_dict)
    session.add(new_obj)
    session.commit()
    print(f"成功添加{TRANSLATION[obj_class.__name__]}: {new_obj}")


search_candidate = lambda x: search_obj(Candidate, x)
search_exam = lambda x: search_obj(Exam, x)
search_registration = lambda x: search_obj(Registration, x)
list_candidates = lambda: list_obj(Candidate)
list_exams = lambda: list_obj(Exam)
list_registrations = lambda: list_obj(Registration)


if __name__ == '__main__':
    def test():
        print(search_candidate('name=Alice'))
        print(search_exam('title=Python Exam'))
        list_exams()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    if not os.path.exists(DATABASE_PATH):
        # 若数据库文件不存在，则初始化数据库
        init_db()
    test()
    session.close()
    # Base.metadata.drop_all(engine)
