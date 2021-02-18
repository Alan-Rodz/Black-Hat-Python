import os


def run():
    print("[*] Dirlister Module.")
    files = os.listdir(".")

    return str(files)
