# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         getwxinfo.py
# Description:
# Author:       xaoyaoo
# Date:         2023/08/21
# -------------------------------------------------------------------------------
import argparse
import ctypes
import json

import psutil
from win32com.client import Dispatch

from app.log import log

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


# 读取内存中的字符串(非key部分)
def get_info_without_key(h_process, address, n_size=64):
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(h_process, void_p(address), array, n_size, 0) == 0: return "None"
    array = bytes(array).split(b"\x00")[0] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else "None"


def get_info_wxid(h_process, address, n_size=32, address_len=8):
    array = ctypes.create_string_buffer(address_len)
    if ReadProcessMemory(h_process, void_p(address), array, address_len, 0) == 0: return "None"
    address = int.from_bytes(array, byteorder='little')  # 逆序转换为int地址（key地址）
    wxid = get_info_without_key(h_process, address, n_size)
    # if not wxid.startswith("wxid_"): wxid = "None"
    return wxid


# 读取内存中的key
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
def read_info(version_list):
    wechat_process = []
    result = []

    for process in psutil.process_iter(['name', 'exe', 'pid', 'cmdline']):
        if process.name() == 'WeChat.exe':
            wechat_process.append(process)

    if len(wechat_process) == 0:
        return -1

    for process in wechat_process:
        tmp_rd = {}

        tmp_rd['pid'] = process.pid
        tmp_rd['version'] = Dispatch("Scripting.FileSystemObject").GetFileVersion(process.exe())

        bias_list = version_list.get(tmp_rd['version'], None)
        if not isinstance(bias_list, list):
            return -2

        wechat_base_address = 0
        for module in process.memory_maps(grouped=False):
            if module.path and 'WeChatWin.dll' in module.path:
                wechat_base_address = int(module.addr, 16)
                break
        if wechat_base_address == 0:
            return f"[-] WeChat WeChatWin.dll Not Found"

        Handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, process.pid)

        name_baseaddr = wechat_base_address + bias_list[0]
        account__baseaddr = wechat_base_address + bias_list[1]
        mobile_baseaddr = wechat_base_address + bias_list[2]
        mail_baseaddr = wechat_base_address + bias_list[3]
        key_baseaddr = wechat_base_address + bias_list[4]
        wxid_baseaddr = wechat_base_address + bias_list[5]

        addrLen = 4 if tmp_rd['version'] in ["3.9.2.23", "3.9.2.26"] else 8

        tmp_rd['account'] = get_info_without_key(Handle, account__baseaddr, 32) if bias_list[1] != 0 else "None"
        tmp_rd['mobile'] = get_info_without_key(Handle, mobile_baseaddr, 64) if bias_list[2] != 0 else "None"
        tmp_rd['name'] = get_info_without_key(Handle, name_baseaddr, 64) if bias_list[0] != 0 else "None"
        tmp_rd['mail'] = get_info_without_key(Handle, mail_baseaddr, 64) if bias_list[3] != 0 else "None"
        tmp_rd['wxid'] = get_info_wxid(Handle, wxid_baseaddr, 24, addrLen) if bias_list[5] != 0 else "None"
        tmp_rd['key'] = get_key(Handle, key_baseaddr, addrLen) if bias_list[4] != 0 else "None"
        result.append(tmp_rd)

    return result


@log
def get_info():
    VERSION_LIST_PATH = "app/decrypt/version_list.json"

    with open(VERSION_LIST_PATH, "r", encoding="utf-8") as f:
        VERSION_LIST = json.load(f)

    result = read_info(VERSION_LIST)  # 读取微信信息
    return result


if __name__ == "__main__":
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
        VERSION_LIST_PATH = "./version_list.json"

        with open(VERSION_LIST_PATH, "r", encoding="utf-8") as f:
            VERSION_LIST = json.load(f)

    result = read_info(VERSION_LIST)  # 读取微信信息

    print("=" * 32)
    if isinstance(result, str):  # 输出报错
        print(result)
    else:  # 输出结果
        for i, rlt in enumerate(result):
            for k, v in rlt.items():
                print(f"[+] {k:>7}: {v}")
            print(end="-" * 32 + "\n" if i != len(result) - 1 else "")
    print("=" * 32)
