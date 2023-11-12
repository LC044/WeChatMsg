import sqlite3
from pprint import pprint

DB = sqlite3.connect("./de_MicroMsg.db", check_same_thread=False)
# '''创建游标'''
cursor = DB.cursor()


def get_contact():
    sql = '''select UserName,Alias,Type,Remark,NickName,PYInitial,RemarkPYInitial,ContactHeadImgUrl.smallHeadImgUrl,ContactHeadImgUrl.bigHeadImgUrl
          from Contact inner join ContactHeadImgUrl on Contact.UserName = ContactHeadImgUrl.usrName
          where  Type=3 and Alias is not null 
          order by PYInitial
          '''
    cursor.execute(sql)
    result = cursor.fetchall()
    pprint(result)
    print(len(result))
    return result


if __name__ == '__main__':
    get_contact()
