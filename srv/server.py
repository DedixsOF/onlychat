from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import jwt
from datetime import datetime, timedelta, timezone
from modules.utils import load_config, setup_logging
from modules.db import Database
from modules.encryption import Encryption

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bbe76ef0db9779dd62cfc89845a'
socketio = SocketIO(app)
logger = setup_logging()
config = load_config()
db = Database()
SECRET_KEY = config['SERVER']['SECRET']

def create_token(username):
    payload = {
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)  # Use timezone-aware UTC time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def create_user(username, password, permissions):
    salt = Encryption.generate_salt()
    hashed_password = Encryption.hash_password(password, salt)
    db.add_user(username, hashed_password, salt, permissions)
    logger.info(f"User {username} created successfully.")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    #print(f"{data}") #debug, for delete
    username = data.get("username")
    password = data.get("password")
    #print(f"{username} and {password}") #debug, for delete
    user = db.get_user(username)
    
    if user:
        stored_password, salt, permissions = user[2], user[3], user[4]
        if Encryption.verify_password(stored_password, password, salt):
            token = create_token(username)
            logger.info(f"{username} authenticated successfully.")
            return jsonify({"status": "success", "token": token, "permissions": permissions}), 200
    return jsonify({"status": "failed", "message": "Authentication failed"}), 401

@app.route('/create_user', methods=['POST'])
def api_create_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    permissions = data.get("permissions", 1)  # Права по умолчанию

    if db.get_user(username) is not None:
        return jsonify({"status": "failed", "message": "User already exists."}), 400
    
    create_user(username, password, permissions)
    logger.info(f"User [{username}] was created with permissions [{permissions}].")
    return jsonify({"status": "success", "message": "User created successfully."}), 201

@app.route('/get_chats', methods=['GET'])
def get_chats():
    token = request.headers.get("Authorization")
    if not token or not verify_token(token.split(" ")[1]):
        return jsonify({"status": "failed", "message": "Unauthorized"}), 401
    
    permissions = request.args.get("permissions", type=int)
    chats = db.get_chats_for_user(permissions)
    logger.info("Sent chat list to user.")
    return jsonify(chats), 200
   
@app.route('/get_users', methods =['GET'])
#/get_users (GET) -  получение списка всех пользователей ( rec perm 4)

@app.route('/get_chats', methods = ['GET'])


@app.route('/add_chat', methods = ['POST'])
#/add_chat (POST) - создание чата: chat_name, permission (def 1, max 4). (Rec perm 4)
def  add_chat():
    data = request.get_json()
    
    # Проверка на наличие данных
    if not data or 'name' not in data or 'permissions' not in data:
        return jsonify({"status": "failed", "message": "Invalid input."}), 401
    
    chatname = data["name"]
    permissions = data["permissions"]
    status = data.get("status", "Offline")
    if db.get_chat(chatname) is not None:
        return jsonify({"status": "failed", "message": "Chat already exists."}), 400
    
    db.add_chat(chatname, permissions, status)
    return jsonify({"status": "success", "message": "Chat created successfully."}), 201
    logger.info(f"Chat [{chatname}] was created with permissions [{permissions}] and status '{status}'.")

@app.route('/change_user_perm', methods = ['POST'])
#/change_user_perm (POST) - (rec perm 4)

@app.route('/change_chat_perm', methods = ['POST'])
#/change_chat_perm (POST) - (rec perm 4)

@app.route('/disable_user', methods = ['POST'])
#/disable_user (POST) - (rec perm 4)

@app.route('/disable_chat', methods = ['POST'])
#/disable_chat (POST) - chat_id (rec perm 4)

@socketio.on('join_chat')
def on_join(data):
    username = data['username']
    chat_id = data['chat_id']
    join_room(chat_id)
    logger.info(f"{username} joined chat {chat_id}.")
    emit('message', {'username': 'Server', 'message': f"{username} has joined the chat."}, room=chat_id)

@socketio.on('leave_chat')
def on_leave(data):
    username = data['username']
    chat_id = data['chat_id']
    leave_room(chat_id)
    logger.info(f"{username} left chat {chat_id}.")
    emit('message', {'username': 'Server', 'message': f"{username} has left the chat."}, room=chat_id)

@socketio.on('send_message')
def handle_message(data):
    username = data['username']
    chat_id = data['chat_id']
    message = data['message']
    db.save_message(chat_id, username, message)
    #logger.info(f"{username} sent message to chat {chat_id}: {message}")
    emit('message', {'username': username, 'message': message}, room=chat_id)

def create_user_console():
    AnyAdmins=db.get_user_adm()
    isAnyAdmins=AnyAdmins[0][1]
    if isAnyAdmins == None:
        print(f"No admin user was found...")
        while True:
            username = input("Enter username (or 'exit' to quit): ")
            if username.lower() == 'exit':
                break
            password = input("Enter password: ")
            permissions = int(input("Enter permissions level (1-3 for user, 4 for admin): "))
            if permissions < 0 or permissions > 4:
                print("Error: Permissions level must be between 0 and 4. Please try again.")
                continue  # Запросить ввод заново
            create_user(username, password, permissions)
            print(f"User {username} created successfully.")
    else:
        print(f"Admin user was found, continue starting...")
        print(f"One of them: {isAnyAdmins}")


if __name__ == "__main__":
    create_user_console()  # Запускаем консоль для создания админа, если такового нет
    socketio.run(app, host=config['SERVER']['IP'], port=int(config['SERVER']['PORT']), debug=True)
