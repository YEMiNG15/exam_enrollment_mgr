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


def input_text(msg):
    """
    获取用户输入的非空字符串
    :param msg: str 提示信息
    :return: str 用户输入的非空字符串
    """
    i = input(msg)
    while i.strip() == '':
        e_print("不能为空")
        i = input(msg)
    return i


def init_db():
    """
    初始化数据库，创建表并插入一些示例数据
    :return: None
    """
    global Base, engine, session
    Base.metadata.create_all(engine)
    exam_0 = Exam(title='Python Exam', date=datetime.date(2021, 1, 1), location = 'Online')
    exam_1 = Exam(title='Java Exam', date=datetime.date(2021, 1, 2), location='W2301')
    candidate_0 = Candidate(name='张三', phone_number='19518114514',
                            registered_date=datetime.date(2021, 1, 1))
    candidate_1 = Candidate(name='李四', phone_number='19511114514',
                            registered_date=datetime.date(2021, 1, 2))
    candidate_2 = Candidate(name='王五', phone_number='19513114514',
                            registered_date=datetime.date(2021, 1, 3))
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
    :return: list 只包含一个对象
    """
    print("从如下的结果中选择一个:")
    for i, obj in enumerate(obj_list):
        print(f"{i+1}. {obj}")
    return obj_list[int(input("选择: ")) - 1]


def query_str_to_dict(query_str):
    """
    将查询字符串转换为字典
    :param query_str: 查询字符串，格式为"字段1=值1,字段2=值2,..."
    :return: dict 查询字典，格式为{"字段1": "值1", "字段2": "值2", ...}
    """
    return {msg[0]: msg[1] for msg in [msg.split('=') for msg in query_str.split(',')]}


def sole_result(func):
    """
    修饰器，使得函数只返回用户选择的对象
    :param func: 返回由若干个对象组成的列表的函数
    :return: func 返回一个只包含一个对象的列表的函数
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
def search_obj(obj_class, search_str, verbose=True):
    """
    搜索对象
    :param obj_class: 要查询的对象类，可以从Candidate, Exam, Registration中选择
    :param search_str: 查询字符串，格式为"字段1=值1,字段2=值2,..."
    :param verbose: 是否打印错误信息
    :return: list 查询结果，为对象列表
    """
    global session
    query_dict = query_str_to_dict(search_str)
    query = session.query(obj_class)
    if not all([field in obj_class.ALLOWED_SEARCH_FIELDS for field in query_dict.keys()]):
        if verbose:
            e_print("不合法的查询字段")
        results = []
    else:
        for field, value in query_dict.items():
            query = query.filter(getattr(obj_class, field).like(f"%{value}%"))
        else:
            results = query.all()
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
    :param obj_class: 要添加的对象类，可以从Candidate, Exam中选择
    :param query_str: 查询字符串，格式为"字段1=值1,字段2=值2,..."
    :return: bool 添加是否成功
    """
    global session
    query_dict = query_str_to_dict(query_str)
    required_fields = obj_class.REQUIRED_FIELDS
    optional_fields = obj_class.OPTIONAL_FIELDS
    if not all([field in required_fields + optional_fields for field in query_dict.keys()]):
        e_print("不合法的字段")
        return False
    if not all([field in query_dict.keys() for field in required_fields]):
        e_print("缺少必要字段")
        return False
    try:
        new_obj = obj_class(**query_dict)
    except Exception as e:
        e_print(f"未知错误: {e}")
        return False
    try:
        session.add(new_obj)
        session.commit()
    except Exception as e:
        e_print(f"数据库错误: {e}")
        session.rollback()
        return False
    return True


def update_obj(obj_class, query_str_0, query_str_1, verbose=True):
    """
    更新对象
    :param obj_class: 要更新的对象类，可以从Candidate, Exam, Registration中选择
    :param query_str_0: 查询字符串，格式为"字段1=值1,字段2=值2,..."，用于查询要更新的对象
    :param query_str_1: 查询字符串，格式为"字段1=值1,字段2=值2,..."，用于更新对象
    :param verbose: 是否打印错误信息
    :return: bool 更新是否成功
    """
    global session
    query_dict_0 = query_str_to_dict(query_str_0)
    query_dict_1 = query_str_to_dict(query_str_1)
    if not all([field in obj_class.ALLOWED_SEARCH_FIELDS for field in query_dict_0.keys()]):
        if verbose:
            e_print("不合法的查询字段")
        return False
    if not all([field in obj_class.ALLOWED_MODIFY_FIELDS for field in query_dict_1.keys()]):
        if verbose:
            e_print("不合法的修改字段")
        return False
    obj = search_obj(obj_class, query_str_0, verbose=verbose)
    if not obj:
        if verbose:
            e_print("找不到对应的对象")
        return False
    for field, value in query_dict_1.items():
        setattr(obj[0], field, value)
    try:
        session.add(obj[0])
        session.commit()
    except Exception as e:
        e_print(f"数据库错误: {e}")
        session.rollback()
        return False
    else:
        return True


def add_registration(query_str):
    """
    添加报名，因为报名对象的创建需要考生和考试对象，所以需要先确认考生和考试对象是否存在
    :param query_str: 查询字符串，格式为"字段1=值1,字段2=值2,..."
    :return: bool 添加是否成功
    """
    global session
    query_dict = query_str_to_dict(query_str)
    if not all([field in Registration.REQUIRED_FIELDS + Registration.OPTIONAL_FIELDS for field in query_dict.keys()]):
        e_print("不合法的字段")
        return False
    if not all([field in query_dict.keys() for field in Registration.REQUIRED_FIELDS]):
        e_print("缺少必要字段")
        return False
    candidate = search_candidate(f"id={query_dict['candidate_id']}", v=False)
    exam = search_exam(f"id={query_dict['exam_id']}", v=False)
    if not candidate or not exam:
        e_print("找不到对应的考生或考试")
        return False
    try:
        new_registration = Registration(**query_dict)
    except Exception as e:
        e_print(f"未知错误: {e}")
        return False
    try:
        session.add(new_registration)
        session.commit()
    except Exception as e:
        e_print(f"数据库错误: {e}")
        session.rollback()
        return False
    return True


search_candidate = lambda s, v=True: search_obj(Candidate, s, v)
search_exam = lambda s, v=True: search_obj(Exam, s, v)
search_registration = lambda s, v=True: search_obj(Registration, s, v)
list_candidates = lambda: list_obj(Candidate)
list_exams = lambda: list_obj(Exam)
list_registrations = lambda: list_obj(Registration)
add_candidate = lambda x: add_obj(Candidate, x)
add_exam = lambda x: add_obj(Exam, x)
update_candidate = lambda q_1, q_2, v=True: update_obj(Candidate, q_1, q_2, v)
update_exam = lambda q_1, q_2, v=True: update_obj(Exam, q_1, q_2, v)
update_registration = lambda q_1, q_2, v=True: update_obj(Registration, q_1, q_2, v)


if __name__ == '__main__':
    def test():
        list_candidates()
        update_candidate("id=1", "name=哈哈哈")
        list_candidates()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    if not os.path.exists(DATABASE_PATH):
        # 若数据库文件不存在，则初始化数据库
        init_db()
    test()
    session.close()
    # Base.metadata.drop_all(engine)
