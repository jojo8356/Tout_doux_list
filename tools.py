"""File for manage tools for the main program (app.py) and model (model.py)"""
import os
from cryptography.fernet import Fernet
import re


# Config errors
class ErrorDB(Exception):
    """Customizable error messages for databases"""

    def __init__(self, message="Erreur administrateur"):
        self.message = message
        super().__init__(self.message)


# init classes
class Env:
    """Classe for get the variables of virtual environnement"""

    def __init__(self):
        self.file = ".env"

    # --Get--
    # -Get All-
    def get_all_vars_in_dict(self):
        """Get all variables in dictionary"""
        try:
            var = []
            dictio = {}
            with open(self.file, "r", encoding="utf-8") as file:
                txt = file.read()
            for x in txt.split("\n"):
                if "=" in x:
                    key, value = split_at_first_specific_element(x, "=")
                    key = key.replace(" ", "")
                    value = value.replace(" ", "")
                    dictio[key] = value
            if not dictio:
                return {}
            return dictio
        except:
            return {}

    def get_all_vars_names(self):
        """Get all variables names"""
        dictio = self.get_all_vars_in_dict()
        if not dictio:
            return {}
        return dictio.keys()

    def get_all_vars_values(self):
        """Get all variables values"""
        dictio = self.get_all_vars_in_dict()
        if not dictio:
            return {}
        return dictio.values()

    # -Get One-
    def get_var(self, var):
        """Get variable with/by name"""
        return self.get_all_vars_in_dict().get(var)

    # --Others--
    def add_var(self, var):
        """A function to write a dictionary variable to the .env file"""
        var = convert_dict_to_list(var)[0]
        with open(self.file, "a", encoding="utf-8") as file:
            file.write(f"\n{' = '.join(var)}")


class Cryptographie:
    """Classe for Crypt datas"""

    def __init__(self, name: str) -> None:
        self.key = None
        self.cipher_suite = None
        self.env = Env()
        self.name = name
        self.load_key()

    def load_key(self):
        """Load main key for crypt"""
        self.key = self.env.get_var(self.name)
        if not self.key:
            self.init_key()
        if isinstance(self.key, str):
            self.key = self.key.encode()
        self.cipher_suite = Fernet(self.key)

    def init_key(self):
        """Initializat° of the primary key, if it doesn't exist, it's created and for crypt."""
        self.key = self.generate_key()
        self.env.add_var({self.name: self.key.decode()})
        self.cipher_suite = Fernet(self.key)

    def get_key(self):
        """Get main key for crypt"""
        dictio = self.env.get_all_vars_in_dict()
        if dictio:
            return dictio.get(self.name)

    def generate_key(self):
        """Generate key for crypt"""
        return Fernet.generate_key()

    def crypt(self, data: str) -> str:
        """Crypt data for security"""
        encrypted_data = self.cipher_suite.encrypt(data.encode()).decode()
        return encrypted_data

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data for analyse"""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        if isinstance(decrypted_data, str):
            decrypted_data = decrypted_data.decode()
        return decrypted_data


def check_file_exists(file_path):
    """Check if file exists"""
    return os.path.exists(file_path)


def sum_dict(list_of_dicts):
    """Sum dict"""
    result = {}
    for element in list_of_dicts:
        result.update(element)
    return result


def convert_dict_to_list(dictio):
    """Convert dict to list"""
    return [[key, value] for key, value in dictio.items()]


def del_doubles(liste):
    return list(set(liste))


def get_code_file(file):
    with open(file, "r") as file:
        code = file.read()
    return code


def split_at_first_specific_element(string, element):
    index = string.find(element)
    if index != -1:
        return string[:index], string[(index + 1) :]
    else:
        return [string]


def verif_password(password):
    if len(password) < 12:
        return "Ton mot de passe est en dessous de 12 caractères"

    lowercase = re.compile(r"[a-z]")
    uppercase = re.compile(r"[A-Z]")
    digits = re.compile(r"[0-9]")
    specialChars = re.compile(r"[$&+,:;=?@#|<>.^*()%!-]")

    if not lowercase.search(password):
        return "Il n'y a pas de minuscules dans ton mot de passe"
    if not uppercase.search(password):
        return "Il n'y a pas de majuscules dans ton mot de passe"
    if not digits.search(password):
        return "Il n'y a pas de chiffres dans ton mot de passe"
    if not specialChars.search(password):
        return "Il n'y a pas de caractères spéciaux dans ton mot de passe"
