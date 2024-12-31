from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import wraps
from models import Candidate, Exam, Registration
from constants import DATABASE_URL, DATABASE_PATH, TRANSLATION, SUBMENUS, HELP_DOC
import models
import os
import datetime


e_print = lambda x: print(f"[ERROR] {x}")
Base = models.Base
choice_map = {
    '1': Candidate,
    '2': Exam,
    '3': Registration
}


def input_text(msg):
    """
    获取用户输入的非空字符串
    :param msg: str 提示信息
    :return: str 用户输入的非空字符串
    """
    i = input(msg).strip()
    while i.strip() == '':
        e_print("不接受空输入")
        i = input(msg).strip()
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


def reset_db():
    """
    重置数据库，删除所有表并重新创建, 并插入一些示例数据
    :return: None
    """
    global Base, engine
    Base.metadata.drop_all(engine)
    init_db()


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
    try:
        return {msg[0]: msg[1] for msg in [msg.split('=') for msg in query_str.split(',')]}
    except IndexError:
        e_print("不合法的输入，请重新启动程序!")
        exit()


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
            e_print(f"找不到对应的{TRANSLATION[obj_class.__name__]}")
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


def del_obj(obj_class, query_str, verbose=True):
    """
    删除对象
    :param obj_class: 要删除的对象类，可以从Candidate, Exam, Registration中选择
    :param query_str: 查询字符串，格式为"字段1=值1,字段2=值2,..."
    :param verbose: 是否打印错误信息和二次确认
    :return: bool 删除是否成功
    """
    global session
    query_dict = query_str_to_dict(query_str)
    if not all([field in obj_class.ALLOWED_SEARCH_FIELDS for field in query_dict.keys()]):
        if verbose:
            e_print("不合法的查询字段")
        return False
    obj = search_obj(obj_class, query_str)
    if not obj:
        if verbose:
            e_print(f"找不到对应的{TRANSLATION[obj_class.__name__]}")
        return False
    try:
        if not verbose or input(f"确定要删除{obj[0]}吗？(y/n): ").lower() == 'y':
            session.delete(obj[0])
            session.commit()
        else:
            return False
    except Exception as e:
        e_print(f"数据库错误: {e}")
        session.rollback()
        return False
    else:
        return True


def add_registration(query_str_0, query_str_1):
    """
    添加报名，因为报名对象的创建需要考生和考试对象，所以需要先确认考生和考试对象是否存在
    :param query_str_0: 查询字符串，格式为"字段1=值1,字段2=值2,..."，用于查询考生
    :param query_str_1: 查询字符串，格式为"字段1=值1,字段2=值2,..."，用于查询考试
    :return: bool 添加是否成功
    """
    global session
    candidate = search_obj(Candidate, query_str_0, verbose=False)
    exam = search_obj(Exam, query_str_1, verbose=False)
    if not candidate or not exam:
        e_print("找不到对应的考生或考试")
        return False
    try:
        new_registration = Registration(candidate=candidate[0], exam=exam[0])
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


def submenu(obj_class):
    """
    打印子菜单并获取用户输入
    :param obj_class: 要打印子菜单的对象类，可以从Candidate, Exam, Registration中选择
    :return: str 用户输入的选项
    """
    print_str = f"-----{TRANSLATION[obj_class.__name__]}管理------\n"
    for i, item in enumerate(SUBMENUS[obj_class.__name__]):
        print_str += f"{i+1}. {item}\n"
    print_str += "-------------------"
    print(print_str)
    return input_text("选择你要进行的操作: ")


def main_menu():
    """
    打印主菜单并获取用户输入
    :return: str 用户输入的选项
    """
    print_str = "----------主菜单----------\n"
    for i, item in enumerate(SUBMENUS['main']):
        print_str += f"{i+1}. {item}\n"
    print_str += "------------------------"
    print(print_str)
    return input_text("选择你要进行的操作: ")


def print_help(obj_class):
    """
    打印帮助文档
    :param obj_class: 要打印帮助文档的对象类，可以从Candidate, Exam, Registration中选择
    :return: None
    """
    print(HELP_DOC[obj_class.__name__])


if __name__ == '__main__':
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    if not os.path.exists(DATABASE_PATH):
        # 若数据库文件不存在，则初始化数据库
        init_db()
    while True:
        choice = main_menu()
        if choice in choice_map.keys():
            chosen_obj_class = choice_map[choice]
            while True:
                choice = submenu(chosen_obj_class)
                if choice == '1':
                    if chosen_obj_class == Registration:
                        add_registration(input_text("考生查询字符串: "), input_text("考试查询字符串: "))
                    else:
                        add_obj(chosen_obj_class, input_text("创建字符串: "))
                elif choice == '2':
                    list_obj(chosen_obj_class)
                elif choice == '3':
                    search_obj(chosen_obj_class, input_text("查询字符串: "))
                elif choice == '4':
                    update_obj(chosen_obj_class, input_text("查询字符串: "), input_text("更新字符串: "))
                elif choice == '5':
                    del_obj(chosen_obj_class, input_text("查询字符串: "))
                elif choice == '6':
                    print_help(chosen_obj_class)
                elif choice == '7':
                    break
                elif choice == '8':
                    session.close()
                    exit()
                else:
                    e_print("无效的选项")
        elif choice == '4':
            reset_db()
        elif choice == '5':
            session.close()
            exit()
        else:
            e_print("无效的选项")
