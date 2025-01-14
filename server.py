import socket
import threading
import os
from jinja2 import Environment, FileSystemLoader

HOST = 'localhost'
PORT = 8080
DOCUMENT_ROOT = './templates'  # Папка с шаблонами

# Создаем объект окружения Jinja2, указывая папку с шаблонами
env = Environment(loader=FileSystemLoader(DOCUMENT_ROOT))

def handle_request(client_socket):
    try:
        # 1. Получаем запрос от клиента
        request_data = client_socket.recv(1024).decode('utf-8')
        if not request_data:
            return

        # 2. Разбираем запрос
        request_lines = request_data.splitlines()
        request_line = request_lines[0]  # Первая строка запроса
        method, path, http_version = request_line.split()

        # Собираем заголовки запроса в словарь
        headers = {}
        for line in request_lines[1:]:
            if line == '':
                break  # Пустая строка означает конец заголовков
            header_name, header_value = line.split(":", 1)
            headers[header_name.strip()] = header_value.strip()

        # Форматируем заголовки для отображения
        headers_formatted = '\n'.join(f"{name}: {value}" for name, value in headers.items())

        if method in ['GET', 'HEAD']:
            # Устанавливаем путь к запрашиваемому файлу
            if path == '/':
                template_name = 'index.html'
            else:
                # Удаляем ведущий слэш и предотвращаем выход из директории с шаблонами
                template_name = path.lstrip('/').replace('..', '')

            try:
                # Загружаем шаблон
                template = env.get_template(template_name)

                # Рендерим шаблон с данными
                content = template.render(method=method, path=path, headers=headers_formatted)
                response_body = content.encode('utf-8')

                # Формируем успешный HTTP-ответ
                response_headers = 'HTTP/1.1 200 OK\r\n'
                response_headers += f'Content-Length: {len(response_body)}\r\n'
                response_headers += 'Content-Type: text/html; charset=utf-8\r\n'
                response_headers += 'Connection: close\r\n'
                response_headers += '\r\n'

                if method == 'GET':
                    # Отправляем заголовки и тело ответа
                    client_socket.send(response_headers.encode('utf-8') + response_body)
                elif method == 'HEAD':
                    # Отправляем только заголовки
                    client_socket.send(response_headers.encode('utf-8'))
            except Exception as e:
                # Если шаблон не найден или ошибка при рендеринге, отправляем 404 Not Found
                response_body = '<h1>404 Not Found</h1>'.encode('utf-8')
                response_headers = 'HTTP/1.1 404 Not Found\r\n'
                response_headers += f'Content-Length: {len(response_body)}\r\n'
                response_headers += 'Content-Type: text/html; charset=utf-8\r\n'
                response_headers += 'Connection: close\r\n'
                response_headers += '\r\n'
                client_socket.send(response_headers.encode('utf-8') + response_body)
        else:
            # Метод не поддерживается, отправляем 405 Method Not Allowed
            response_body = '<h1>405 Method Not Allowed</h1>'.encode('utf-8')
            response_headers = 'HTTP/1.1 405 Method Not Allowed\r\n'
            response_headers += f'Content-Length: {len(response_body)}\r\n'
            response_headers += 'Content-Type: text/html; charset=utf-8\r\n'
            response_headers += 'Connection: close\r\n'
            response_headers += '\r\n'
            client_socket.send(response_headers.encode('utf-8') + response_body)
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
    finally:
        client_socket.close()

def start_server():
    # 1. Создаем сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Позволяем повторно использовать адрес порта
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 2. Привязываем сокет к адресу и порту
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Сервер запущен на {HOST}:{PORT}")

    try:
        while True:
            # 3. Принимаем соединения в цикле
            client_socket, client_address = server_socket.accept()
            print(f"Подключен клиент: {client_address}")
            # Создаем новый поток для обработки запроса
            thread = threading.Thread(target=handle_request, args=(client_socket,))
            thread.start()
    except KeyboardInterrupt:
        print("\nОстановка сервера.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()