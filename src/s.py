import socket
import struct
import cv2
import logging
from typing import Optional, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импорт функций (с обработкой ошибок)
try:
    from src.detection import detection
except ImportError as e:
    logger.error(f"Ошибка импорта модуля detection: {e}")
    detection = None

HOST = "127.0.0.1"
PORT = 8888

def validate_coordinates(x: int, y: int, w: int, h: int, cx: int, cy: int) -> bool:
    """Проверка корректности координат"""
    if w <= 0 or h <= 0:
        logger.warning(f"Некорректные размеры: w={w}, h={h}")
        return False
    
    # Проверяем что центр внутри прямоугольника (с допуском)
    if not (x <= cx <= x + w and y <= cy <= y + h):
        logger.warning(f"Центр вне прямоугольника: rect=({x},{y},{w},{h}), center=({cx},{cy})")
        return False
    
    # Проверка на разумные пределы (можно настроить под вашу задачу)
    MAX_DIMENSION = 513
    if abs(x) > MAX_DIMENSION or abs(y) > MAX_DIMENSION or w > MAX_DIMENSION or h > MAX_DIMENSION:
        logger.warning(f"Координаты выходят за пределы: x={x}, y={y}, w={w}, h={h}")
        return False
    
    return True

def create_reply(x: int, y: int, w: int, h: int, cx: int, cy: int) -> Optional[bytes]:
    """Создание безопасного ответа"""
    try:
        # Ограничиваем значения разумными пределами
        x = max(-2147483648, min(2147483647, x))
        y = max(-2147483648, min(2147483647, y))
        w = max(0, min(65535, w))
        h = max(0, min(65535, h))
        cx = max(-2147483648, min(2147483647, cx))
        cy = max(-2147483648, min(2147483647, cy))
        # Проверяем координаты
        if not validate_coordinates(x, y, w, h, cx, cy):
            return None
        
        # Упаковываем в little-endian
        reply = (x.to_bytes(4, "little", signed=True) + 
                y.to_bytes(4, "little", signed=True) +
                w.to_bytes(4, "little", signed=False) +
                h.to_bytes(4, "little", signed=False) +
                cx.to_bytes(4, "little", signed=True) +
                cy.to_bytes(4, "little", signed=True))
        
        return reply
    except Exception as e:
        logger.error(f"Ошибка создания ответа: {e}")
        return None

def main():
    if detection is None:
        logger.error("Модуль detection недоступен, завершение работы")
        return
    
    # Создание сокета с таймаутами
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Устанавливаем таймауты
    server.settimeout(5.0)  # таймаут на операции с сокетом
    
    try:
        server.bind((HOST, PORT))
        logger.info(f"UDP сервер запущен на {HOST}:{PORT}")
    except socket.error as e:
        logger.error(f"Ошибка привязки сокета: {e}")
        return
    except OSError as e:
        logger.error(f"Ошибка ОС при привязке сокета: {e}")
        return
    
    packet_counter = 0
    error_counter = 0
    MAX_ERRORS = 100
    
    while True:
        try:
            # Получение данных
            try:
                data, addr = server.recvfrom(65507)
            except socket.timeout:
                logger.debug("Таймаут ожидания данных")
                continue
            except ConnectionResetError:
                logger.warning("Соединение сброшено клиентом")
                continue
            except OSError as e:
                logger.error(f"Ошибка ОС при получении данных: {e}")
                error_counter += 1
                if error_counter > MAX_ERRORS:
                    logger.error("Слишком много ошибок, завершение работы")
                    break
                continue
            
            packet_counter += 1
            if packet_counter % 100 == 0:
                logger.info(f"Обработано пакетов: {packet_counter}")
            
            # Проверка размера пакета
            if len(data) < 4:
                logger.warning(f"Пакет слишком мал: {len(data)} байт")
                continue
            
            # Извлечение размера с проверкой
            try:
                size = struct.unpack("<I", data[:4])[0]
            except struct.error as e:
                logger.warning(f"Ошибка распаковки размера пакета: {e}")
                continue
            
            # Проверка соответствия размера
            if size != len(data) - 4:
                logger.warning(f"Несоответствие размеров: заголовок={size}, фактически={len(data)-4}")
            
            payload = data[4:]
            
            # Проверка что payload не пустой
            if not payload:
                logger.warning("Пустой payload")
                continue
            
            # Обработка через detection
            try:
                _, cnt, M = detection(payload)
            except Exception as e:
                logger.error(f"Ошибка в функции detection: {e}")
                continue
            
            # Проверка результата detection
            if cnt is None or M is None:
                logger.debug("Объект не обнаружен")
                continue
            
            # Вычисление boundingRect с проверкой
            try:
                x, y, w, h = cv2.boundingRect(cnt)
            except Exception as e:
                logger.error(f"Ошибка вычисления boundingRect: {e}")
                continue
            
            # Проверка моментов перед делением
            if M["m00"] == 0:
                logger.warning("Нулевой момент m00")
                continue
            
            # Вычисление центра
            try:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            except (ValueError, ZeroDivisionError) as e:
                logger.error(f"Ошибка вычисления центра: {e}")
                continue
            
            # Создание ответа
            reply = create_reply(x, y, w, h, cx, cy)
            if reply is None:
                logger.warning("Некорректные координаты для ответа")
                continue
            
            # Отправка ответа
            try:
                server.sendto(reply, addr)
                logger.debug(f"Отправлен ответ клиенту {addr}")
            except socket.error as e:
                logger.error(f"Ошибка отправки ответа: {e}")
                continue
            except OSError as e:
                logger.error(f"Ошибка ОС при отправке: {e}")
                continue
            
            error_counter = 0  # Сбрасываем счетчик ошибок при успешной обработке
            
        except KeyboardInterrupt:
            logger.info("Получен сигнал завершения")
            break
        except Exception as e:
            logger.error(f"Неожиданная ошибка в основном цикле: {e}", exc_info=True)
            error_counter += 1
            if error_counter > MAX_ERRORS:
                logger.error("Слишком много ошибок, завершение работы")
                break
    
    # Закрытие сокета
    try:
        server.close()
        logger.info("Сокет закрыт")
    except Exception as e:
        logger.error(f"Ошибка при закрытии сокета: {e}")