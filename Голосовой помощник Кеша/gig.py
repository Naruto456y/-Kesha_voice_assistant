import requests
import base64
import uuid
from urllib.parse import urlencode
import json

# ВСТАВЬТЕ СЮДА ВАШИ ДАННЫЕ:
CLIENT_ID = "b3b26ea0-61d9-4e48-9097-3c8524efae28"      # ← ЗАМЕНИТЕ
CLIENT_SECRET = "e746bfd6-d42f-4aa7-aee3-8145bb9a0e24"  # ← ЗАМЕНИТЕ

def get_gigachat_token():
    """Получает токен доступа с правильными заголовками"""
    # Кодируем client_id:client_secret в base64
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": f"Basic {encoded_credentials}",
        "RqUID": str(uuid.uuid4()),  # Уникальный ID для каждого запроса
    }
    
    # Правильно формируем данные
    data = {
        "scope": "GIGACHAT_API_PERS"
    }
    
    try:
        # Используем data=urlencode(data) для правильного формата
        response = requests.post(
            url, 
            headers=headers, 
            data=urlencode(data),
            verify=False,  # Отключаем проверку SSL для теста
            timeout=30
        )
        
        print(f"Статус ответа: {response.status_code}")
        print(f"Ответ сервера: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"Ошибка получения токена: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Исключение: {e}")
        return None

def ask_gigachat(question: str):
    """Задаем вопрос GigaChat"""
    print("Получаем токен...")
    token = get_gigachat_token()
    
    if not token:
        print("Не удалось получить токен. Проверьте Client ID и Client Secret.")
        return None
    
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": question}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            json=data, 
            verify=False,
            timeout=30
        )
        
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"Ошибка GigaChat API: {response.text}")
            return None
            
    except Exception as e:
        print(f"Ошибка при запросе: {e}")
        return None

# Отключаем SSL предупреждения
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)