import html
import xml.etree.ElementTree as ET

import lz4


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
    except lz4.block.LZ4BlockError:
        print("Decompression failed: potentially corrupt input or insufficient buffer size.")
        return ''
    return decoded_string
def escape_js_and_html(input_str):
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
            }
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
            'title': escape_js_and_html(title),
            'refer': None if refermsg_type != 1 else {
                'type': refermsg_type,
                'content': escape_js_and_html(refermsg_content.lstrip("\n")),
                'displayname': escape_js_and_html(refermsg_displayname),
            }
        }
    except:
        return {
            'type': 57,
            'title': "发生错误",
            'refer': {
                'type': '1',
                'content': '引用错误',
                'displayname': '用户名',
            }
        }
