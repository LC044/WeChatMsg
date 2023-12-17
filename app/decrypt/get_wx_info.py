# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         getwxinfo.py
# Description:
# Author:       xaoyaoo
# Date:         2023/08/21
# -------------------------------------------------------------------------------
import hmac
import hashlib
import ctypes
import os
import re
import winreg
import pymem
from win32com.client import Dispatch
import psutil
import sys
from typing import List, Union

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


# 获取exe文件的位数
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


# 读取内存中的字符串(非key部分)
def get_info_without_key(h_process, address, n_size=64):
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(h_process, void_p(address), array, n_size, 0) == 0: return "None"
    array = bytes(array).split(b"\x00")[0] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else "None"


def pattern_scan_all(handle, pattern, *, return_multiple=False, find_num=100):
    next_region = 0
    found = []
    user_space_limit = 0x7FFFFFFF0000 if sys.maxsize > 2 ** 32 else 0x7fff0000
    while next_region < user_space_limit:
        try:
            next_region, page_found = pymem.pattern.scan_pattern_page(
                handle,
                next_region,
                pattern,
                return_multiple=return_multiple
            )
        except Exception as e:
            print(e)
            break
        if not return_multiple and page_found:
            return page_found
        if page_found:
            found += page_found
        if len(found) > find_num:
            break
    return found


def get_info_wxid(h_process):
    find_num = 100
    addrs = pattern_scan_all(h_process, br'\\Msg\\FTSContact', return_multiple=True, find_num=find_num)
    wxids = []
    for addr in addrs:
        array = ctypes.create_string_buffer(80)
        if ReadProcessMemory(h_process, void_p(addr - 30), array, 80, 0) == 0: return "None"
        array = bytes(array)  # .split(b"\\")[0]
        array = array.split(b"\\Msg")[0]
        array = array.split(b"\\")[-1]
        wxids.append(array.decode('utf-8', errors='ignore'))
    wxid = max(wxids, key=wxids.count) if wxids else "None"
    return wxid


def get_info_filePath(wxid="all"):
    if not wxid:
        return "None"
    w_dir = "MyDocument:"
    is_w_dir = False

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, "FileSavePath")
        winreg.CloseKey(key)
        w_dir = value
        is_w_dir = True
    except Exception as e:
        w_dir = "MyDocument:"

    if not is_w_dir:
        try:
            user_profile = os.environ.get("USERPROFILE")
            path_3ebffe94 = os.path.join(user_profile, "AppData", "Roaming", "Tencent", "WeChat", "All Users", "config",
                                         "3ebffe94.ini")
            with open(path_3ebffe94, "r", encoding="utf-8") as f:
                w_dir = f.read()
            is_w_dir = True
        except Exception as e:
            w_dir = "MyDocument:"

    if w_dir == "MyDocument:":
        try:
            # 打开注册表路径
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
            documents_path = winreg.QueryValueEx(key, "Personal")[0]  # 读取文档实际目录路径
            winreg.CloseKey(key)  # 关闭注册表
            documents_paths = os.path.split(documents_path)
            if "%" in documents_paths[0]:
                w_dir = os.environ.get(documents_paths[0].replace("%", ""))
                w_dir = os.path.join(w_dir, os.path.join(*documents_paths[1:]))
                # print(1, w_dir)
            else:
                w_dir = documents_path
        except Exception as e:
            profile = os.environ.get("USERPROFILE")
            w_dir = os.path.join(profile, "Documents")

    msg_dir = os.path.join(w_dir, "WeChat Files")

    if wxid == "all" and os.path.exists(msg_dir):
        return msg_dir

    filePath = os.path.join(msg_dir, wxid)
    return filePath if os.path.exists(filePath) else "None"


def get_key(db_path, addr_len):
    def read_key_bytes(h_process, address, address_len=8):
        array = ctypes.create_string_buffer(address_len)
        if ReadProcessMemory(h_process, void_p(address), array, address_len, 0) == 0: return "None"
        address = int.from_bytes(array, byteorder='little')  # 逆序转换为int地址（key地址）
        key = ctypes.create_string_buffer(32)
        if ReadProcessMemory(h_process, void_p(address), key, 32, 0) == 0: return "None"
        key_bytes = bytes(key)
        return key_bytes

    def verify_key(key, wx_db_path):
        if wx_db_path == "None":
            return True
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

    type1_addrs = pm.pattern_scan_module(phone_type1.encode(), module_name, return_multiple=True)
    type2_addrs = pm.pattern_scan_module(phone_type2.encode(), module_name, return_multiple=True)
    type3_addrs = pm.pattern_scan_module(phone_type3.encode(), module_name, return_multiple=True)
    type_addrs = type1_addrs if len(type1_addrs) >= 2 else type2_addrs if len(type2_addrs) >= 2 else type3_addrs if len(
        type3_addrs) >= 2 else "None"
    # print(type_addrs)
    if type_addrs == "None":
        return "None"
    for i in type_addrs[::-1]:
        for j in range(i, i - 2000, -addr_len):
            key_bytes = read_key_bytes(pm.process_handle, j, addr_len)
            if key_bytes == "None":
                continue
            if verify_key(key_bytes, MicroMsg_path):
                return key_bytes.hex()
    return "None"


# 读取微信信息(account,mobile,name,mail,wxid,key)
def read_info(version_list, is_logging=False):
    wechat_process = []
    result = []
    error = ""
    for process in psutil.process_iter(['name', 'exe', 'pid', 'cmdline']):
        if process.name() == 'WeChat.exe':
            wechat_process.append(process)

    if len(wechat_process) == 0:
        error = "[-] WeChat No Run"
        if is_logging: print(error)
        return -1

    for process in wechat_process:
        tmp_rd = {}

        tmp_rd['pid'] = process.pid
        tmp_rd['version'] = Dispatch("Scripting.FileSystemObject").GetFileVersion(process.exe())

        wechat_base_address = 0
        for module in process.memory_maps(grouped=False):
            if module.path and 'WeChatWin.dll' in module.path:
                wechat_base_address = int(module.addr, 16)
                break
        if wechat_base_address == 0:
            error = f"[-] WeChat WeChatWin.dll Not Found"
            if is_logging: print(error)
            return -1

        Handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, process.pid)

        bias_list = version_list.get(tmp_rd['version'], None)
        if not isinstance(bias_list, list) or len(bias_list) <= 4:
            error = f"[-] WeChat Current Version Is Not Supported(maybe not get account,mobile,name,mail)"
            if is_logging: print(error)
            tmp_rd['account'] = "None"
            tmp_rd['mobile'] = "None"
            tmp_rd['name'] = "None"
            tmp_rd['mail'] = "None"
            return -2
        else:
            name_baseaddr = wechat_base_address + bias_list[0]
            account__baseaddr = wechat_base_address + bias_list[1]
            mobile_baseaddr = wechat_base_address + bias_list[2]
            mail_baseaddr = wechat_base_address + bias_list[3]
            # key_baseaddr = wechat_base_address + bias_list[4]

            tmp_rd['account'] = get_info_without_key(Handle, account__baseaddr, 32) if bias_list[1] != 0 else "None"
            tmp_rd['mobile'] = get_info_without_key(Handle, mobile_baseaddr, 64) if bias_list[2] != 0 else "None"
            tmp_rd['name'] = get_info_without_key(Handle, name_baseaddr, 64) if bias_list[0] != 0 else "None"
            tmp_rd['mail'] = get_info_without_key(Handle, mail_baseaddr, 64) if bias_list[3] != 0 else "None"

        addrLen = get_exe_bit(process.exe()) // 8

        tmp_rd['wxid'] = get_info_wxid(Handle)
        tmp_rd['filePath'] = get_info_filePath(tmp_rd['wxid']) if tmp_rd['wxid'] != "None" else "None"
        tmp_rd['key'] = get_key(tmp_rd['filePath'], addrLen)
        result.append(tmp_rd)

    if is_logging:
        print("=" * 32)
        if isinstance(result, str):  # 输出报错
            print(result)
        else:  # 输出结果
            for i, rlt in enumerate(result):
                for k, v in rlt.items():
                    print(f"[+] {k:>8}: {v}")
                print(end="-" * 32 + "\n" if i != len(result) - 1 else "")
        print("=" * 32)

    return result


import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def get_info(VERSION_LIST):
    result = read_info(VERSION_LIST, True)  # 读取微信信息
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--vlfile", type=str, help="手机号", required=False)
    parser.add_argument("--vldict", type=str, help="微信昵称", required=False)

    args = parser.parse_args()

    # 读取微信各版本偏移
    if args.vlfile:
        VERSION_LIST_PATH = args.vlfile
        with open(VERSION_LIST_PATH, "r", encoding="utf-8") as f:
            VERSION_LIST = json.load(f)
    if args.vldict:
        VERSION_LIST = json.loads(args.vldict)

    if not args.vlfile and not args.vldict:
        VERSION_LIST_PATH = "../version_list.json"

        with open(VERSION_LIST_PATH, "r", encoding="utf-8") as f:
            VERSION_LIST = json.load(f)

    result = read_info(VERSION_LIST, True)  # 读取微信信息
