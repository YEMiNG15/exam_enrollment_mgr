from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from constants import TRANSLATION, DATE_STR_FORMAT, DATETIME_STR_FORMAT
import datetime


Base = declarative_base()


class Candidate(Base):
    __tablename__ = 'candidates'
    ALLOWED_SEARCH_FIELDS = ['name', 'phone_number'] # 允许的搜索字段
    REQUIRED_FIELDS = ['name', 'phone_number'] # 创建时必须提供的字段
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
        return f"<{TRANSLATION['Candidate']} {self.name}-{self.phone_number}-{self.registered_date_str}>"

    @property
    def registered_date_str(self):
        return self.registered_date.strftime(DATETIME_STR_FORMAT)


class Exam(Base):
    __tablename__ = 'exams'
    ALLOWED_SEARCH_FIELDS = ['title', 'location'] # 允许的搜索字段
    REQUIRED_FIELDS = ['title', 'date', 'location', 'max_candidates'] # 创建时必须提供的字段
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    date = Column(Date, nullable=False, default=datetime.date.today)
    location = Column(String(200), nullable=False)
    registrations = relationship(
        "Registration",
        back_populates="exam",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<{TRANSLATION['Exam']} {self.title}-{self.location}-{self.date_str}>"

    @property
    def date_str(self):
        return self.date.strftime(DATE_STR_FORMAT)


class Registration(Base):
    __tablename__ = 'registrations'
    ALLOWED_SEARCH_FIELDS = ['candidate_id', 'exam_id'] # 允许的搜索字段
    REQUIRED_FIELDS = ['candidate_id', 'exam_id'] # 创建时必须提供的字段
    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    exam_id = Column(Integer, ForeignKey('exams.id'), nullable=False)
    registration_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    candidate = relationship("Candidate", back_populates="registrations")
    exam = relationship("Exam", back_populates="registrations")

    def __repr__(self):
        return f"<{TRANSLATION['Registration']} {self.exam.title} - {self.candidate.name} - {self.registration_date_str}>"

    @property
    def registration_date_str(self):
        return self.registration_date.strftime(DATETIME_STR_FORMAT)
