import os

path = "img"

for filename in os.listdir(path):
    # Собрать полный путь к файлу
    file_path = os.path.join(path, filename)
    # Удалить файл
    os.remove(file_path)

f = open("img/.gitkeep", "w")
f.close()