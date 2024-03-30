"""Function and class toolbox for the app"""


from os import path
from inspect import currentframe, getframeinfo
import re
from cryptography.fernet import Fernet


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
            dictio = {}
            with open(self.file, "r", encoding="utf-8") as file:
                txt = file.read()
            for x in txt.split("\n"):
                if "=" in x:
                    key, value = split_at_first_specific_element(x, "=")
                    key = key.replace(" ", "")
                    value = value.replace(" ", "")
                    dictio[key] = value
            return dictio or {}
        except FileNotFoundError:
            return {}

    def get_all_vars_names(self):
        """Get all variables names"""
        return self.get_all_vars_in_dict().keys() or {}

    def get_all_vars_values(self):
        """Get all variables values"""
        return self.get_all_vars_in_dict().values() or {}

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
        return None

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
    return path.exists(file_path)


def sum_dict(list_of_dicts):
    """Sum list of dict to one dict"""
    return {k: v for d in list_of_dicts for k, v in d.items()}


def convert_dict_to_list(dictio):
    """Convert dict to list"""
    return [[key, value] for key, value in dictio.items()]


def del_doubles(liste):
    """Removes all duplicates from the list"""
    return list(set(liste))


def get_code_file(file):
    """Get code of <file>"""
    with open(file, "r", encoding="utf-8") as content:
        code = content.read()
    return code


def split_at_first_specific_element(string, element):
    """Splits the given string at the first occurrence of the specified delimiter"""
    index = string.find(element)
    if index != len(string) - 1:
        return string[:index], string[(index + 1) :]
    return [string]


def verif_password(password):
    """Verification of password."""
    if len(password) < 12:
        return "Ton mot de passe est en dessous de 12 caractères"

    lowercase = re.compile(r"[a-z]")
    uppercase = re.compile(r"[A-Z]")
    digits = re.compile(r"[0-9]")
    special_chars = re.compile(r"[$&+,:;=?@#|<>.^*()%!-]")

    elements = ["minuscules", "majuscules", "chiffres", "caractères spéciaux"]
    type_letters = [lowercase, uppercase, digits, special_chars]

    for i, element in enumerate(elements):
        if not type_letters[i].search(password):
            return f"Il n'y a pas de {element} dans ton mot de passe"
    return None


def get_current_filename():
    """Get the name of the current file"""
    frame = currentframe()
    filename = getframeinfo(frame).filename
    return filename


def get_all_names():
    names = findall(r'DB\("([^"]+)"\)', get_code_file("models.py"))
    return del_doubles(names)
