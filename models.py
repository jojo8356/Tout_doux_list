"""Program grouping all DB managers"""

import re
from sqlalchemy import create_engine, Column, Integer, Text, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from tools import (
    Cryptographie,
    del_doubles,
    get_code_file,
    get_current_filename,
    get_db_names,
)


db = declarative_base

base_account = db()
base_tdl = db()

base_mapping = {
    "base_tdl": base_tdl,
    "base_account": base_account,
}


class DB:
    """Main class DB"""

    def __init__(self, file: str = ""):
        if file:
            self.options = {"check_same_thread": False}
            self.sql_engine = "sqlite:///db/"
            self.file = file
            self.engine = create_engine(
                self.sql_engine + self.file, connect_args=self.options
            )
            self.session = sessionmaker(bind=self.engine)()
            self.conn = self.session.connection()

    # --Get--
    # -Get One-
    def get_engine(self) -> object:
        """Get engine of ORM"""
        return self.engine

    def get_session(self) -> object:
        """Get session of ORM"""
        return self.session

    def get_conn(self) -> object:
        """Get connexion (conn) of ORM"""
        return self.conn

    def get_name(self) -> str:
        """Get name of SQL file"""
        return self.file

    # --Others--
    def exec_sql(self, sql: str):
        """Execute the SQL for commands that are not supported by the ORM."""
        return self.conn.execute(sql)

    def build(self, base: object):
        """Create all tables defined by base metadata."""
        base.metadata.create_all(self.engine)

    @classmethod
    def get_all_filenames(cls):
        """Get all names of SQL files"""
        names = re.findall(r'DB\("([^"]+)"\)', get_code_file(get_current_filename()))
        return del_doubles(names)


class Todolist(base_tdl):
    """Class Account (table) for the ORM. It is the structure of the DB"""

    __tablename__ = "todolist"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    status = Column(Boolean)

    def __init__(self, name, status):
        self.name = name
        self.status = status

    def __repr__(self):
        return f"Todolist(id={self.id}, name={self.name}, status={self.status})"

    def get_infos_of_task(self):
        """Get name and amil to string"""
        return f"Name: {self.name}, status: {self.status}"


class TodolistManager:
    """Tools for class Todolist"""

    def __init__(self):
        self.db = DB("todolist.db")
        self.engine = self.db.get_engine()
        self.session = self.db.get_session()
        self.all_tasks = self.session.query(Todolist).all()
        self.all_tasks_names = [x.name for x in self.all_tasks]

    # --Get--
    # -Get All-
    def get_all_tasks(self):
        """Get all todolists"""
        return self.all_tasks

    def get_all_names_of_tasks(self):
        """Get all tasks names"""
        return self.all_tasks_names

    # -Get One-
    def get_task_by_name(self, name):
        """Get task with/by name"""
        if self.verif_task(name):
            index = self.all_tasks_names.index(name)
            return self.all_tasks[index]
        return None

    # --Verification--
    # -Verification One-
    def verif_task(self, name):
        """Verification of name in list names"""
        return name in self.all_tasks_names

    # --Others--
    def save(self):
        """Save the db"""
        self.session.commit()

    def add_task(self, name, status):
        """Add task to db"""
        task = Todolist(name=name, status=status)
        self.session.add(task)
        self.save()

    def del_task(self, name):
        """Delete task from db"""
        task = self.get_task_by_name(name)
        self.session.delete(task)
        self.save()

    def change_task_name(self, old_name, new_name):
        """Change the name of task"""
        task = self.get_task_by_name(old_name)
        task.name = new_name
        self.save()

    def change_task_status(self, name):
        """Change the status of task"""
        task = self.get_task_by_name(name)
        task.status = not task.status
        self.save()


class Account(base_account):
    """Class Account (table) for the ORM. It is the structure of the DB"""

    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    email = Column(Text)
    password = Column(Text)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return f"Account(id={self.id}, name={self.name}, email={self.email})"

    def get_name_and_email(self):
        """Get name and amil to string"""
        return f"Name: {self.name}, Email: {self.email}"


def get_db_names():
    """Get all bases"""
    code = get_code_file(get_current_filename())
    pattern = r"\b(base_[a-zA-Z_][a-zA-Z0-9_]*)\b"
    database_names = re.findall(pattern, code)
    return del_doubles(database_names)


def run_db():
    """Run DB"""
    bases = sorted(get_db_names())
    files = sorted(DB.get_all_filenames())
    for base_name, file in zip(bases, files):
        base = base_mapping.get(base_name)
        if base is not None:
            DB(file).build(base)
        else:
            print(f"Warning: Base '{base_name}' not found.")
