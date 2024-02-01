# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         get_base_addr.py
# Description:
# Author:       xaoyaoo
# Date:         2023/08/22
# -------------------------------------------------------------------------------
import argparse
import ctypes
import hashlib
import json
import multiprocessing
import os
import re
import sys

import psutil
from win32com.client import Dispatch
from pymem import Pymem
import pymem
import hmac

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p
KEY_SIZE = 32
DEFAULT_PAGESIZE = 4096
DEFAULT_ITER = 64000


def validate_key(key, salt, first, mac_salt):
    byteKey = hashlib.pbkdf2_hmac("sha1", key, salt, DEFAULT_ITER, KEY_SIZE)
    mac_key = hashlib.pbkdf2_hmac("sha1", byteKey, mac_salt, 2, KEY_SIZE)
    hash_mac = hmac.new(mac_key, first[:-32], hashlib.sha1)
    hash_mac.update(b'\x01\x00\x00\x00')

    if hash_mac.digest() == first[-32:-12]:
        return True
    else:
        return False


def get_exe_bit(file_path):
    """
    获取 PE 文件的位数: 32 位或 64 位
    :param file_path:  PE 文件路径(可执行文件)
    :return: 如果遇到错误则返回 64
    """
    try:
        with open(file_path, 'rb') as f:
            dos_header = f.read(2)
            if dos_header != b'MZ':
                print('get exe bit error: Invalid PE file')
                return 64
            # Seek to the offset of the PE signature
            f.seek(60)
            pe_offset_bytes = f.read(4)
            pe_offset = int.from_bytes(pe_offset_bytes, byteorder='little')

            # Seek to the Machine field in the PE header
            f.seek(pe_offset + 4)
            machine_bytes = f.read(2)
            machine = int.from_bytes(machine_bytes, byteorder='little')

            if machine == 0x14c:
                return 32
            elif machine == 0x8664:
                return 64
            else:
                print('get exe bit error: Unknown architecture: %s' % hex(machine))
                return 64
    except IOError:
        print('get exe bit error: File not found or cannot be opened')
        return 64


def get_exe_version(file_path):
    """
    获取 PE 文件的版本号
    :param file_path:  PE 文件路径(可执行文件)
    :return: 如果遇到错误则返回
    """
    file_version = Dispatch("Scripting.FileSystemObject").GetFileVersion(file_path)
    return file_version


def find_all(c: bytes, string: bytes, base_addr=0):
    """
    查找字符串中所有子串的位置
    :param c: 子串 b'123'
    :param string: 字符串 b'123456789123'
    :return:
    """
    return [base_addr + m.start() for m in re.finditer(re.escape(c), string)]


class BiasAddr:
    def __init__(self, account, mobile, name, key, db_path):
        self.account = account.encode("utf-8")
        self.mobile = mobile.encode("utf-8")
        self.name = name.encode("utf-8")
        self.key = bytes.fromhex(key) if key else b""
        self.db_path = db_path if db_path and os.path.exists(db_path) else ""

        self.process_name = "WeChat.exe"
        self.module_name = "WeChatWin.dll"

        self.pm = None  # Pymem 对象
        self.is_WoW64 = None  # True: 32位进程运行在64位系统上 False: 64位进程运行在64位系统上
        self.process_handle = None  # 进程句柄
        self.pid = None  # 进程ID
        self.version = None  # 微信版本号
        self.process = None  # 进程对象
        self.exe_path = None  # 微信路径
        self.address_len = None  # 4 if self.bits == 32 else 8  # 4字节或8字节
        self.bits = 64 if sys.maxsize > 2 ** 32 else 32  # 系统：32位或64位

    def get_process_handle(self):
        try:
            self.pm = Pymem(self.process_name)
            self.pm.check_wow64()
            self.is_WoW64 = self.pm.is_WoW64
            self.process_handle = self.pm.process_handle
            self.pid = self.pm.process_id
            self.process = psutil.Process(self.pid)
            self.exe_path = self.process.exe()
            self.version = get_exe_version(self.exe_path)

            version_nums = list(map(int, self.version.split(".")))  # 将版本号拆分为数字列表
            if version_nums[0] <= 3 and version_nums[1] <= 9 and version_nums[2] <= 2:
                self.address_len = 4
            else:
                self.address_len = 8
            return True, ""
        except pymem.exception.ProcessNotFound:
            return False, "[-] WeChat No Run"

    def search_memory_value(self, value: bytes, module_name="WeChatWin.dll"):
        # 创建 Pymem 对象
        module = pymem.process.module_from_name(self.pm.process_handle, module_name)
        ret = self.pm.pattern_scan_module(value, module, return_multiple=True)
        ret = ret[-1] - module.lpBaseOfDll if len(ret) > 0 else 0
        return ret

    def get_key_bias1(self):
        try:
            byteLen = self.address_len  # 4 if self.bits == 32 else 8  # 4字节或8字节

            keyLenOffset = 0x8c if self.bits == 32 else 0xd0
            keyWindllOffset = 0x90 if self.bits == 32 else 0xd8

            module = pymem.process.module_from_name(self.process_handle, self.module_name)
            keyBytes = b'-----BEGIN PUBLIC KEY-----\n...'
            publicKeyList = pymem.pattern.pattern_scan_all(self.process_handle, keyBytes, return_multiple=True)

            keyaddrs = []
            for addr in publicKeyList:
                keyBytes = addr.to_bytes(byteLen, byteorder="little", signed=True)  # 低位在前
                may_addrs = pymem.pattern.pattern_scan_module(self.process_handle, module, keyBytes,
                                                              return_multiple=True)
                if may_addrs != 0 and len(may_addrs) > 0:
                    for addr in may_addrs:
                        keyLen = self.pm.read_uchar(addr - keyLenOffset)
                        if keyLen != 32:
                            continue
                        keyaddrs.append(addr - keyWindllOffset)

            return keyaddrs[-1] - module.lpBaseOfDll if len(keyaddrs) > 0 else 0
        except:
            return 0

    def search_key(self, key: bytes):
        key = re.escape(key)  # 转义特殊字符
        key_addr = self.pm.pattern_scan_all(key, return_multiple=False)
        key = key_addr.to_bytes(self.address_len, byteorder='little', signed=True)
        result = self.search_memory_value(key, self.module_name)
        return result

    def get_key_bias2(self, wx_db_path):

        addr_len = get_exe_bit(self.exe_path) // 8
        db_path = wx_db_path

        def read_key_bytes(h_process, address, address_len=8):
            array = ctypes.create_string_buffer(address_len)
            if ReadProcessMemory(h_process, void_p(address), array, address_len, 0) == 0: return "None"
            address = int.from_bytes(array, byteorder='little')  # 逆序转换为int地址（key地址）
            key = ctypes.create_string_buffer(32)
            if ReadProcessMemory(h_process, void_p(address), key, 32, 0) == 0: return "None"
            key_bytes = bytes(key)
            return key_bytes

        def verify_key(key, wx_db_path):
            KEY_SIZE = 32
            DEFAULT_PAGESIZE = 4096
            DEFAULT_ITER = 64000
            with open(wx_db_path, "rb") as file:
                blist = file.read(5000)
            salt = blist[:16]
            byteKey = hashlib.pbkdf2_hmac("sha1", key, salt, DEFAULT_ITER, KEY_SIZE)
            first = blist[16:DEFAULT_PAGESIZE]

            mac_salt = bytes([(salt[i] ^ 58) for i in range(16)])
            mac_key = hashlib.pbkdf2_hmac("sha1", byteKey, mac_salt, 2, KEY_SIZE)
            hash_mac = hmac.new(mac_key, first[:-32], hashlib.sha1)
            hash_mac.update(b'\x01\x00\x00\x00')

            if hash_mac.digest() != first[-32:-12]:
                return False
            return True

        phone_type1 = "iphone\x00"
        phone_type2 = "android\x00"
        phone_type3 = "ipad\x00"

        pm = pymem.Pymem("WeChat.exe")
        module_name = "WeChatWin.dll"

        MicroMsg_path = os.path.join(db_path, "MSG", "MicroMsg.db")

        module = pymem.process.module_from_name(pm.process_handle, module_name)

        type1_addrs = pm.pattern_scan_module(phone_type1.encode(), module, return_multiple=True)
        type2_addrs = pm.pattern_scan_module(phone_type2.encode(), module, return_multiple=True)
        type3_addrs = pm.pattern_scan_module(phone_type3.encode(), module, return_multiple=True)
        type_addrs = type1_addrs if len(type1_addrs) >= 2 else type2_addrs if len(
            type2_addrs) >= 2 else type3_addrs if len(type3_addrs) >= 2 else "None"
        if type_addrs == "None":
            return 0
        for i in type_addrs[::-1]:
            for j in range(i, i - 2000, -addr_len):
                key_bytes = read_key_bytes(pm.process_handle, j, addr_len)
                if key_bytes == "None":
                    continue
                if verify_key(key_bytes, MicroMsg_path):
                    return j - module.lpBaseOfDll
        return 0

    def run(self, logging_path=False, version_list_path=None):
        if not self.get_process_handle()[0]:
            return {}
        mobile_bias = self.search_memory_value(self.mobile, self.module_name)
        name_bias = self.search_memory_value(self.name, self.module_name)
        account_bias = self.search_memory_value(self.account, self.module_name)
        key_bias = 0
        key_bias = self.get_key_bias1()
        key_bias = self.search_key(self.key) if key_bias <= 0 and self.key else key_bias
        key_bias = self.get_key_bias2(self.db_path) if key_bias <= 0 and self.db_path else key_bias

        rdata = {self.version: [name_bias, account_bias, mobile_bias, 0, key_bias]}

        if version_list_path and os.path.exists(version_list_path):
            with open(version_list_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                data.update(rdata)
            with open(version_list_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        if os.path.exists(logging_path) and isinstance(logging_path, str):
            with open(logging_path, "a", encoding="utf-8") as f:
                f.write("{版本号:昵称,账号,手机号,邮箱,KEY}" + "\n")
                f.write(str(rdata) + "\n")
        elif logging_path:
            print("{版本号:昵称,账号,手机号,邮箱,KEY}")
            print(rdata)
        return rdata


def get_info_without_key(h_process, address, n_size=64):
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(h_process, void_p(address), array, n_size, 0) == 0: return "None"
    array = bytes(array).split(b"\x00")[0] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else "None"
