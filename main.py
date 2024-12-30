from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from functools import wraps
import os
import datetime


# 数据库文件路径默认为脚本所在目录下的database.sqlite
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


Base = declarative_base()


class Candidate(Base):
    __tablename__ = 'candidates'
    ALLOWED_SEARCH_FIELDS = ['name', 'phone_number']
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    registered_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    registrations = relationship(
        "Registration",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Candidate {self.name}-{self.phone_number}-{self.registered_date}>"


class Exam(Base):
    __tablename__ = 'exams'
    ALLOWED_SEARCH_FIELDS = ['title', 'location']
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    date = Column(Date, nullable=False, default=datetime.date.today)
    location = Column(String(200), nullable=False)
    max_candidates = Column(Integer, nullable=False)
    registrations = relationship(
        "Registration",
        back_populates="exam",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Exam {self.title}-{self.location}-{self.date}>"


class Registration(Base):
    __tablename__ = 'registrations'
    ALLOWED_SEARCH_FIELDS = ['candidate_id', 'exam_id']
    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False)
    registration_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    candidate = relationship("Candidate", back_populates="registrations")
    exam = relationship("Exam", back_populates="registrations")

    def __repr__(self):
        return f"<Registration {self.exam.title} - {self.candidate.name} - {self.registration_date}>"


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
    print("1. Add a candidate")
    print("2. List all candidates")
    print("3. Search for a candidate")
    print("4. Update a candidate")
    print("5. Delete a candidate")
    print("6. Back to main menu")
    print("7. Exit")
    return input("Please select an option: ")


def exam_submenu():
    print("1. Add an exam")
    print("2. List all exams")
    print("3. Search for an exam")
    print("4. Update an exam")
    print("5. Delete an exam")
    print("6. Back to main menu")
    print("7. Exit")
    return input("Please select an option: ")


def registration_submenu():
    print("1. Register a candidate for an exam")
    print("2. List all registrations")
    print("3. Search for a registration")
    print("4. Update a registration")
    print("5. Delete a registration")
    print("6. Back to main menu")
    print("7. Exit")
    return input("Please select an option: ")
if __name__ == '__main__':
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    if not os.path.exists(DATABASE_PATH):
        # 若数据库文件不存在，则初始化数据库
        init_db()
    session.close()
    # Base.metadata.drop_all(engine)
