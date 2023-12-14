import os
import winreg

from app.person import MePC
from app.util import dat2pic

os.makedirs('./data/image', exist_ok=True)


def get_abs_path(path, base_path="/data/image"):
    # return os.path.join(os.getcwd(), 'app/data/icons/404.png')
    if path:
        base_path = os.getcwd() + base_path
        output_path = dat2pic.decode_dat(os.path.join(MePC().wx_dir, path), base_path)
        return output_path if output_path else ':/icons/icons/404.png'
    else:
        return ':/icons/icons/404.png'


def get_relative_path(path, base_path, type_='image'):
    if path:
        base_path = os.getcwd() + base_path
        output_path = dat2pic.decode_dat(os.path.join(MePC().wx_dir, path), base_path)
        relative_path = './image/' + os.path.basename(
            output_path) if output_path else 'https://www.bing.com/images/search?view=detailV2&ccid=Zww6woP3&id=CCC91337C740656E800E51247E928ACD3052FECF&thid=OIP.Zww6woP3Em49TdSG_lnggAHaEK&mediaurl=https%3a%2f%2fmeekcitizen.files.wordpress.com%2f2018%2f09%2f404.jpg%3fw%3d656&exph=360&expw=640&q=404&simid=608040792714530493&FORM=IRPRST&ck=151E7337A86F1B9C5C5DB08B15B90809&selectedIndex=21&itb=0'
        return relative_path
    else:
        return ':/icons/icons/404.png'


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def wx_path():
    try:
        ## 获取当前用户名
        user_home = os.environ.get("USERPROFILE")
        ## 找到3ebffe94.ini配置文件
        f = open(user_home + '\\AppData\\Roaming\\Tencent\\WeChat\\All Users\\config\\3ebffe94.ini', encoding='utf-8')
        txt = f.read()
        f.close()
        # 打开Windows注册表
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        # 获取“我的文档”路径的注册表键值
        documents_path_value = winreg.QueryValueEx(reg_key, "Personal")
        # 输出路径
        ##读取文件将路径放到wx_location变量里
        if txt == 'MyDocument:':
            wx_location = documents_path_value[0] + '\WeChat Files'
        else:
            wx_location = txt + "\WeChat Files"
        return wx_location
    except FileNotFoundError:
        return '.'
