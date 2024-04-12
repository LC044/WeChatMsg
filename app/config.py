import os

version = '2.0.5'
contact = '701805520'
github = 'https://github.com/LC044/WeChatMsg'
website = 'https://memotrace.cn/'
copyright = '© 2022-2024 SiYuan'
license = 'GPLv3'
description = [
    '1. 支持获取个人信息<br>',
    '2. 支持显示聊天界面<br>',
    '3. 支持导出聊天记录<br>&nbsp;&nbsp;&nbsp;&nbsp;* csv<br>&nbsp;&nbsp;&nbsp;&nbsp;* html<br>&nbsp;&nbsp;&nbsp;&nbsp;* '
    'txt<br>&nbsp;&nbsp;&nbsp;&nbsp;* docx<br>',
    '4. 生成年度报告——圣诞特别版',
]
about = f'''
    版本：{version}<br>
    QQ交流群:请关注微信公众号回复：联系方式<br>
    地址：<a href='{github}'>{github}</a><br>
    官网：<a href='{website}'>{website}</a><br>
    新特性:<br>{''.join(['' + i for i in description])}<br>
    License <a href='https://github.com/LC044/WeChatMsg/blob/master/LICENSE' target='_blank'>{license}</a><br>
    Copyright {copyright}
'''

# 数据存放文件路径
INFO_FILE_PATH = './app/data/info.json'  # 个人信息文件
DB_DIR = './app/Database/Msg'
OUTPUT_DIR = './data/'  # 输出文件夹
os.makedirs('./app/data', exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
# 全局参数
SEND_LOG_FLAG = True  # 是否发送错误日志
SERVER_API_URL = 'http://api.lc044.love'  # api接口