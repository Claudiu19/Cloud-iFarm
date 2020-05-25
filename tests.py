import uuid
import re
print(uuid.uuid4().hex + uuid.uuid4().hex + uuid.uuid4().hex)

def check_keys_format(key):
    if len(key) != 96:
        return False
    if re.match("^[a-z0-9]*$", key):
        return True
    else:
        return False


print(check_keys_format("5d39e5ac3bb645f9ab91195a4b084995e90b2ec5441844a595d621270c27a2b3b01c079ffa4a4bbcabfca9a33c1163c9"))
