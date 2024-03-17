from ast import literal_eval
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from tools import *
import re

db = declarative_base


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
    def get_engine(self):
        """Get engine of ORM"""
        return self.engine

    def get_session(self):
        """Get session of ORM"""
        return self.session

    def get_conn(self):
        """Get connexion (conn) of ORM"""
        return self.conn

    def get_name(self):
        return self.file

    # --Others--
    def exec_sql(self, sql):
        """Execute the SQL for commands that are not supported by the ORM."""
        return self.conn.execute(sql)

    def build(self, base):
        """Create all tables defined by base metadata."""
        base.metadata.create_all(self.engine)

    def get_all_names():
        names = re.findall(r'DB\("([^"]+)"\)', get_code_file("models.py"))
        return del_doubles(names)


base_tdl = db()


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


class Todolist_manager:
    """Tools for class Todolist"""

    def __init__(self):
        self.db = DB("todolist.db")
        self.engine = self.db.get_engine()
        self.session = self.db.get_session()
        self.all_tasks = self.session.query(Todolist).all()
        self.all_tasks_names = [x.name for x in self.all_lists]

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
        if self.verif_name(name):
            index = self.all_tasks_names.index(name)
            return self.all_tasks[index]
        return None

    # --Verification--
    # -Verification One-
    def verif_name(self, name):
        """Verification of name in list names"""
        return name in self.all_tasks_names

    def verif_task(self, task):
        """Verification of task in list tasks"""
        return task in self.all_lists

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
        task = self.get_task_by_name(name)
        task.name = new_name
        self.save()

    def change_task_status(self, name):
        """Change the status of task"""
        task = self.get_task_by_name(name)
        task.status = not task.status
        self.save()


base_account = db()


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


class Account_manager:
    def __init__(self):
        # inits variables db
        self.db = DB("account.db")
        self.engine = self.db.get_engine()
        self.session = self.db.get_session()
        self.crypto = Cryptographie("ACCOUNT_KEY")

        # DB variables
        self.accounts = self.session.query(Account).all()
        self.emails = [account.email for account in self.accounts]
        self.passwords = [
            self.crypto.decrypt(account.password) for account in self.accounts
        ]
        self.names = [account.name for account in self.accounts]

    # --Get--
    # -Get All-
    def get_all_accounts(self):
        """Get all accounts"""
        return self.accounts

    def get_all_names(self):
        """Get all names"""
        return self.names

    def get_all_emails(self):
        """Get all emails"""
        return self.emails

    def get_all_passwords(self):
        """Get all passwords"""
        return self.passwords

    # -Get One-
    def get_account_by_password(self, password):
        """Get account with/by password"""
        if self.verif_password(password):
            index = self.passwords.index(password)
            return self.accounts[index]
        return None

    def get_account_by_name(self, name):
        """Get account with/by name"""
        if self.verif_name(name):
            index = self.names.index(name)
            return self.accounts[index]
        return None

    # --Verif--
    # -Verif One-
    def verif_account(self, email: str, password: str) -> bool:
        """Verif account with/by verification of args"""
        if self.verif_password(password) and self.verif_email(email):
            return self.emails.index(email) == self.passwords.index(password)

    def verif_password(self, password):
        """Verification of password with/by list of passwords"""
        return password in self.passwords

    def verif_email(self, email):
        """Verification of email with/by list of emails"""
        return email in self.emails

    def verif_name(self, name):
        """Verification of name with/by list of names"""
        return name in self.names

    # --Others--
    def add_account(self, name, email, password):
        """Add account"""
        account = Account(name=name, email=email, password=self.crypto.crypt(password))
        self.session.add(account)
        self.save()
        return self.to_dict(account)

    def save(self):
        """Shortcut command for save."""
        self.session.commit()

    def change_password(self, old_password, new_password):
        """Change password"""
        account = get_account_by_password(old_password)
        if account:
            account.password = crypto.crypt(new_password)
            self.save()
        else:
            return f"Ce mot de passe n'existe pas: {old_password}"

    def to_dict(self, email, password):
        """Convert account to dict for get easily the variables"""
        return {
            "password": password,
            "email": email,
        }

    def to_dict(self, account):
        """Convert account to dict for get easily the variables"""
        return {
            "name": account.name,
            "password": account.password,
            "email": account.email,
        }


def get_bases():
    code = get_code_file("models.py")
    pattern = r"\b(base_[a-zA-Z_][a-zA-Z0-9_]*)\b"
    database_names = re.findall(pattern, code)
    return database_names


def run_db():
    """Run DB"""
    bases = sorted(del_doubles(get_bases()))
    files = sorted(DB.get_all_names())
    for base, file in zip(bases, files):
        DB(file).build(eval(base))
