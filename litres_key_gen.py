from hashlib import sha256


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


def keygen(str_to_key):
    key = str_to_sha256(shake_string(str_to_key))

    return key[8:28]


# print(keygen("litres202502@n-drive.cf"))
# print(keygen("kitres202502@n-drive.cf"))
