from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import os


DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


Base = declarative_base()
engine = create_engine(DATABASE_URL)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String())
    age = Column(Integer)


if not os.path.exists(DATABASE_PATH):
    Base.metadata.create_all(engine)
    print('Database created!')
Session = sessionmaker(bind=engine)
session = Session()
new_user = User(name='Alice', age=30)
session.add(new_user)
session.commit()


users = session.query(User).all()
for user in users:
    print(user.id, user.name, user.age)


session.close()
# Base.metadata.drop_all(engine)
