import os

def imgDstr():
    path = "img"

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        os.remove(file_path)

    f = open("img/.gitkeep", "w")
    f.close()