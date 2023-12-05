import hashlib
import hmac
import os
from typing import Union, List

from Cryptodome.Cipher import AES

from app.log import log, logger

# from Crypto.Cipher import AES # 如果上面的导入失败，可以尝试使用这个

SQLITE_FILE_HEADER = "SQLite format 3\x00"  # SQLite文件头

KEY_SIZE = 32
DEFAULT_PAGESIZE = 4096
DEFAULT_ITER = 64000


# 通过密钥解密数据库
@log
def decrypt(key: str, db_path, out_path):
    if not os.path.exists(db_path):
        return f"[-] db_path:'{db_path}' File not found!"
    if not os.path.exists(os.path.dirname(out_path)):
        return f"[-] out_path:'{out_path}' File not found!"
    if len(key) != 64:
        logger.error(f"[-] key:'{key}' Error!")
        return -1
    password = bytes.fromhex(key.strip())
    with open(db_path, "rb") as file:
        blist = file.read()

    salt = blist[:16]
    byteKey = hashlib.pbkdf2_hmac("sha1", password, salt, DEFAULT_ITER, KEY_SIZE)
    first = blist[16:DEFAULT_PAGESIZE]

    mac_salt = bytes([(salt[i] ^ 58) for i in range(16)])
    mac_key = hashlib.pbkdf2_hmac("sha1", byteKey, mac_salt, 2, KEY_SIZE)
    hash_mac = hmac.new(mac_key, first[:-32], hashlib.sha1)
    hash_mac.update(b'\x01\x00\x00\x00')

    if hash_mac.digest() != first[-32:-12]:
        logger.error(f"[-] Password Error! (key:'{key}'; db_path:'{db_path}'; out_path:'{out_path}' )")
        return -1

    newblist = [blist[i:i + DEFAULT_PAGESIZE] for i in range(DEFAULT_PAGESIZE, len(blist), DEFAULT_PAGESIZE)]

    with open(out_path, "wb") as deFile:
        deFile.write(SQLITE_FILE_HEADER.encode())
        t = AES.new(byteKey, AES.MODE_CBC, first[-48:-32])
        decrypted = t.decrypt(first[:-48])
        deFile.write(decrypted)
        deFile.write(first[-48:])

        for i in newblist:
            t = AES.new(byteKey, AES.MODE_CBC, i[-48:-32])
            decrypted = t.decrypt(i[:-48])
            deFile.write(decrypted)
            deFile.write(i[-48:])
    return [True, db_path, out_path, key]


@log
def batch_decrypt(key: str, db_path: Union[str, List[str]], out_path: str):
    if not isinstance(key, str) or not isinstance(out_path, str) or not os.path.exists(out_path) or len(key) != 64:
        return f"[-] (key:'{key}' or out_path:'{out_path}') Error!"

    process_list = []

    if isinstance(db_path, str):
        if not os.path.exists(db_path):
            return f"[-] db_path:'{db_path}' not found!"

        if os.path.isfile(db_path):
            inpath = db_path
            outpath = os.path.join(out_path, 'de_' + os.path.basename(db_path))
            process_list.append([key, inpath, outpath])

        elif os.path.isdir(db_path):
            for root, dirs, files in os.walk(db_path):
                for file in files:
                    inpath = os.path.join(root, file)
                    rel = os.path.relpath(root, db_path)
                    outpath = os.path.join(out_path, rel, 'de_' + file)

                    if not os.path.exists(os.path.dirname(outpath)):
                        os.makedirs(os.path.dirname(outpath))
                    process_list.append([key, inpath, outpath])
        else:
            return f"[-] db_path:'{db_path}' Error "
    elif isinstance(db_path, list):
        rt_path = os.path.commonprefix(db_path)
        if not os.path.exists(rt_path):
            rt_path = os.path.dirname(rt_path)

        for inpath in db_path:
            if not os.path.exists(inpath):
                return f"[-] db_path:'{db_path}' not found!"

            inpath = os.path.normpath(inpath)
            rel = os.path.relpath(os.path.dirname(inpath), rt_path)
            outpath = os.path.join(out_path, rel, 'de_' + os.path.basename(inpath))
            if not os.path.exists(os.path.dirname(outpath)):
                os.makedirs(os.path.dirname(outpath))
            process_list.append([key, inpath, outpath])
    else:
        return f"[-] db_path:'{db_path}' Error "

    result = []
    for i in process_list:
        result.append(decrypt(*i))  # 解密

    # 删除空文件夹
    for root, dirs, files in os.walk(out_path, topdown=False):
        for dir in dirs:
            if not os.listdir(os.path.join(root, dir)):
                os.rmdir(os.path.join(root, dir))
    return result


if __name__ == '__main__':
    # 调用 decrypt 函数，并传入参数
    key = "2aafab10af7940328bb92ac9d2a8ab5fc07a685646b14f2e9ae6948a7060c0fc"
    db_path = "E:\86390\Documents\WeChat Files\wxid_27hqbq7vx5hf22\FileStorage\CustomEmotion\\71\\71CE49ED3CE9E57E43E07F802983BF45"
    out_path = "./test/1.png"
    print(decrypt(key, db_path, out_path))
