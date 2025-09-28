from hashlib import sha256
import re


def shake_string(str_to_shake):
    ind = 0
    l1 = []
    l2 = []
    for char in list(str_to_shake):
        if ind % 2 == 0:
            l1.append(char)
        else:
            l2.append(char)
        ind += 1
    return "".join(l1 + l2)


def str_to_sha256(str_to_hash):
    hash = str(sha256(str_to_hash.encode("utf-8")).hexdigest())
    return hash


def extract_email(text):
    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    # Поиск первого совпадения
    match = re.search(email_regex, text)
    if match:
        return match.group(0)  # Возвращаем найденную строку
    else:
        return None  # Возвращаем None, если адрес не найден


def keygen(str_to_key):
    email = extract_email(str_to_key)

    if email == None:
        return "В качестве параметра необходимо передать email"
    else:
        key = str_to_sha256(shake_string(email))
        return key[8:28]


# print(keygen("litres202502@n-drive.cf"))
# print(keygen("kitres202502@n-drive.cf"))
