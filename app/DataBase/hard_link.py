import binascii
import os.path
import sqlite3
import threading
import xml.etree.ElementTree as ET

from app.log import log

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


class tencent_struct:
    def __setVals__(self, data, off):
        if data:
            self.__data = data
        if self.__data:
            self.__size = len(self.__data)
        self.__off = off

    def __readString(self):
        try:
            length = self.__readUleb()
            res = self.__data[self.__off: self.__off + length]
            self.__add(length)
        except:
            raise
        return res.decode("utf-8")

    def __readUleb(self):
        try:
            i = self.__data[self.__off]
            self.__add()
            if i & 0x80:
                j = self.__data[self.__off]
                i = i & 0x7F
                i = i | (j << 7)
                self.__add()
                if i & 0x4000:
                    j = self.__data[self.__off]
                    i = i & 0x3FFF
                    i = i | (j << 14)
                    self.__add()
                    if i & 0x200000:
                        j = self.__data[self.__off]
                        i = i & 0x1FFFFF
                        i = i | (j << 21)
                        self.__add()
                        if i & 0x10000000:
                            j = self.__data[self.__off]
                            i = i & 0xFFFFFFF
                            i = i | (j << 28)
                            self.__add()
            return i
        except:
            raise

    def __readData(self):
        try:
            length = self.__readUleb()
            data = self.__data[self.__off: self.__off + length]
            self.__add(length)
            return data
        except:
            raise

    def __init__(self, data=None, off=0):
        self.__data = data
        self.__off = off
        if self.__data:
            self.__size = len(self.__data)
        else:
            self.__size = 0

    def __add(self, value=1):
        self.__off += value
        if self.__off > self.__size:
            raise "偏移量超出size"

    def readStruct(self, struct_type):
        current_dict = None
        if isinstance(struct_type, str):
            current_dict = getattr(self, struct_type)
        else:
            current_dict = struct_type
        res = {}
        try:
            while self.__off < self.__size:
                key = self.__readUleb()
                key = key >> 3
                if key == 0:
                    break
                op = None
                fieldName = ""
                if key in current_dict:
                    op = current_dict[key][1]
                    fieldName = current_dict[key][0]
                else:
                    break
                if isinstance(op, dict):
                    if not key in res:
                        res[key] = []
                    current_struct = self.__readData()
                    recursion = tencent_struct(current_struct)
                    res[key].append((fieldName, recursion.readStruct(op)))
                elif op != "":
                    res[key] = (fieldName, self.__contenttype__[op](self))
                else:
                    break
        except:
            raise
        return res

    __struct1__ = {1: ("", "I"), 2: ("", "I")}

    __msgInfo__ = {1: ("", "I"), 2: ("msg_info", "s")}

    __bytesExtra__ = {
        1: ("", __struct1__),
        3: ("msg_info_struct", __msgInfo__),
    }

    __struct2__ = {1: ("", "s"), 2: ("", "s")}

    __extraBuf__ = {
        1: ("", __struct2__),
    }

    def get_bytesExta_Content(self, data=None, off=0):
        self.__setVals__(data, off)
        try:
            return self.readStruct("__bytesExtra__")
        except:
            raise

    def get_extraBuf_Content(self, data=None, off=0):
        self.__setVals__(data, off)
        try:
            return self.readStruct("__extraBuf__")
        except:
            raise

    __contenttype__ = {
        "s": __readString,
        "I": __readUleb,
        "P": __readData,
    }


def parseBytes(content: bytes):
    try:
        bytesExtra = tencent_struct().get_bytesExta_Content(content)
        return bytesExtra
    except:
        pass


def parseExtraBuf(content: bytes):
    try:
        extraBuf = tencent_struct().get_extraBuf_Content(content)
        return extraBuf
    except:
        pass


def decodeExtraBuf(extra_buf_content: bytes):
    off = 0
    types = [b"\x04", b"\x18", b"\x17", b"\x02", b"\x05"]
    trunkName = {
        "46CF10C4": "个性签名",
        "A4D9024A": "国家",
        "E2EAA8D1": "省份",
        "1D025BBF": "市",
        "81AE19B4": "朋友圈背景url",
        "F917BCC0": "公司名称",
        "4EB96D85": "企业微信属性",
        "0E719F13": "备注图片",
        "759378AD": "手机号",
        "74752C06": "性别",
    }
    res = {'手机号': {'18': ''}}
    while off < len(extra_buf_content):
        length = 4  # 块头
        trunk_head = extra_buf_content[off: off + length]
        off += length
        trunk_head = binascii.hexlify(trunk_head).decode().upper()
        if trunk_head in trunkName:
            trunk_head = trunkName[trunk_head]
        res[trunk_head] = {}
        char = extra_buf_content[off: off + 1]
        off += 1
        field = binascii.hexlify(char).decode()
        if char == b"\x04":  # 四个字节的int，小端序
            length = 4
            intContent = extra_buf_content[off: off + length]
            off += 4
            intContent = int.from_bytes(intContent, "little")
            res[trunk_head][field] = intContent
        elif char == b"\x18":  # utf-16字符串
            length = 4
            lengthContent = extra_buf_content[off: off + length]
            off += 4
            lengthContent = int.from_bytes(lengthContent, "little")
            strContent = extra_buf_content[off: off + lengthContent]
            off += lengthContent
            res[trunk_head][field] = strContent.decode("utf-16").rstrip("\x00")
        elif char == b"\x17":  # utf-8 protobuf
            length = 4
            lengthContent = extra_buf_content[off: off + length]
            off += 4
            lengthContent = int.from_bytes(lengthContent, "little")
            strContent = extra_buf_content[off: off + lengthContent]
            off += lengthContent
            res[trunk_head][field] = parseExtraBuf(strContent)
        elif char == b"\x02":  # 一个字节的int
            content = extra_buf_content[off: off + 1]
            off += 1
            res[trunk_head][field] = int.from_bytes(content, "little")
        elif char == b"\x05":  # 暂时不知道有啥用，固定8个字节，先当int处理
            length = 8
            content = extra_buf_content[off: off + length]
            off += length
            res[trunk_head][field] = int.from_bytes(content, "little")
    # print(res)

    return {
        'region': (res['国家']['18'], res['省份']['18'], res['市']['18']),
        'signature': res['个性签名']['18'],
        'telephone': res['手机号']['18'],
        'gender': res['性别']['04']
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
            except AttributeError:
                self.init_database()
                self.video_cursor.execute(sql, [md5])
            result = self.video_cursor.fetchone()
            return result
        finally:
            video_db_lock.release()

    def get_image(self, content, bytesExtra, thumb=False):
        bytesDict = parseBytes(bytesExtra)
        for msginfo in bytesDict[3]:
            if msginfo[1][1][1] == (3 if thumb else 4):
                pathh = msginfo[1][2][1]  # wxid\FileStorage\...
                pathh = "\\".join(pathh.split("\\")[1:])
                return pathh
        md5 = get_md5_from_xml(content)
        if not md5:
            return None
        result = self.get_image_by_md5(binascii.unhexlify(md5))

        if result:
            dir1 = result[3]
            dir2 = result[4]
            data_image = result[2]
            dir0 = "Thumb" if thumb else "Image"
            dat_image = os.path.join(root_path, dir1, dir0, dir2, data_image)
            return dat_image

    def get_video(self, content, bytesExtra, thumb=False):
        bytesDict = parseBytes(bytesExtra)
        for msginfo in bytesDict[3]:
            if msginfo[1][1][1] == (3 if thumb else 4):
                pathh = msginfo[1][2][1]  # wxid\FileStorage\...
                pathh = "\\".join(pathh.split("\\")[1:])
                return pathh
        md5 = get_md5_from_xml(content, type_="video")
        if not md5:
            return None
        result = self.get_video_by_md5(binascii.unhexlify(md5))
        if result:
            dir2 = result[3]
            data_image = result[2].split(".")[0] + ".jpg" if thumb else result[2]
            # dir0 = 'Thumb' if thumb else 'Image'
            dat_image = os.path.join(video_root_path, dir2, data_image)
            return dat_image

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
