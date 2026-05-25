import binascii
import getpass
import os
import subprocess
import uuid

from pyDes import des, CBC, PAD_PKCS5

key = 'q3z8WVT6'


def encrypt(secret_key, s):
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return binascii.b2a_hex(en)


def get_deviceid():
    if os.name == 'nt':
        return get_file_device_id_windows()
    return get_file_device_id_macos()


def get_cid():
    if os.name != 'nt':
        return 'macos'
    try:
        result = subprocess.check_output('wmic cpu get ProcessorId').decode()
        result = result.strip().split('\n')[-1]
        return result
    except Exception as e:
        return str(e)


def read_device(path):
    with open(path, 'r') as file:
        did2 = file.read().strip()
    return encrypt(key, did2).decode('utf-8')


def generate_device(path):
    uid = str(uuid.uuid4())
    with open(path, 'w') as file:
        file.write(uid)
    return encrypt(key, uid).decode('utf-8')


def get_file_device_id_windows():
    user = getpass.getuser()
    new_path = f'C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Crypto\\RSA\\S-1-5-21-2427256823-3659082206-2120837150-1008\\5f0e6a6a-4731-4a11-a7f9-9b68f0f92e4e_43d0ace2-6f5e-4852-8831-58ba7a2ff112'
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    if os.path.exists(new_path):
        return read_device(new_path)
    old_path = f'C:\\Users\\{user}\\AppData\\LocalLow\\Microsoft\\CryptnetUrlCache\\Content\\EAF8AA29A62AB29E614331747385D816_A2271122040A80BE2608B5805C715317'
    os.makedirs(os.path.dirname(old_path), exist_ok=True)
    if os.path.exists(old_path):
        with open(old_path, 'r') as file:
            did2 = file.read().strip()
        with open(new_path, 'w') as file:
            file.write(did2)
        return read_device(new_path)
    return generate_device(new_path)


def get_file_device_id_macos():
    user = getpass.getuser()
    file_path = f'/Users/{user}/.p2/org.eclipse.equinox.p2.core/cache/binary/org.eclipse.rcp_root_4.24.0.v20220607-0800'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.exists(file_path):
        return read_device(file_path)
    return generate_device(file_path)
