from bs4 import BeautifulSoup


def create_title_page(nickname, time, avatar_path):
    with open('D:\\Project\\Python\\WeChatMsg\\app\\data\\html\\0.html', 'r+', encoding='utf-8') as f:
        html_document = f.read()
        # 创建Beautiful Soup对象
        soup = BeautifulSoup(html_document, 'html.parser')
        # 找到需要替换的图片元素
        target_image = soup.find(id='avatar')
        # 替换图片元素的src属性
        if target_image:
            target_image['src'] = avatar_path
        # 找到需要替换的元素
        target_element = soup.find(id='nickname')
        # 替换元素的文本内容
        if target_element:
            target_element.string = nickname
        target_element = soup.find(id='first_time')
        # 替换元素的文本内容
        if target_element:
            target_element.string = time
        with open('./data/AnnualReport/0.html', 'w', encoding='utf-8') as f1:
            f1.write(soup.prettify())


if __name__ == '__main__':
    create_title_page('小学生', '2023-09-18 20:39:08', 'D:\Project\Python\WeChatMsg\\app\data\icons\default_avatar.svg')
