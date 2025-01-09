import json


# Функция для сохранения обновлённого списка заблокированных пользователей в JSON файл
def save_banned_users(banned_users):
    with open('restricted_users.json', 'w', encoding='utf-8') as file:
        json.dump(banned_users, file, indent=4)


# Функция для загрузки списка заблокированных пользователей из JSON файла
def load_banned_users():
    try:
        with open('restricted_users.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        # Если файл не существует, создаём новый с пустым списком заблокированных
        return {"banned": []}
