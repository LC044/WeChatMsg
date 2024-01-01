import html
import xml.etree.ElementTree as ET

import lz4.block

import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from app.DataBase.hard_link import parseBytes


def decompress_CompressContent(data):
    """
    解压缩Msg：CompressContent内容
    :param data:
    :return:
    """
    if data is None or not isinstance(data, bytes):
        return ''
    try:
        dst = lz4.block.decompress(data, uncompressed_size=len(data) << 10)
        decoded_string = dst.decode().replace('\x00', '')  # Remove any null characters
    except:
        print("Decompression failed: potentially corrupt input or insufficient buffer size.")
        return ''
    return decoded_string


def escape_js_and_html(input_str):
    if not input_str:
        return ''
    # 转义HTML特殊字符
    html_escaped = html.escape(input_str, quote=False)

    # 手动处理JavaScript转义字符
    js_escaped = (
        html_escaped
        .replace("\\", "\\\\")
        .replace("'", r"\'")
        .replace('"', r'\"')
        .replace("\n", r'\n')
        .replace("\r", r'\r')
        .replace("\t", r'\t')
    )

    return js_escaped


def parser_reply(data: bytes):
    xml_content = decompress_CompressContent(data)
    if not xml_content:
        return {
            'type': 57,
            'title': "发生错误",
            'refer': {
                'type': '1',
                'content': '引用错误',
                'displayname': '用户名',
            },
            "is_error": True
        }
    try:
        root = ET.XML(xml_content)
        appmsg = root.find('appmsg')
        msg_type = int(appmsg.find('type').text)
        title = appmsg.find('title').text
        refermsg_content = appmsg.find('refermsg').find('content').text
        refermsg_type = int(appmsg.find('refermsg').find('type').text)
        refermsg_displayname = appmsg.find('refermsg').find('displayname').text
        return {
            'type': msg_type,
            'title': title,
            'refer': None if refermsg_type != 1 else {
                'type': refermsg_type,
                'content': refermsg_content.lstrip("\n"),
                'displayname': refermsg_displayname,
            },
            "is_error": False
        }
    except:
        return {
            'type': 57,
            'title': "发生错误",
            'refer': {
                'type': '1',
                'content': '引用错误',
                'displayname': '用户名',
            },
            "is_error": True
        }


def music_share(data: bytes):
    xml_content = decompress_CompressContent(data)
    if not xml_content:
        return {
            'type': 3,
            'title': "发生错误",
            "is_error": True
        }
    try:
        root = ET.XML(xml_content)
        appmsg = root.find('appmsg')
        msg_type = int(appmsg.find('type').text)
        title = appmsg.find('title').text
        if len(title) >= 39:
            title = title[:38] + '...'
        artist = appmsg.find('des').text
        link_url = appmsg.find('url').text  # 链接地址
        audio_url = get_audio_url(appmsg.find('dataurl').text)  # 播放地址
        website_name = get_website_name(link_url)
        return {
            'type': msg_type,
            'title': title,
            'artist': artist,
            'link_url': link_url,
            'audio_url': audio_url,
            'website_name': website_name,
            "is_error": False
        }
    except Exception as e:
        print(f"Music Share Error: {e}")
        return {
            'type': 3,
            'title': "发生错误",
            "is_error": True
        }


def share_card(bytesExtra, compress_content_):
    xml = decompress_CompressContent(compress_content_)
    root = ET.XML(xml)
    appmsg = root.find('appmsg')
    title = appmsg.find('title').text
    des = appmsg.find('des').text
    url = appmsg.find('url').text
    appinfo = root.find('appinfo')
    show_display_name = appmsg.find('sourcedisplayname')
    if show_display_name is not None:
        show_display_name = show_display_name.text
    else:
        if appinfo is not None:
            show_display_name = appinfo.find('appname').text
    bytesDict = parseBytes(bytesExtra)
    app_logo = ''
    thumbnail = ''
    for msginfo in bytesDict[3]:
        if msginfo[1][1][1] == 3:
            thumbnail = msginfo[1][2][1]
            thumbnail = "\\".join(thumbnail.split('\\')[1:])
        if msginfo[1][1][1] == 4:
            app_logo = msginfo[1][2][1]
            app_logo = "\\".join(app_logo.split('\\')[1:])
    return {
        'title': escape_js_and_html(title),
        'description': escape_js_and_html(des),
        'url': url,
        'app_name': escape_js_and_html(show_display_name),
        'thumbnail': thumbnail,
        'app_logo': app_logo
    }


def get_website_name(url):
    parsed_url = urlparse(url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    website_name = ''
    try:
        response = requests.get(domain, allow_redirects=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            website_name = soup.title.string.strip()
        elif response.status_code == 302:
            domain = response.headers['Location']
            response = requests.get(domain, allow_redirects=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            website_name = soup.title.string.strip()
        else:
            response = requests.get(url, allow_redirects=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                website_name = soup.title.string.strip()
                index = website_name.find("-")
                if index != -1:  # 如果找到了 "-"
                    website_name = website_name[index + 1:].strip()
    except Exception as e:
        print(f"Get Website Info Error: {e}")
    return website_name


def get_audio_url(url):
    path = ''
    try:
        response = requests.get(url, allow_redirects=False)
        # 检查响应状态码
        if response.status_code == 302:
            path = response.headers['Location']
        elif response.status_code == 200:
            print('音乐文件已失效,url:' + url)
        else:
            print('音乐文件地址获取失败,url:' + url + ',状态码' + str(response.status_code))
    except Exception as e:
        print(f"Get Audio Url Error: {e}")
    return path
