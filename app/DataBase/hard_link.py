import binascii
import os.path
import sqlite3
import threading
import traceback
import xml.etree.ElementTree as ET

from app.log import log, logger
from app.util.protocbuf.msg_pb2 import MessageBytesExtra

image_db_lock = threading.Lock()
video_db_lock = threading.Lock()
image_db_path = "./app/Database/Msg/HardLinkImage.db"
video_db_path = "./app/Database/Msg/HardLinkVideo.db"
root_path = "FileStorage/MsgAttach/"
video_root_path = "FileStorage/Video/"


@log
def get_md5_from_xml(content, type_="img"):
    try:
        # 解析XML
        root = ET.fromstring(content)
        if type_ == "img":
            # 提取md5的值
            md5_value = root.find(".//img").get("md5")
        elif type_ == "video":
            md5_value = root.find(".//videomsg").get("md5")
        # print(md5_value)
        return md5_value
    except ET.ParseError:
        return None


def decodeExtraBuf(extra_buf_content: bytes):
    if not extra_buf_content:
        return {
            "region": ('', '', ''),
            "signature": '',
            "telephone": '',
            "gender": 0,
        }
    trunkName = {
        b"\x46\xCF\x10\xC4": "个性签名",
        b"\xA4\xD9\x02\x4A": "国家",
        b"\xE2\xEA\xA8\xD1": "省份",
        b"\x1D\x02\x5B\xBF": "市",
        # b"\x81\xAE\x19\xB4": "朋友圈背景url",
        # b"\xF9\x17\xBC\xC0": "公司名称",
        # b"\x4E\xB9\x6D\x85": "企业微信属性",
        # b"\x0E\x71\x9F\x13": "备注图片",
        b"\x75\x93\x78\xAD": "手机号",
        b"\x74\x75\x2C\x06": "性别",
    }
    res = {"手机号": ""}
    off = 0
    try:
        for key in trunkName:
            trunk_head = trunkName[key]
            try:
                off = extra_buf_content.index(key) + 4
            except:
                pass
            char = extra_buf_content[off: off + 1]
            off += 1
            if char == b"\x04":  # 四个字节的int，小端序
                intContent = extra_buf_content[off: off + 4]
                off += 4
                intContent = int.from_bytes(intContent, "little")
                res[trunk_head] = intContent
            elif char == b"\x18":  # utf-16字符串
                lengthContent = extra_buf_content[off: off + 4]
                off += 4
                lengthContent = int.from_bytes(lengthContent, "little")
                strContent = extra_buf_content[off: off + lengthContent]
                off += lengthContent
                res[trunk_head] = strContent.decode("utf-16").rstrip("\x00")
        return {
            "region": (res["国家"], res["省份"], res["市"]),
            "signature": res["个性签名"],
            "telephone": res["手机号"],
            "gender": res["性别"],
        }
    except:
        logger.error(f'联系人解析错误:\n{traceback.format_exc()}')
        return {
            "region": ('', '', ''),
            "signature": '',
            "telephone": '',
            "gender": 0,
        }


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


@singleton
class HardLink:
    def __init__(self):
        self.imageDB = None
        self.videoDB = None
        self.image_cursor = None
        self.video_cursor = None
        self.open_flag = False
        self.init_database()

    def init_database(self):
        if not self.open_flag:
            if os.path.exists(image_db_path):
                self.imageDB = sqlite3.connect(image_db_path, check_same_thread=False)
                # '''创建游标'''
                self.image_cursor = self.imageDB.cursor()
                self.open_flag = True
                if image_db_lock.locked():
                    image_db_lock.release()
            if os.path.exists(video_db_path):
                self.videoDB = sqlite3.connect(video_db_path, check_same_thread=False)
                # '''创建游标'''
                self.video_cursor = self.videoDB.cursor()
                self.open_flag = True
                if video_db_lock.locked():
                    video_db_lock.release()

    def get_image_by_md5(self, md5: bytes):
        if not md5:
            return None
        if not self.open_flag:
            return None
        sql = """
            select Md5Hash,MD5,FileName,HardLinkImageID.Dir as DirName1,HardLinkImageID2.Dir as DirName2
            from HardLinkImageAttribute
            join HardLinkImageID on HardLinkImageAttribute.DirID1 = HardLinkImageID.DirID
            join HardLinkImageID as HardLinkImageID2 on HardLinkImageAttribute.DirID2 = HardLinkImageID2.DirID
            where MD5 = ?;
            """
        try:
            image_db_lock.acquire(True)
            try:
                self.image_cursor.execute(sql, [md5])
            except AttributeError:
                self.init_database()
                self.image_cursor.execute(sql, [md5])
            result = self.image_cursor.fetchone()
            return result
        finally:
            image_db_lock.release()

    def get_video_by_md5(self, md5: bytes):
        if not md5:
            return None
        if not self.open_flag:
            return None
        sql = """
            select Md5Hash,MD5,FileName,HardLinkVideoID2.Dir as DirName2
            from HardLinkVideoAttribute
            join HardLinkVideoID as HardLinkVideoID2 on HardLinkVideoAttribute.DirID2 = HardLinkVideoID2.DirID
            where MD5 = ?;
            """
        try:
            video_db_lock.acquire(True)
            try:
                self.video_cursor.execute(sql, [md5])
            except sqlite3.OperationalError:
                return None
            except AttributeError:
                self.init_database()
                self.video_cursor.execute(sql, [md5])
            result = self.video_cursor.fetchone()
            return result
        finally:
            video_db_lock.release()

    def get_image_original(self, content, bytesExtra) -> str:
        msg_bytes = MessageBytesExtra()
        msg_bytes.ParseFromString(bytesExtra)
        result = ''
        for tmp in msg_bytes.message2:
            if tmp.field1 != 4:
                continue
            pathh = tmp.field2  # wxid\FileStorage\...
            pathh = "\\".join(pathh.split("\\")[1:])
            return pathh
        md5 = get_md5_from_xml(content)
        if not md5:
            pass
        else:
            result = self.get_image_by_md5(binascii.unhexlify(md5))
            if result:
                dir1 = result[3]
                dir2 = result[4]
                data_image = result[2]
                dir0 = "Image"
                dat_image = os.path.join(root_path, dir1, dir0, dir2, data_image)
                result = dat_image
        return result

    def get_image_thumb(self, content, bytesExtra) -> str:
        msg_bytes = MessageBytesExtra()
        msg_bytes.ParseFromString(bytesExtra)
        result = ''
        for tmp in msg_bytes.message2:
            if tmp.field1 != 3:
                continue
            pathh = tmp.field2  # wxid\FileStorage\...
            pathh = "\\".join(pathh.split("\\")[1:])
            return pathh
        md5 = get_md5_from_xml(content)
        if not md5:
            pass
        else:
            result = self.get_image_by_md5(binascii.unhexlify(md5))
            if result:
                dir1 = result[3]
                dir2 = result[4]
                data_image = result[2]
                dir0 = "Thumb"
                dat_image = os.path.join(root_path, dir1, dir0, dir2, data_image)
                result = dat_image
        return result

    def get_image(self, content, bytesExtra, up_dir="", thumb=False) -> str:
        msg_bytes = MessageBytesExtra()
        msg_bytes.ParseFromString(bytesExtra)
        if thumb:
            result = self.get_image_thumb(content, bytesExtra)
        else:
            result = self.get_image_original(content, bytesExtra)
            if not (result and os.path.exists(os.path.join(up_dir, result))):
                result = self.get_image_thumb(content, bytesExtra)
        return result

    def get_video(self, content, bytesExtra, thumb=False):
        msg_bytes = MessageBytesExtra()
        msg_bytes.ParseFromString(bytesExtra)
        for tmp in msg_bytes.message2:
            if tmp.field1 != (3 if thumb else 4):
                continue
            pathh = tmp.field2  # wxid\FileStorage\...
            pathh = "\\".join(pathh.split("\\")[1:])
            return pathh
        md5 = get_md5_from_xml(content, type_="video")
        if not md5:
            return ''
        result = self.get_video_by_md5(binascii.unhexlify(md5))
        if result:
            dir2 = result[3]
            data_image = result[2].split(".")[0] + ".jpg" if thumb else result[2]
            # dir0 = 'Thumb' if thumb else 'Image'
            dat_image = os.path.join(video_root_path, dir2, data_image)
            return dat_image
        else:
            return ''

    def close(self):
        if self.open_flag:
            try:
                image_db_lock.acquire(True)
                video_db_lock.acquire(True)
                self.open_flag = False
                self.imageDB.close()
                self.videoDB.close()
            finally:
                image_db_lock.release()
                video_db_lock.release()

    def __del__(self):
        self.close()


# 6b02292eecea118f06be3a5b20075afc_t

if __name__ == "__main__":
    msg_root_path = "./Msg/"
    image_db_path = "./Msg/HardLinkImage.db"
    video_db_path = "./Msg/HardLinkVideo.db"
    hard_link_db = HardLink()
    hard_link_db.init_database()
    # content = '''<?xml version="1.0"?><msg>\n\t<img aeskey="bc37a58c32cb203ee9ac587b068e5853" encryver="1" cdnthumbaeskey="bc37a58c32cb203ee9ac587b068e5853" cdnthumburl="3057020100044b30490201000204d181705002032f5405020428a7b4de02046537869d042462313532363539632d663930622d343463302d616636662d333837646434633061626534020401150a020201000405004c4c6d00" cdnthumblength="3097" cdnthumbheight="120" cdnthumbwidth="68" cdnmidheight="0" cdnmidwidth="0" cdnhdheight="0" cdnhdwidth="0" cdnmidimgurl="3057020100044b30490201000204d181705002032f5405020428a7b4de02046537869d042462313532363539632d663930622d343463302d616636662d333837646434633061626534020401150a020201000405004c4c6d00" length="57667" md5="6844b812d5d514eb6878657e0bf4cdbb" originsourcemd5="1dfdfa24922270ea1cb5daba103f45ca" />\n\t<platform_signature></platform_signature>\n\t<imgdatahash></imgdatahash>\n</msg>\n'''
    # print(hard_link_db.get_image(content))
    # print(hard_link_db.get_image(content, thumb=False))
    # result = get_md5_from_xml(content)
    # print(result)
    content = """<?xml version="1.0"?>
<msg>
	<videomsg aeskey="d635d2013d221dbd05a4eab3a8185f5a" cdnvideourl="3057020100044b304902010002040297cead02032f540502042ba7b4de020465673b74042438316562356530652d653764352d343263632d613531642d6464383661313330623965330204052400040201000405004c537500" cdnthumbaeskey="d635d2013d221dbd05a4eab3a8185f5a" cdnthumburl="3057020100044b304902010002040297cead02032f540502042ba7b4de020465673b74042438316562356530652d653764352d343263632d613531642d6464383661313330623965330204052400040201000405004c537500" length="25164270" playlength="60" cdnthumblength="7419" cdnthumbwidth="1920" cdnthumbheight="1080" fromusername="wxid_yt67eeoo4blm22" md5="95558f0e503651375b475636519d2285" newmd5="4ece19bcd92dc5b93b83f397461a1310" isplaceholder="0" rawmd5="d660ba186bb31126d94fa568144face8" rawlength="143850007" cdnrawvideourl="3052020100044b30490201000204d8cd585302032f540502040f6a42b7020465673b85042464666462306634342d653339342d343232302d613534392d3930633030646236306266610204059400040201000400" cdnrawvideoaeskey="5915b14ac8d121e0944d9e444aebb7ed" overwritenewmsgid="0" originsourcemd5="a1a567d8c170bca33d075b787a60dd3f" isad="0" />
</msg>
"""
    print(hard_link_db.get_video(content))
    print(hard_link_db.get_video(content, thumb=True))
