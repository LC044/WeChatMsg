import os

# 图片字节头信息，
# [0][1]为jpg头信息，
# [2][3]为png头信息，
# [4][5]为gif头信息
pic_head = [0xff, 0xd8, 0x89, 0x50, 0x47, 0x49]
# 解密码
decode_code = 0


def get_code(file_path):
    """
    自动判断文件类型，并获取dat文件解密码
    :param file_path: dat文件路径
    :return: 如果文件为jpg/png/gif格式，则返回解密码，否则返回-1
    """
    if os.path.isdir(file_path):
        return -1, -1
    # if file_path[-4:] != ".dat":
    #     return -1, -1
    dat_file = open(file_path, "rb")
    dat_read = dat_file.read(2)
    # print(dat_read)
    head_index = 0
    while head_index < len(pic_head):
        # 使用第一个头信息字节来计算加密码
        # 第二个字节来验证解密码是否正确
        code = dat_read[0] ^ pic_head[head_index]
        idf_code = dat_read[1] ^ code
        head_index = head_index + 1
        if idf_code == pic_head[head_index]:
            dat_file.close()
            return head_index, code
        head_index = head_index + 1
    dat_file.close()
    print("not jpg, png, gif")
    return -1, -1


def decode_dat(file_path, out_path):
    """
    解密文件，并生成图片
    :param file_path: dat文件路径
    :return: 无
    """
    if not os.path.exists(file_path):
        return None
    file_type, decode_code = get_code(file_path)

    if decode_code == -1:
        return
    if file_type == 1:
        pic_name = os.path.basename(file_path)[:-4] + ".jpg"
    elif file_type == 3:
        pic_name = file_path[:-4] + ".png"
    elif file_type == 5:
        pic_name = file_path[:-4] + ".gif"
    else:
        pic_name = file_path[:-4] + ".jpg"
    file_outpath = os.path.join(out_path, pic_name)
    if os.path.exists(file_outpath):
        return file_outpath
    with open(file_path, 'rb') as file_in:
        data = file_in.read()
    # 对数据进行异或加密/解密
    with open(file_outpath, 'wb') as file_out:
        file_out.write(bytes([byte ^ decode_code for byte in data]))
    print(file_path, '->', file_outpath)
    return file_outpath


def find_datfile(dir_path, out_path):
    """
    获取dat文件目录下所有的文件
    :param dir_path: dat文件目录
    :return: 无
    """
    files_list = os.listdir(dir_path)
    for file_name in files_list:
        file_path = dir_path + "\\" + file_name
        decode_dat(file_path, out_path)


if __name__ == "__main__":
    path = "E:\86390\Documents\WeChat Files\wxid_27hqbq7vx5hf22\FileStorage\CustomEmotion\\71\\"
    outpath = "D:\\test"
    if not os.path.exists(outpath):
        os.mkdir(outpath)
    find_datfile(path, outpath)
