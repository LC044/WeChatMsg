import os
import traceback

from app.log import logger
from app.person import Me

# 图片字节头信息，
# [0][1]为jpg头信息，
# [2][3]为png头信息，
# [4][5]为gif头信息
pic_head = [0xff, 0xd8, 0x89, 0x50, 0x47, 0x49]
# 解密码
decode_code = 0


def get_code(dat_read) -> tuple[int, int]:
    """
    自动判断文件类型，并获取dat文件解密码
    :param file_path: dat文件路径
    :return: 如果文件为jpg/png/gif格式，则返回解密码，否则返回-1
    """
    try:
        if not dat_read:
            return -1, -1
        head_index = 0
        while head_index < len(pic_head):
            # 使用第一个头信息字节来计算加密码
            # 第二个字节来验证解密码是否正确
            code = dat_read[0] ^ pic_head[head_index]
            idf_code = dat_read[1] ^ code
            head_index = head_index + 1
            if idf_code == pic_head[head_index]:
                return head_index, code
            head_index = head_index + 1
        print("not jpg, png, gif")
        return -1, -1
    except:
        logger.error(f'image解析发生了错误:\n\n{traceback.format_exc()}')
        return -1, -1


def decode_dat(file_path, out_path) -> str:
    """
    解密文件，并生成图片
    :param file_path: dat文件路径
    :return: 无
    """
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'rb') as file_in:
        data = file_in.read()

    file_type, decode_code = get_code(data[:2])
    if decode_code == -1:
        return ''

    filename = os.path.basename(file_path)
    if file_type == 1:
        pic_name = os.path.basename(file_path)[:-4] + ".jpg"
    elif file_type == 3:
        pic_name = filename[:-4] + ".png"
    elif file_type == 5:
        pic_name = filename[:-4] + ".gif"
    else:
        pic_name = filename[:-4] + ".jpg"
    file_outpath = os.path.join(out_path, pic_name)
    if os.path.exists(file_outpath):
        return file_outpath

    # 对数据进行异或加密/解密
    with open(file_outpath, 'wb') as file_out:
        file_out.write(bytes([byte ^ decode_code for byte in data]))
    print(file_path, '->', file_outpath)
    return file_outpath


def decode_dat_path(file_path, out_path) -> str:
    """
    解密文件，并生成图片
    :param file_path: dat文件路径
    :return: 无
    """
    if not os.path.exists(file_path):
        return ''
    with open(file_path, 'rb') as file_in:
        data = file_in.read(2)
    file_type, decode_code = get_code(data)
    if decode_code == -1:
        return ''
    filename = os.path.basename(file_path)
    if file_type == 1:
        pic_name = os.path.basename(file_path)[:-4] + ".jpg"
    elif file_type == 3:
        pic_name = filename[:-4] + ".png"
    elif file_type == 5:
        pic_name = filename[:-4] + ".gif"
    else:
        pic_name = filename[:-4] + ".jpg"
    file_outpath = os.path.join(out_path, pic_name)
    return file_outpath


def get_image(path, base_path) -> str:
    if path:
        base_path = os.path.join(os.getcwd(),base_path)
        output_path = decode_dat(os.path.join(Me().wx_dir, path), base_path)
        relative_path = './image/' + os.path.basename(
            output_path) if output_path else 'https://www.bing.com/images/search?view=detailV2&ccid=Zww6woP3&id=CCC91337C740656E800E51247E928ACD3052FECF&thid=OIP.Zww6woP3Em49TdSG_lnggAHaEK&mediaurl=https%3a%2f%2fmeekcitizen.files.wordpress.com%2f2018%2f09%2f404.jpg%3fw%3d656&exph=360&expw=640&q=404&simid=608040792714530493&FORM=IRPRST&ck=151E7337A86F1B9C5C5DB08B15B90809&selectedIndex=21&itb=0'
        return relative_path
    else:
        return ':/icons/icons/404.png'


def get_image_abs_path(path, base_path) -> str:
    if path:
        base_path = os.path.join(os.getcwd(),base_path)
        output_path = decode_dat(os.path.join(Me().wx_dir, path), base_path)
        return output_path
    else:
        return ':/icons/icons/404.png'


def get_image_path(path, base_path) -> str:
    if path:
        base_path = os.getcwd() + base_path
        output_path = decode_dat_path(os.path.join(Me().wx_dir, path), base_path)
        relative_path = './image/' + os.path.basename(
            output_path) if output_path else 'https://www.bing.com/images/search?view=detailV2&ccid=Zww6woP3&id=CCC91337C740656E800E51247E928ACD3052FECF&thid=OIP.Zww6woP3Em49TdSG_lnggAHaEK&mediaurl=https%3a%2f%2fmeekcitizen.files.wordpress.com%2f2018%2f09%2f404.jpg%3fw%3d656&exph=360&expw=640&q=404&simid=608040792714530493&FORM=IRPRST&ck=151E7337A86F1B9C5C5DB08B15B90809&selectedIndex=21&itb=0'
        return relative_path
    else:
        return ':/icons/icons/404.png'


if __name__ == "__main__":
    pass
