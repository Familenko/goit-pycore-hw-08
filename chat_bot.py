import pickle
import difflib


from class_store import AddressBook, Record


class ChatBot:
    """
    ChatBot class is a simple chatbot that can store and manage contacts.
    It uses the AddressBook and Record classes from class_store.py to store
    and manage contact information. The chatbot can add, change, delete, and
    display contact information. It can also display upcoming birthdays and
    delete phone numbers from contacts.

    The chatbot uses the following commands:
    - hello: Displays a welcome message.
    - add <name> <phone>: Adds a new contact or updates an existing one with a phone number.
    - change <name> <old_phone> <new_phone>: Changes a phone number for an existing contact.
    - phone <name>: Displays phone numbers for a contact.
    - all: Displays all contacts.
    - add-birthday <name> <birthday>: Adds a birthday for a contact.
    - show-birthday <name>: Displays the birthday for a contact.
    - birthdays: Displays upcoming birthdays in the next week.
    - delete <name>: Deletes a contact.
    - remove-phone <name> <phone>: Removes a phone number from a contact.
    - close or exit: Exits the chatbot.
    """
    def __init__(self, filename="addressbook.pkl"):
        self.book = self.load_data(filename)
        self.commands = [
            'hello', 
            'add', 
            'change', 
            'phone', 
            'all', 
            'add-birthday', 
            'show-birthday', 
            'birthdays', 
            'delete', 
            'remove-phone'
            ]
        
    def find_closest_command(self, input_command):
        closest_matches = difflib.get_close_matches(input_command, self.commands)
        if closest_matches:
            return closest_matches[0]
        return None

    @staticmethod
    def input_error(handler):
        def wrapper(*args, **kwargs):
            try:
                return handler(*args, **kwargs)
            except KeyError:
                return "The contact does not exist. Try again."
            except ValueError as e:
                return str(e)
            except (IndexError, TypeError):
                return "Invalid input. Please check your command format."
        return wrapper

    @input_error
    def add_contact(self, args):
        name, phone, *_ = args
        record = self.book.find(name)
        message = "Contact updated."
        if record is None:
            record = Record(name)
            self.book.add_record(record)
            message = "Contact added."
        if phone:
            record.add_phone(phone)
        return message

    @input_error
    def change_contact(self, args):
        name, old_phone, new_phone = args
        record = self.book.find(name)
        if record:
            record.edit_phone(old_phone, new_phone)
            return "Contact updated."
        else:
            raise KeyError

    @input_error
    def show_phone(self, args):
        name = args[0]
        record = self.book.find(name)
        if record:
            phones = ', '.join(phone.value for phone in record.phones)
            return f"{name}'s phone numbers are {phones}"
        else:
            raise KeyError

    @input_error
    def add_birthday(self, args):
        name, birthday = args
        record = self.book.find(name)
        if record:
            record.add_birthday(birthday)
            return "Birthday added."
        else:
            raise KeyError

    @input_error
    def show_birthday(self, args):
        name = args[0]
        record = self.book.find(name)
        if record and record.birthday:
            return f"{name}'s birthday is {record.birthday.value}"
        else:
            raise KeyError

    @input_error
    def birthdays(self, mock):
        upcoming = self.book.get_upcoming_birthdays()
        if upcoming:
            return "\n".join(str(record) for record in upcoming)
        else:
            return "No birthdays in the next week."

    @input_error
    def delete_contact(self, args):
        name = args[0]
        self.book.delete(name)
        return f"Contact '{name}' deleted."

    @input_error
    def remove_phone(self, args):
        name, phone = args
        record = self.book.find(name)
        if record:
            record.remove_phone(phone)
            return f"Phone number '{phone}' removed from contact '{name}'."
        else:
            raise KeyError

    def show_all_contacts(self, mock):
        if self.book:
            return "\n".join(str(record) for record in self.book.values())
        else:
            return "No contacts found."
        
    def hello(self, mock):
        return "How can I help you?"

    def parse_input(self, user_input: str) -> tuple:
        parts = user_input.strip().split()
        command = parts[0].lower()
        args = parts[1:]
        return command, args

    def run(self, user_input: str):
        if user_input.strip() == "":
            return "Invalid command. Try again."

        command, args = self.parse_input(user_input)
        if command in ["close", "exit"]:
            self.save_data()
            return "Good bye!"

        command_dict = {
            'hello': self.hello,
            'add': self.add_contact,
            'change': self.change_contact,
            'phone': self.show_phone,
            'all': self.show_all_contacts,
            'add-birthday': self.add_birthday,
            'show-birthday': self.show_birthday,
            'birthdays': self.birthdays,
            'delete': self.delete_contact,
            'remove-phone': self.remove_phone,
        }

        if command in command_dict:
            return command_dict[command](args)
        else:
            closest_command = self.find_closest_command(command)
            if closest_command:
                return f"Did you mean '{closest_command}'? Please try again."
            return "Invalid command. Try again."
        
    def save_data(self, filename="addressbook.pkl"):
        with open(filename, 'wb') as file:
            pickle.dump(self.book, file)

    def load_data(self, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()
