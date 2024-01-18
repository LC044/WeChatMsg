import html
import xml.etree.ElementTree as ET

import lz4.block

import requests
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from app.util.protocbuf.msg_pb2 import MessageBytesExtra
from ..util.file import get_file


def decompress_CompressContent(data):
    """
    解压缩Msg：CompressContent内容
    :param data:
    :return:
    """
    if data is None or not isinstance(data, bytes):
        return ""
    try:
        dst = lz4.block.decompress(data, uncompressed_size=len(data) << 10)
        decoded_string = dst.decode().replace("\x00", "")  # Remove any null characters
    except:
        print(
            "Decompression failed: potentially corrupt input or insufficient buffer size."
        )
        return ""
    return decoded_string


def escape_js_and_html(input_str):
    if not input_str:
        return ""
    # 转义HTML特殊字符
    html_escaped = html.escape(input_str, quote=False)

    # 手动处理JavaScript转义字符
    js_escaped = (
        html_escaped.replace("\\", "\\\\")
        .replace("'", r"\'")
        .replace('"', r"\"")
        .replace("\n", r"\n")
        .replace("\r", r"\r")
        .replace("\t", r"\t")
    )

    return js_escaped


def parser_reply(data: bytes):
    xml_content = decompress_CompressContent(data)
    if not xml_content:
        return {
            "type": 57,
            "title": "发生错误",
            "refer": {
                "type": "1",
                "content": "引用错误",
                "displayname": "用户名",
            },
            "is_error": True,
        }
    try:
        root = ET.XML(xml_content)
        appmsg = root.find("appmsg")
        msg_type = int(appmsg.find("type").text)
        title = appmsg.find("title").text
        refermsg_content = appmsg.find("refermsg").find("content").text
        refermsg_type = int(appmsg.find("refermsg").find("type").text)
        refermsg_displayname = appmsg.find("refermsg").find("displayname").text
        return {
            "type": msg_type,
            "title": title,
            "refer": None
            if refermsg_type != 1
            else {
                "type": refermsg_type,
                "content": refermsg_content.lstrip("\n"),
                "displayname": refermsg_displayname,
            },
            "is_error": False,
        }
    except:
        return {
            "type": 57,
            "title": "发生错误",
            "refer": {
                "type": "1",
                "content": "引用错误",
                "displayname": "用户名",
            },
            "is_error": True,
        }


def music_share(data: bytes):
    xml_content = decompress_CompressContent(data)
    if not xml_content:
        return {"type": 3, "title": "发生错误", "is_error": True}
    try:
        root = ET.XML(xml_content)
        appmsg = root.find("appmsg")
        msg_type = int(appmsg.find("type").text)
        title = appmsg.find("title").text
        if len(title) >= 39:
            title = title[:38] + "..."
        artist = appmsg.find("des").text
        link_url = appmsg.find("url").text  # 链接地址
        audio_url = get_audio_url(appmsg.find("dataurl").text)  # 播放地址
        website_name = get_website_name(link_url)
        return {
            "type": msg_type,
            "title": escape_js_and_html(title),
            "artist": escape_js_and_html(artist),
            "link_url": link_url,
            "audio_url": audio_url,
            "website_name": escape_js_and_html(website_name),
            "is_error": False,
        }
    except Exception as e:
        print(f"Music Share Error: {e}")
        return {"type": 3, "title": "发生错误", "is_error": True}


def share_card(bytesExtra, compress_content_):
    title, des, url, show_display_name, thumbnail, app_logo = "", "", "", "", "", ""
    try:
        xml = decompress_CompressContent(compress_content_)
        root = ET.XML(xml)
        appmsg = root.find("appmsg")
        title = appmsg.find("title").text
        try:
            des = appmsg.find("des").text
        except:
            des = ""
        url = appmsg.find("url").text
        appinfo = root.find("appinfo")
        show_display_name = appmsg.find("sourcedisplayname")
        sourceusername = appmsg.find("sourceusername")
        if show_display_name is not None:
            show_display_name = show_display_name.text
        else:
            if appinfo is not None:
                show_display_name = appinfo.find("appname").text
        msg_bytes = MessageBytesExtra()
        msg_bytes.ParseFromString(bytesExtra)
        app_logo = ""
        thumbnail = ""
        for tmp in msg_bytes.message2:
            if tmp.field1 == 3:
                thumbnail = tmp.field2
                thumbnail = "\\".join(thumbnail.split("\\")[1:])
            if tmp.field2 == 4:
                app_logo = tmp.field2
                app_logo = "\\".join(app_logo.split("\\")[1:])
        if sourceusername is not None:
            from app.DataBase import micro_msg_db  # 放上面会导致循环依赖

            contact = micro_msg_db.get_contact_by_username(sourceusername.text)
            if contact:
                app_logo = contact[7]
    finally:
        return {
            "title": escape_js_and_html(title),
            "description": escape_js_and_html(des),
            "url": escape_js_and_html(url),
            "app_name": escape_js_and_html(show_display_name),
            "thumbnail": thumbnail,
            "app_logo": app_logo,
        }


def transfer_decompress(compress_content_):
    """
    return dict
        feedesc: 钱数，str类型，包含一个前缀币种符号（除人民币￥之外未测试）;
        pay_memo: 转账备注;
        receiver_username: 接受转账人的 wxid; （因为电脑上只有私聊页面会显示收款所以这个字段没有也罢，不要轻易使用，因为可能为空）
        paysubtype: int 类型，1 为发出转账，3 为接受转账，4 为退还转账;
    """
    feedesc, pay_memo, receiver_username, paysubtype = "", "", "", ""
    try:
        xml = decompress_CompressContent(compress_content_)
        root = ET.XML(xml)
        appmsg = root.find("appmsg")
        wcpayinfo = appmsg.find("wcpayinfo")
        paysubtype = int(wcpayinfo.find("paysubtype").text)
        feedesc = wcpayinfo.find("feedesc").text
        pay_memo = wcpayinfo.find("pay_memo").text
        receiver_username = wcpayinfo.find("receiver_username").text
    finally:
        return {
            "feedesc": feedesc,
            "pay_memo": escape_js_and_html(pay_memo),
            "receiver_username": receiver_username,
            "paysubtype": paysubtype,
        }


def call_decompress(is_send, bytes_extra, display_content, str_content):  # 音视频通话
    """
    return dict
        call_type: int 类型，0 为视频，1为语音; （返回为 2 是未知错误）
        display_content: str 类型，页面显示的话;
    """
    call_type = 2
    call_length = 0
    msg_bytes = MessageBytesExtra()
    msg_bytes.ParseFromString(bytes_extra)
    # message2 字段 1: 发送人wxid; 字段 3: "1"是语音，"0"是视频; 字段 4: 通话时长
    for i in msg_bytes.message2:
        if i.field1 == 3:
            call_type = int(i.field2)
        elif i.field1 == 4:
            call_length = int(i.field2)

    try:
        if display_content == "":
            if str_content == "11":
                h, m, s = (
                    call_length // 3600,
                    (call_length % 3600) // 60,
                    call_length % 60,
                )
                display_content = f"通话时长 {f'{h:02d}:' if h else ''}{m:02d}:{s:02d}"
            else:
                display_content = {
                    "5": ("" if is_send else "对方") + "已取消",
                    "8": ("对方" if is_send else "") + "已拒绝",
                    "7": "已在其他设备接听",
                    "12": "已在其他设备拒绝",
                }[str_content]
    except KeyError:
        display_content = "未知类型，您可以把这条消息对应的微信界面消息反馈给我们"

    return {
        "call_type": call_type,
        "display_content": display_content,
    }


def get_website_name(url):
    parsed_url = urlparse(url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    website_name = ""
    try:
        response = requests.get(domain, allow_redirects=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            website_name = soup.title.string.strip()
        elif response.status_code == 302:
            domain = response.headers["Location"]
            response = requests.get(domain, allow_redirects=False)
            soup = BeautifulSoup(response.content, "html.parser")
            website_name = soup.title.string.strip()
        else:
            response = requests.get(url, allow_redirects=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                website_name = soup.title.string.strip()
                index = website_name.find("-")
                if index != -1:  # 如果找到了 "-"
                    website_name = website_name[index + 1 :].strip()
    except Exception as e:
        print(f"Get Website Info Error: {e}")
    return website_name


def get_audio_url(url):
    path = ""
    try:
        response = requests.get(url, allow_redirects=False)
        # 检查响应状态码
        if response.status_code == 302:
            path = response.headers["Location"]
        elif response.status_code == 200:
            print("音乐文件已失效,url:" + url)
        else:
            print("音乐文件地址获取失败,url:" + url + ",状态码" + str(response.status_code))
    except Exception as e:
        print(f"Get Audio Url Error: {e}")
    return path


def file(bytes_extra, compress_content, output_path):
    xml_content = decompress_CompressContent(compress_content)
    if not xml_content:
        return {"type": 6, "title": "发生错误", "is_error": True}
    try:
        root = ET.XML(xml_content)
        appmsg = root.find("appmsg")
        msg_type = int(appmsg.find("type").text)
        file_name = appmsg.find("title").text
        pattern = r'[\\/:*?"<>|\r\n]+'
        file_name = re.sub(pattern, "_", file_name)
        appattach = appmsg.find("appattach")
        file_len = int(appattach.find("totallen").text)
        app_name = ""
        file_len = format_bytes(file_len)
        file_ext = appattach.find("fileext").text
        if root.find("appinfo") is not None:
            app_info = root.find("appinfo")
            app_name = app_info.find("appname").text
            if app_name is None:
                app_name = ""
        file_path = get_file(bytes_extra, file_name, output_path)
        return {
            "type": msg_type,
            "file_name": escape_js_and_html(file_name),
            "file_len": file_len,
            "file_ext": file_ext,
            "file_path": file_path,
            "app_name": escape_js_and_html(app_name),
            "is_error": False,
        }
    except Exception as e:
        print(f"File Get Info Error: {e}")
        return {"type": 6, "title": "发生错误", "is_error": True}


def format_bytes(size):
    units = ["B", "KB", "MB", "GB"]

    def convert_bytes(size, unit_index):
        if size < 1024 or unit_index >= len(units) - 1:
            return size, unit_index
        return convert_bytes(size / 1024, unit_index + 1)

    final_size, final_unit_index = convert_bytes(size, 0)
    return f"{final_size:.2f} {units[final_unit_index]}"
