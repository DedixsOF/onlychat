import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QListWidget, QTextEdit, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt
import requests
import socketio
from modules.utils import load_config

config = load_config()
SERVER_URL = config['CLIENT']['SERVER_URL']
sio = socketio.Client()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)
        self.setWindowTitle('Login')
        self.setGeometry(300, 300, 300, 200)

        # Установка фокуса на поле ввода логина
        self.username_input.setFocus()

        # Установка обработчика клавиатуры
        self.username_input.returnPressed.connect(self.focus_on_password)
        self.password_input.returnPressed.connect(self.login)

    def focus_on_password(self):
        self.password_input.setFocus()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        # Здесь добавьте логику для отправки данных на сервер
        print(f"Logging in with username: {username} and password: {password}")

        response = requests.post(f"{SERVER_URL}/login",
                                 json={"username": username, "password": password})

        if response.status_code == 200:
            data = response.json()
            self.chat_select = ChatSelectWindow(username, data['token'],
                                                data['permissions'])
            self.chat_select.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Login failed')


class ChatSelectWindow(QWidget):
    def __init__(self, username, token, permissions):
        super().__init__()
        self.username = username
        self.token = token
        self.permissions = permissions
        self.init_ui()
        self.load_chats()

    def init_ui(self):
        layout = QVBoxLayout()

        # Chat list
        self.chat_list = QListWidget()
        layout.addWidget(QLabel('Available Chats:'))
        layout.addWidget(self.chat_list)

        # Join button
        self.join_button = QPushButton('Join Chat')
        self.join_button.clicked.connect(self.join_chat)
        layout.addWidget(self.join_button)

        self.setLayout(layout)
        self.setWindowTitle('Select Chat')
        self.setGeometry(300, 300, 400, 300)

        # Add Admin Panel button for users with admin permissions
        if self.permissions == 4:
            self.admin_button = QPushButton('Open Admin Panel')
            self.admin_button.clicked.connect(self.open_admin_panel)
            layout.addWidget(self.admin_button)

        self.setLayout(layout)
        self.setWindowTitle('Select Chat')
        self.setGeometry(300, 300, 400, 300)
        
    def load_chats(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{SERVER_URL}/get_chats",
                                headers=headers,
                                params={"permissions": self.permissions})

        if response.status_code == 200:
            self.chats = response.json()
            for chat in self.chats:
                chat_id, chat_name, _, _ = chat
                self.chat_list.addItem(f"{chat_name} (ID: {chat_id})")
        else:
            QMessageBox.warning(self, 'Error', 'Failed to load chats')
    
    def refresh_chats(self):
        self.chat_list.clear()  # Очищаем текущий список
        self.load_chats()  # Загружаем чаты заново
    
    def join_chat(self):
        if self.chat_list.currentRow() >= 0:
            selected_chat = self.chats[self.chat_list.currentRow()]
            chat_id = selected_chat[0]
            self.chat_window = ChatWindow(self.username, chat_id, self.token, self.permissions)
            self.chat_window.show()
        self.close()
    def open_admin_panel(self):
        self.admin_panel = AdminPanel(self.token, self)
        self.admin_panel.show()


class ChatWindow(QWidget):
    def __init__(self, username, chat_id, token, permissions):
        super().__init__()
        self.username = username
        self.chat_id = chat_id
        self.token = token
        self.permissions = permissions
        self.init_ui()
        self.connect_to_server()

    def init_ui(self):
        layout = QVBoxLayout()

        # Добавляем кнопку выхода в верхней части окна
        self.exit_button = QPushButton('Exit Chat')
        self.exit_button.clicked.connect(self.exit_chat)
        layout.addWidget(self.exit_button)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Message input
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)
        self.setWindowTitle(f'Chat - {self.username}')
        self.setGeometry(300, 300, 500, 400)

        # Добавляем обработчик Enter для отправки сообщения
        self.message_input.returnPressed.connect(self.send_message)

    def exit_chat(self):
        sio.emit('leave_chat', {'username': self.username, 'chat_id': self.chat_id})
        sio.disconnect()
        
        # Создаем и показываем окно выбора чата
        self.chat_select = ChatSelectWindow(self.username, self.token, self.permissions)
        self.chat_select.show()
        
        # Закрываем текущее окно чата
        self.close()
        
    def connect_to_server(self):
        sio.connect(SERVER_URL)
        sio.emit('join_chat', {'username': self.username, 'chat_id': self.chat_id})

        @sio.event
        def message(data):
            self.chat_display.append(f"{data['username']}: {data['message']}")

    def send_message(self):
        message = self.message_input.text()
        if message:
            sio.emit('send_message', {
                'username': self.username,
                'chat_id': self.chat_id,
                'message': message
            })
            self.message_input.clear()


class AdminPanel(QWidget):
    def __init__(self, token, chat_select_window):
        super().__init__()
        self.token = token
        self.chat_select_window = chat_select_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Создание чата
        chat_group = QGroupBox("Create New Chat")
        chat_layout = QVBoxLayout()
        
        self.chat_name_input = QLineEdit()
        self.chat_name_input.setPlaceholderText("Chat Name")
        self.chat_perm_input = QLineEdit()
        self.chat_perm_input.setPlaceholderText("Permissions (1-4)")
        self.chat_status_input = QLineEdit()
        self.chat_status_input.setPlaceholderText("Chat Status")
        
        create_chat_btn = QPushButton("Create Chat")
        create_chat_btn.clicked.connect(self.create_chat)
        
        chat_layout.addWidget(self.chat_name_input)
        chat_layout.addWidget(self.chat_perm_input)
        chat_layout.addWidget(self.chat_status_input)
        chat_layout.addWidget(create_chat_btn)
        chat_group.setLayout(chat_layout)
        
        # Управление пользователями
        user_group = QGroupBox("User Management")
        user_layout = QVBoxLayout()
        
        self.user_list = QListWidget()
        self.load_users_btn = QPushButton("Load Users")
        self.load_users_btn.clicked.connect(self.load_users)
        
        user_layout.addWidget(self.user_list)
        user_layout.addWidget(self.load_users_btn)
        user_group.setLayout(user_layout)
        
        layout.addWidget(chat_group)
        layout.addWidget(user_group)
        self.setLayout(layout)
        self.setWindowTitle('Admin Panel')
        self.setGeometry(300, 300, 400, 500)

    def create_chat(self):
        chat_name = self.chat_name_input.text()
        permissions = int(self.chat_perm_input.text())
        status = self.chat_status_input.text()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{SERVER_URL}/add_chat",
            headers=headers,
            json={
                "name": chat_name,
                "permissions": permissions,
                "status": status
            }
        )
        
        if response.status_code == 201:
            QMessageBox.information(self, 'Success', 'Chat created successfully')
            if self.chat_select_window:
                self.chat_select_window.refresh_chats()  # Обновляем список чатов
        else:
            try:
                error_data = response.json()  # Получаем JSON из ответа
                error_message = error_data.get('message', 'Unknown error')  # Получаем сообщение об ошибке или используем значение по умолчанию
                QMessageBox.warning(self, 'Error', f'Failed to create chat: {error_message}')
            except ValueError:  # Если JSON не может быть прочитан
                QMessageBox.warning(self, 'Error', f'Failed to create chat: Status code {response.status_code}')

    def load_users(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{SERVER_URL}/get_users",
            headers=headers
        )
        
        if response.status_code == 200:
            self.user_list.clear()
            users = response.json()
            for user in users:
                self.user_list.addItem(f"User: {user['username']} - Permissions: {user['permissions']}")
        else:
            QMessageBox.warning(self, 'Error', 'Failed to load users')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())