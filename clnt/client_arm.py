import requests
import socketio
from modules.utils import load_config

config = load_config('arm')
SERVER_URL = config['CLIENT']['SERVER_URL']
sio = socketio.Client()

class ChatClient:
    def __init__(self):
        self.token = None
        self.chat_id = None
        self.username = None

    def login(self, username, password):
        response = requests.post(f"{SERVER_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self.username = username
            print("Login successful!")
            return data['permissions']
        else:
            print("Login failed.")
            return None

    def get_chats(self, permissions):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{SERVER_URL}/get_chats", headers=headers, params={"permissions": permissions})
        if response.status_code == 200:
            chats = response.json()
            print("Available Chats:")
            while True:
                for index, chat in enumerate(chats):
                    chat_id, chat_name, chat_permissions, chat_status = chat
                    print(f"{index + 1}. {chat_name} (ID: {chat_id})")
                try:
                    choice = int(input("Select a chat by entering the corresponding number: ")) - 1
                    if 0 <= choice < len(chats):
                        self.chat_id = chats[choice][0]
                        return self.chat_id
                    else:
                        print("Такой чат не существует или не доступен для Вас.")
                except ValueError:
                    print("Пожалуйста, введите корректный номер.")
        else:
            print("Failed to get chats:", response.json())
            return None

    def connect_to_server(self):
        sio.connect(SERVER_URL)
        sio.emit('join_chat', {'username': self.username, 'chat_id': self.chat_id})

    def send_message(self, message):
        sio.emit('send_message', {'username': self.username, 'chat_id': self.chat_id, 'message': message})

    def close_connection(self):
        sio.emit('leave_chat', {'username': self.username, 'chat_id': self.chat_id})
        sio.disconnect()

@sio.event
def connect():
    print("Connected to chat server.")

@sio.event
def message(data):
    print(f"{data['username']}: {data['message']}")

@sio.event
def disconnect():
    print("Disconnected from chat server.")

if __name__ == "__main__":
    client = ChatClient()
    username = input("Username: ")
    password = input("Password: ")
    permissions = client.login(username, password)

    if permissions is not None:
        chat_id = client.get_chats(permissions)
        if chat_id:
            client.connect_to_server()
            while True:
                message = input("Message: ")
                if message == "/quit":
                    client.close_connection()
                    break
                client.send_message(message)
