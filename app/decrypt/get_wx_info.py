# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         getwxinfo.py
# Description:
# Author:       xaoyaoo
# Date:         2023/08/21
# -------------------------------------------------------------------------------
import ctypes
import json

import psutil
import pymem
from win32com.client import Dispatch

from app.log import log

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


# 读取内存中的字符串(非key部分)
@log
def get_info_without_key(h_process, address, n_size=64):
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(h_process, void_p(address), array, n_size, 0) == 0: return "None"
    array = bytes(array).split(b"\x00")[0] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else "None"


@log
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


@log
def get_info_wxid(h_process):
    find_num = 100
    addrs = pattern_scan_all(h_process, br'\\FileStorage', return_multiple=True, find_num=find_num)
    wxids = []
    for addr in addrs:
        array = ctypes.create_string_buffer(33)
        if ReadProcessMemory(h_process, void_p(addr - 21), array, 33, 0) == 0: return "None"
        array = bytes(array)  # .decode('utf-8', errors='ignore')
        array = array.split(br'\FileStorage')[0]
        for part in [b'}', b'\x7f', b'\\']:
            if part in array:
                array = array.split(part)[1]
                wxids.append(array.decode('utf-8', errors='ignore'))
                break
    wxid = max(wxids, key=wxids.count) if wxids else "None"
    return wxid


# 读取内存中的key
@log
def get_key(h_process, address, address_len=8):
    array = ctypes.create_string_buffer(address_len)
    if ReadProcessMemory(h_process, void_p(address), array, address_len, 0) == 0: return "None"
    address = int.from_bytes(array, byteorder='little')  # 逆序转换为int地址（key地址）
    key = ctypes.create_string_buffer(32)
    if ReadProcessMemory(h_process, void_p(address), key, 32, 0) == 0: return "None"
    key_string = bytes(key).hex()
    return key_string


# 读取微信信息(account,mobile,name,mail,wxid,key)
@log
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

        bias_list = version_list.get(tmp_rd['version'], None)
        if not isinstance(bias_list, list):
            error = f"[-] WeChat Current Version {tmp_rd['version']} Is Not Supported"
            if is_logging: print(error)
            return -2

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

        name_baseaddr = wechat_base_address + bias_list[0]
        account__baseaddr = wechat_base_address + bias_list[1]
        mobile_baseaddr = wechat_base_address + bias_list[2]
        mail_baseaddr = wechat_base_address + bias_list[3]
        key_baseaddr = wechat_base_address + bias_list[4]

        addrLen = 4 if tmp_rd['version'] in ["3.9.2.23", "3.9.2.26"] else 8

        tmp_rd['account'] = get_info_without_key(Handle, account__baseaddr, 32) if bias_list[1] != 0 else "None"
        tmp_rd['mobile'] = get_info_without_key(Handle, mobile_baseaddr, 64) if bias_list[2] != 0 else "None"
        tmp_rd['name'] = get_info_without_key(Handle, name_baseaddr, 64) if bias_list[0] != 0 else "None"
        tmp_rd['mail'] = get_info_without_key(Handle, mail_baseaddr, 64) if bias_list[3] != 0 else "None"
        tmp_rd['wxid'] = get_info_wxid(Handle)
        tmp_rd['key'] = get_key(Handle, key_baseaddr, addrLen) if bias_list[4] != 0 else "None"
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


@log
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
