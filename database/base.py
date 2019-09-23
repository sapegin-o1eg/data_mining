from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from database.models import Vacancy, Base


class VacancyDB:

    def __init__(self, url):
        self.url = url
        pass

    def add_salary(self, db_item):
        self.engine = create_engine(self.url)
        Base.metadata.create_all(self.engine)

        db_session = sessionmaker(bind=self.engine)
        session = db_session()
        session.add(db_item)
        try:
            session.commit()
        except Exception as e:
            print(e)
        session.close()
