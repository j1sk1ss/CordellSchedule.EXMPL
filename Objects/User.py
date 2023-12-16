import pickle


class User:
    def __init__(self, chat_id):
        self.login = ''
        self.password = ''

        self.pairs_missed = {}
        self.chat_id = chat_id

        self.is_setting_attention = False
        self.is_setting_review = False
        self.is_setting_login_and_pass = False

        self.attention = 0
        self.is_attention = False
        self.attention_pairs = []

        self.every_day_review = False


class Users:
    def __init__(self, users):
        self.users = users

    def get_user(self, chat_id):
        for user in self.users:
            if user.chat_id == chat_id:
                return user

        return None

    def add_user(self, user):
        self.users.append(user)

    @staticmethod
    def load_object():
        try:
            with open("data.pickle", "rb") as f:
                return pickle.load(f)
        except Exception as ex:
            print("Error during unpickling object (Possibly unsupported):", ex)
            return Users([])

    def save_object(self):
        try:
            with open("data.pickle", "wb") as f:
                pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as ex:
            print("Error during pickling object (Possibly unsupported):", ex)
