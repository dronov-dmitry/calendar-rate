import json
import urllib.error
import urllib.request
import argparse
import sys
import ssl
from datetime import datetime

try:
    import certifi
except ImportError:
    certifi = None


DEFAULT_API_URL = "https://calendar-logger-api.dronov-dmitry-bim.workers.dev/api/log"


def parse_amount(value):
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        raise argparse.ArgumentTypeError("amount должен быть числом, например 1 или 12.5")


def main():
    # Настройка парсера аргументов
    parser = argparse.ArgumentParser(description="Отправка данных в Calendar Logger API")
    
    # Обязательные аргументы
    parser.add_argument('--key', required=True, help='Ваш API ключ (X-API-Key)')
    parser.add_argument('--name', required=True, help='Название активности (например, steps)')
    parser.add_argument('--amount', required=True, type=parse_amount, help='Значение/количество')
    
    # Необязательные аргументы
    parser.add_argument('--type', default='count', help='Тип данных (по умолчанию: count)')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'), 
                        help='Дата в формате YYYY-MM-DD (по умолчанию: сегодня)')
    parser.add_argument('--url', default=DEFAULT_API_URL,
                        help='URL API (есть значение по умолчанию)')

    args = parser.parse_args()

    # Формирование данных
    json_data = {
        'name': args.name,
        'type': args.type,
        'amount': args.amount,
        'date': args.date
    }

    encoded_data = json.dumps(json_data).encode('utf-8')

    headers = {
        'X-API-Key': args.key, 
        'Content-Type': 'application/json',
        'User-Agent': 'CalendarLoggerPythonClient/1.0'
    }

    # Создание запроса
    req = urllib.request.Request(args.url, data=encoded_data, headers=headers, method='POST')

    # --- РЕШЕНИЕ ПРОБЛЕМЫ SSL ---
    try:
        # Используем сертификаты из пакета certifi для проверки SSL
        context = ssl.create_default_context(cafile=certifi.where() if certifi else None)
    except Exception:
        # Если что-то пошло не так, откатываемся к стандартному контексту
        context = ssl.create_default_context()
    # ----------------------------

    try:
        print(f"Отправка данных: {json_data}...")
        
        # Добавляем аргумент context=context
        with urllib.request.urlopen(req, context=context, timeout=20) as response:
            print("OK: Успех!")
            print(response.read().decode('utf-8'))

    except urllib.error.HTTPError as e:
        print(f"ERROR: Произошла ошибка сервера: {e.code}")
        error_message = e.read().decode('utf-8', errors='replace')
        print(f"Ответ сервера: {error_message}")
        sys.exit(1)

    except urllib.error.URLError as e:
        print(f"ERROR: Не удалось связаться с сервером: {e.reason}")
        # Если ошибка SSL все еще лезет, выводим подсказку
        if "CERTIFICATE_VERIFY_FAILED" in str(e.reason):
            print("Подсказка: Попробуйте обновить certifi (pip install --upgrade certifi)")
        sys.exit(1)

if __name__ == "__main__":
    main()
