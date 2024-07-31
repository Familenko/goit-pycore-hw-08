import re
from datetime import datetime, timedelta
from collections import UserDict


class Field:
    """
    Base class for all fields.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """
    A class for storing and validate a contact's name.
    """
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)


class Phone(Field):
    """
    A class for storing and validate a phone number.
    """
    def __init__(self, value):
        normalized_value = self.normalize_phone(value)
        if not re.match(r'^\+38\d{10}$', normalized_value):
            raise ValueError("Phone number must be in the format +38XXXXXXXXXX")
        super().__init__(normalized_value)

    @staticmethod
    def normalize_phone(phone_number: str) -> str:
        """
        Normalize a phone number to the format +38XXXXXXXXXX.
        Args:
            phone_number (str): The phone number to normalize.
        Returns:
            str: The normalized phone number.
        """
        cleaned_number = re.sub(r'\D', '', phone_number)
        civil_number = cleaned_number[-10:]
        country_code = "+38"
        result = country_code + civil_number
        
        return result


class Birthday(Field):
    """
    A class for storing and validate a birthday.
    """
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:
    """
    A class for creating a contact record.
    """
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if p.value != phone_number]

    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if phone.value == old_number:
                phone.value = new_number
                return
        raise ValueError("Old phone number not found")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone.value
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = self.birthday.value if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"


class AddressBook(UserDict):
    """
    A class for storing contact records.
    """
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        today = datetime.now().date()
        deadline = today + timedelta(days=days)
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday = birthday.replace(year=today.year)
                if today <= birthday <= deadline:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

    def __getstate__(self):
        state = {}
        for name, record in self.data.items():
            state[name] = {
                'name': name,
                'phones': [phone.value for phone in record.phones],
                'birthday': record.birthday.value if record.birthday else None
            }

        return state

    def __setstate__(self, state):
        self.data = {}
        for name, record in state.items():
            new_record = Record(name)
            new_record.phones = [Phone(phone) for phone in record['phones'] if phone]
            new_record.birthday = Birthday(record['birthday']) if record['birthday'] else None
            self.data[name] = new_record
