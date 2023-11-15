import os.path
import sqlite3

DB = None
cursor = None
micromsg_path = "./app/Database/Msg/MicroMsg.db"
if os.path.exists(micromsg_path):
    DB = sqlite3.connect(micromsg_path, check_same_thread=False)
    # '''创建游标'''
    cursor = DB.cursor()


def is_database_exist():
    return os.path.exists(micromsg_path)


def get_contact():
    sql = '''select UserName,Alias,Type,Remark,NickName,PYInitial,RemarkPYInitial,ContactHeadImgUrl.smallHeadImgUrl,ContactHeadImgUrl.bigHeadImgUrl
          from Contact inner join ContactHeadImgUrl on Contact.UserName = ContactHeadImgUrl.usrName
          where  Type=3 and Alias is not null 
          order by PYInitial
          '''
    cursor.execute(sql)
    result = cursor.fetchall()
    # pprint(result)
    # print(len(result))
    return result


if __name__ == '__main__':
    get_contact()
