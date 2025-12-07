import cv2
import numpy as np
import scipy.ndimage
from skimage.filters import threshold_otsu

def detection(payload):
    # 1. Проверка входных данных
    if payload is None:
        return None, None, None
    
    # 2. Загрузка изображения с проверкой
    try:
        if isinstance(payload, str):
            import os
            if not os.path.exists(payload):
                print(f"Файл не найден: {payload}")
                return None, None, None
            img = cv2.imread(payload, cv2.IMREAD_GRAYSCALE)
        elif isinstance(payload, np.ndarray):
            img = cv2.cvtColor(payload, cv2.COLOR_BGR2GRAY) if len(payload.shape) == 3 else payload
        elif isinstance(payload, bytes):
            img = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_GRAYSCALE)
        else:
            print(f"Неподдерживаемый тип данных: {type(payload)}")
            return None, None, None
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return None, None, None
    
    # 3. Проверка, что изображение загружено
    if img is None:
        print("Не удалось загрузить изображение")
        return None, None, None
    
    # 4. Проверка размера изображения
    if img.size == 0:
        print("Пустое изображение")
        return None, None, None
    
    # 5. Медианная фильтрация с проверкой
    try:
        median_filtered = scipy.ndimage.median_filter(img, size=3)
    except Exception as e:
        print(f"Ошибка медианной фильтрации: {e}")
        median_filtered = img
    
    # 6. Порог Оцу с проверкой
    try:
        threshold = threshold_otsu(median_filtered)
        
        # Проверка порога
        if threshold > 173 or threshold < 80:
            print(f"Порог вне допустимого диапазона: {threshold}")
            return None, None, None
    except Exception as e:
        print(f"Ошибка вычисления порога Оцу: {e}")
        return None, None, None
    
    # 7. Бинаризация
    try:
        predicted = np.uint8(median_filtered > threshold) * 255
        
    except Exception as e:
        print(f"Ошибка бинаризации: {e}")
        return None, None, None
    
    # 8. Пороговая обработка OpenCV
    try:
        _, thresh = cv2.threshold(img, threshold + 10, 255, cv2.THRESH_BINARY_INV)
    except Exception as e:
        print(f"Ошибка пороговой обработки: {e}")
        return None, None, None
    
    # 9. Поиск контуров
    try:
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            print("Контуры не найдены")
            return None, None, None
        
        # Проверяем что контуры не пустые
        contours = [c for c in contours if len(c) > 0]
        if not contours:
            print("Все контуры пустые")
            return None, None, None
    except Exception as e:
        print(f"Ошибка поиска контуров: {e}")
        return None, None, None
    
    # 10. Находим самый большой контур
    try:
        cnt = max(contours, key=cv2.contourArea)
        
        # Фильтрация по площади
        if cv2.contourArea(cnt) < 1:
            print(f"Контур слишком маленький: {cv2.contourArea(cnt)}")
            return None, None, None
    except ValueError as e:
        print(f"Ошибка поиска максимального контура: {e}")
        return None, None, None
    except Exception as e:
        print(f"Ошибка при работе с контурами: {e}")
        return None, None, None
    
    # 11. Вычисляем моменты
    try:
        M = cv2.moments(cnt)
        
        if M["m00"] == 0:
            print("Момент m00 равен нулю")
            return None, None, None
    except Exception as e:
        print(f"Ошибка вычисления моментов: {e}")
        return None, None, None
    
    # 12. Возвращаем результат с проверкой
    if predicted is not None and cnt is not None and M is not None:
        return predicted, cnt, M
    
    return None, None, None