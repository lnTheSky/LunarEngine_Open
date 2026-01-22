__all__ = []


def __dir__():
    return []


from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from hashlib import pbkdf2_hmac
from datetime import datetime
from os import urandom
import subprocess
from pickle import dumps, loads
import requests
import ntplib
import base64
import struct
import time


__edp = urandom(32)


# Dynamic encryption
def derive_key(password: bytes, salt, iterations=200):
    key = pbkdf2_hmac('sha256', password, salt, iterations)
    return key


def pad(data):
    padding_length = 16 - (len(data) % 16)
    return data + bytes([padding_length] * padding_length)


def unpad(data):
    padding_length = data[-1]
    return data[:-padding_length]


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def encrypt_block(block, key):
    return xor_bytes(block, key[:16])


def decrypt_block(block, key):
    return xor_bytes(block, key[:16])


def encrypt(data: bytes, password: bytes = __edp):
    salt = urandom(16)
    iv = urandom(16)

    key = derive_key(password, salt)
    data = pad(data)

    encrypted_data = b''
    previous_block = iv
    for i in range(0, len(data), 16):
        block = data[i:i + 16]
        block = xor_bytes(block, previous_block)
        encrypted_block = encrypt_block(block, key)
        encrypted_data += encrypted_block
        previous_block = encrypted_block

    return salt + iv + encrypted_data


def decrypt(encrypted_data: bytes, password: bytes = __edp):
    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    encrypted_message = encrypted_data[32:]

    key = derive_key(password, salt)

    decrypted_data = b''
    previous_block = iv
    for i in range(0, len(encrypted_message), 16):
        block = encrypted_message[i:i + 16]
        decrypted_block = decrypt_block(block, key)
        decrypted_block = xor_bytes(decrypted_block, previous_block)
        decrypted_data += decrypted_block
        previous_block = block

    return unpad(decrypted_data)


__edp = urandom(32)


class UIDError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


def get_uid():
    failure_count = -1
    try:
        uid = subprocess.check_output('wmic diskdrive get SerialNumber').decode().split('\n')[1:]
        uid = [s.strip() for s in uid if s.strip()]
    except:
        uid = []
        failure_count += 1
        print('[License] [W]: UID 1 Failure')
    uid.append('1983279f87ds98f7n892379487nas980')
    
    try:
        uid.append(subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip())
        # uid.append
    except:
        failure_count += 1
        print('[License] [W]: UID 2 Failure')

    try:
        uid.append(subprocess.check_output('powershell.exe Get-WmiObject Win32_ComputerSystemProduct | Select-Object UUID').decode().split('\n')[3].strip())
    except:
        failure_count += 1
        print('[License] [W]: UID 3 Failure')
    
    try:
        serials = subprocess.check_output('powershell.exe Get-WmiObject Win32_DiskDrive | Select-Object SerialNumber').decode().strip().split('\r\n')[2:]
        serials = [i.strip() for i in serials]
        uid += serials
        del serials
    except:
        failure_count += 1
        print('[License] [W]: UID 4 Failure')
    
    if failure_count == 4:
        print('[License] [F]: Cannot generate UID for the PC. Try to install WMIC or add powershell.exe to the PATH')
        raise UIDError

    return encrypt(SHA256.SHA256Hash(bytes(''.join(uid), encoding='utf-8')).digest(), __edp)


def is_online() -> bool:
    import socket

    for host in '8.8.8.8', '223.5.5.5':  # Google, AliDNS:
        try:
            test_connection = socket.create_connection(address=(host, 53), timeout=2)
        except (socket.timeout, socket.gaierror, OSError):
            continue
        else:
            test_connection.close()
            return True
    return False


# def is_online():
#     return True


# def check_online(timeout=1):
#     try:
#         requests.head("http://www.google.com/", timeout=timeout)
#         return True
#     except requests.ConnectionError:
#         return False
#     except requests.ReadTimeout:
#         return check_online(timeout + 1)

def get_time():
    time_list = []
    client = ntplib.NTPClient()
    try:
        response = client.request('pool.ntp.org', version=3)
        time_list.append(datetime.fromtimestamp(int(response.tx_timestamp - 2208988800)))
    except:
        print('[Time] [F]: Server 0 is unavailable')
    try:
        response = client.request('time.google.com', version=3)
        time_list.append(datetime.fromtimestamp(int(response.tx_timestamp - 2208988800)))
    except:
        print('[Time] [F]: Server 1 is unavailable')
    
    time_list.append(datetime.fromtimestamp((time.time() + time.timezone + 10800)))

    return time_list

def get_time_new():
    # time_list = []
    timestamps = []
    client = ntplib.NTPClient()
    try:
        response = client.request('pool.ntp.org', version=3)
        timestamp = response.tx_time
        timestamps.append(timestamp)
    except:
        print('[Time] [F]: Server unavailable')
    try:
        response = client.request('time.google.com', version=3)
        # timestamp = int(response.tx_timestamp - 2208988800)
        timestamp = response.tx_time
        timestamps.append(timestamp)

        # time_list.append(datetime.fromtimestamp(timestamp))
    except:
        print('[Time] [F]: Server unavailable')
    # try:
    #     r = requests.get('https://www.timeapi.io/api/time/current/zone?timeZone=Europe%2FMoscow').json()
    #     date_1 = datetime(r['year'], r['month'], r['day'], r['hour'], r['minute'], r['seconds'], r['milliSeconds'] * 1000)
    #     date_2 = datetime.fromisoformat(r['dateTime'])
    #     ts_1 = date_1.timestamp()
    #     # ts_2 = date_2.timestamp() - date_2.timestamp() % 0.001
    #     ts_2 = float(str(date_2.timestamp())[:14])
    #     # print(ts_1, ts_2)
    #     if ts_1 == ts_2:
    #         timestamps.append(ts_1)
    # except Exception as e:
    #     # print(e)
    #     pass
    timestamps.append(time.time() + time.timezone + 10800)
    # print(timestamps, time.timezone)

    if len(timestamps) == 3:
        if abs(timestamps[0] - timestamps[1]) < 60001 and abs(timestamps[0] - timestamps[2]) < 60001 and abs(timestamps[2] - timestamps[1]) < 60001:
            return [datetime.fromtimestamp(max(timestamps))]
    else:
        return [datetime.fromtimestamp(max(timestamps))]


def generate_uid_file(public_1, version: bytes):

    public_key = serialization.load_pem_public_key(
        base64.decodebytes(public_1),
        backend=default_backend()
    )
    del public_1

    uid = public_key.encrypt(
        dumps((decrypt(get_uid(), __edp), version)),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    with open('uid.encrypted', 'wb') as file:
        file.write(uid)

    del uid

    return True


def open_license(private_2, version: bytes, lc_path: str, password=None):
    date = time.time()
    return 'J29dJ3ue87CV2987IUESNP1Phd83E3h', datetime.fromtimestamp(date+60*60*24*999), 3, datetime.fromtimestamp(date)


# def open_license(private_2, version: bytes, lc_path: str, password=None):
#     return 'J29dJ3ue87CV2987IUESNP1Phd83E3h', datetime.fromtimestamp(get_time()[0]), 3


def encrypt_model(file):
    pass


def decrypt_model(path):
    pass

