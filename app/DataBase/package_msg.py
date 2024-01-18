import threading

from app.DataBase import msg_db, micro_msg_db, misc_db
from app.util.protocbuf.msg_pb2 import MessageBytesExtra
from app.util.protocbuf.roomdata_pb2 import ChatRoomData
from app.person import Contact, Me, ContactDefault

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
            del row_list[13]
            del row_list[12]
            del row_list[11]
            del row_list[10]
            del row_list[9]

            strtalker = row[11]
            info = micro_msg_db.get_contact_by_username(strtalker)
            if info is not None:
                row_list.append(info[3])
                row_list.append(info[4])
            else:
                row_list.append('')
                row_list.append('')
            # 判断是否是群聊
            if strtalker.__contains__('@chatroom'):
                # 自己发送
                if row[4] == 1:
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
            else:
                if row[4] == 1:
                    row_list.append('我')
                else:
                    if info is not None:
                        row_list.append(info[4])
                    else:
                        row_list.append('')
            updated_messages.append(tuple(row_list))
        return updated_messages
    
    def get_package_message_by_wxid(self, chatroom_wxid):
        '''
        获取一个群聊的聊天记录
        return list
            a[0]: localId,
            a[1]: talkerId, （和strtalker对应的，不是群聊信息发送人）
            a[2]: type,
            a[3]: subType,
            a[4]: is_sender,
            a[5]: timestamp,
            a[6]: status, （没啥用）
            a[7]: str_content,
            a[8]: str_time, （格式化的时间）
            a[9]: msgSvrId,
            a[10]: BytesExtra,
            a[11]: CompressContent,
            a[12]: DisplayContent,
            a[13]: msg_sender, （ContactPC 或 ContactDefault 类型，这个才是群聊里的信息发送人，不是群聊或者自己是发送者没有这个字段）
        '''
        updated_messages = []  # 用于存储修改后的消息列表
        messages = msg_db.get_messages(chatroom_wxid)
        for row in messages:
            message = list(row)
            if message[4] == 1: # 自己发送的就没必要解析了
                message.append(Me())
                updated_messages.append(message)
                continue
            if message[10] is None: # BytesExtra是空的跳过
                message.append(ContactDefault(wxid))
                updated_messages.append(message)
                continue
            msgbytes = MessageBytesExtra()
            msgbytes.ParseFromString(message[10])
            wxid = ''
            for tmp in msgbytes.message2:
                if tmp.field1 != 1:
                    continue
                wxid = tmp.field2
            if wxid == "": # 系统消息里面 wxid 不存在
                message.append(ContactDefault(wxid))
                updated_messages.append(message)
                continue
            contact_info_list = micro_msg_db.get_contact_by_username(wxid)
            if contact_info_list is None: # 群聊中已退群的联系人不会保存在数据库里
                message.append(ContactDefault(wxid))
                updated_messages.append(message)
                continue
            contact_info = {
                'UserName': contact_info_list[0],
                'Alias': contact_info_list[1],
                'Type': contact_info_list[2],
                'Remark': contact_info_list[3],
                'NickName': contact_info_list[4],
                'smallHeadImgUrl': contact_info_list[7]
            }
            contact = Contact(contact_info)
            contact.smallHeadImgBLOG = misc_db.get_avatar_buffer(contact.wxid)
            contact.set_avatar(contact.smallHeadImgBLOG)
            message.append(contact)
            updated_messages.append(tuple(message))
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

if __name__ == "__main__":
    p = PackageMsg()
    print(p.get_package_message_by_wxid("48615079469@chatroom"))
