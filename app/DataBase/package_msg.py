import threading

from app.DataBase import msg_db, micro_msg_db
from app.util.protocbuf.msg_pb2 import MessageBytesExtra
from app.util.protocbuf.roomdata_pb2 import ChatRoomData

lock = threading.Lock()


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


@singleton
class PackageMsg:
    def __init__(self):
        self.ChatRoomMap = {}

    def get_package_message_all(self):
        '''
        获取完整的聊天记录
        '''
        updated_messages = []  # 用于存储修改后的消息列表

        messages = msg_db.get_messages_all()
        for row in messages:
            row_list = list(row)
            # 删除不使用的几个字段
            del row_list[12]
            del row_list[11]
            del row_list[10]

            strtalker = row[11]
            info = micro_msg_db.get_contact_by_username(strtalker)
            if info is not None:
                row_list.append(info[3])
                row_list.append(info[4])
            # 判断是否是群聊
            if strtalker.__contains__('@chatroom'):
                # 自己发送
                if row[12] == 1:
                    row_list.append('我')
                else:
                    # 存在BytesExtra为空的情况，此时消息类型应该为提示性消息。跳过不处理
                    if row[10] is None:
                        continue
                    # 解析BytesExtra
                    msgbytes = MessageBytesExtra()
                    msgbytes.ParseFromString(row[10])
                    wxid = ''
                    for tmp in msgbytes.message2:
                        if tmp.field1 != 1:
                            continue
                        wxid = tmp.field2
                    sender = ''
                    # 获取群聊成员列表
                    membersMap = self.get_chatroom_member_list(strtalker)
                    if membersMap is not None:
                        if wxid in membersMap:
                            sender = membersMap.get(wxid)
                        else:
                            senderinfo = micro_msg_db.get_contact_by_username(wxid)
                            if senderinfo is not None:
                                sender = senderinfo[4]
                                membersMap[wxid] = senderinfo[4]
                                if len(senderinfo[3]) > 0:
                                    sender = senderinfo[3]
                                    membersMap[wxid] = senderinfo[3]
                    row_list.append(sender)
            updated_messages.append(tuple(row_list))
        return updated_messages

    def get_chatroom_member_list(self, strtalker):
        membermap = {}
        '''
        获取群聊成员
        '''
        try:
            lock.acquire(True)
            if strtalker in self.ChatRoomMap:
                membermap = self.ChatRoomMap.get(strtalker)
            else:
                chatroom = micro_msg_db.get_chatroom_info(strtalker)
                if chatroom is None:
                    return None
                # 解析RoomData数据
                parsechatroom = ChatRoomData()
                parsechatroom.ParseFromString(chatroom[1])
                # 群成员数据放入字典存储
                for mem in parsechatroom.members:
                    if mem.displayName is not None and len(mem.displayName) > 0:
                        membermap[mem.wxID] = mem.displayName
                self.ChatRoomMap[strtalker] = membermap
        finally:
            lock.release()
        return membermap
