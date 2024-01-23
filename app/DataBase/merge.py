import os
import sqlite3
import traceback

from app.log import logger


def merge_MediaMSG_databases(source_paths, target_path):
    # 创建目标数据库连接
    target_conn = sqlite3.connect(target_path)
    target_cursor = target_conn.cursor()
    try:
        # 开始事务
        target_conn.execute("BEGIN;")
        for i, source_path in enumerate(source_paths):
            if not os.path.exists(source_path):
                continue
            db = sqlite3.connect(source_path)
            db.text_factory = str
            cursor = db.cursor()
            # 附加源数据库
            try:
                sql = '''SELECT Key,Reserved0,Buf,Reserved1,Reserved2 FROM Media;'''
                cursor.execute(sql)
                result = cursor.fetchall()
                target_cursor.executemany(
                    "INSERT INTO Media (Key,Reserved0,Buf,Reserved1,Reserved2)"
                    "VALUES(?,?,?,?,?)",
                    result)
            except sqlite3.IntegrityError:
                print("有重复key", "跳过")
            except sqlite3.OperationalError:
                print("no such table: Media", "跳过")
            cursor.close()
            db.close()
        # 提交事务
        target_conn.execute("COMMIT;")

    except Exception as e:
        # 发生异常时回滚事务
        target_conn.execute("ROLLBACK;")
        raise e

    finally:
        # 关闭目标数据库连接
        target_conn.close()


def merge_databases(source_paths, target_path):
    # 创建目标数据库连接
    target_conn = sqlite3.connect(target_path)
    target_cursor = target_conn.cursor()
    try:
        # 开始事务
        target_conn.execute("BEGIN;")
        for i, source_path in enumerate(source_paths):
            if not os.path.exists(source_path):
                continue
            db = sqlite3.connect(source_path)
            db.text_factory = str
            cursor = db.cursor()
            try:
                sql = '''
                    SELECT TalkerId,MsgsvrID,Type,SubType,IsSender,CreateTime,Sequence,StrTalker,StrContent,DisplayContent,BytesExtra,CompressContent
                    FROM MSG;
                '''
                cursor.execute(sql)
                result = cursor.fetchall()
                # 附加源数据库
                target_cursor.executemany(
                    "INSERT INTO MSG "
                    "(TalkerId,MsgsvrID,Type,SubType,IsSender,CreateTime,Sequence,StrTalker,StrContent,DisplayContent,"
                    "BytesExtra,CompressContent)"
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    result)
            except:
                logger.error(f'{source_path}数据库合并错误:\n{traceback.format_exc()}')
            cursor.close()
            db.close()
        # 提交事务
        target_conn.execute("COMMIT;")

    except Exception as e:
        # 发生异常时回滚事务
        target_conn.execute("ROLLBACK;")
        raise e

    finally:
        # 关闭目标数据库连接
        target_conn.close()


if __name__ == "__main__":
    # 源数据库文件列表
    source_databases = ["Msg/MSG1.db", "Msg/MSG2.db", "Msg/MSG3.db"]

    # 目标数据库文件
    target_database = "Msg/MSG.db"
    import shutil

    shutil.copy('Msg/MSG0.db', target_database)  # 使用一个数据库文件作为模板
    # 合并数据库
    merge_databases(source_databases, target_database)
