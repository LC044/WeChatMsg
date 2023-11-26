<h1 align="center">我的数据我做主</h1>
<div align="center">
<img src="https://img.shields.io/badge/WeChat-解密-blue.svg">
<a href="https://github.com/LC044/WeChatMsg/stargazers">
    <img src="https://img.shields.io/github/stars/LC044/WeChatMsg.svg" />
</a>
<a href="https://github.com/LC044/WeChatMsg/issues">
      <img alt="Issues" src="https://img.shields.io/github/issues/LC044/WeChatMsg?color=0088ff" />
    </a>
<a href="./doc/readme.md">
    <img src="https://img.shields.io/badge/文档-最新-brightgreen.svg" />
</a>
<a href="LICENSE">
    <img src="https://img.shields.io/github/license/LC044/WeChatMsg" />
</a>
</div>
<div align="center">

<a><img src="./doc/images/logo.png" height="240"/></a>
</div>

## 功能

- 破解📱手机微信数据库
- 安卓 or 苹果都可以哦
- 破解💻PC端微信数据库
- 还原微信聊天界面
    - 文本
    - 图片
- 导出聊天记录
    - HTML(文本)
    - Word文档
    - CSV文档
- 分析聊天数据，做成可视化年报
- 🔥**项目持续更新中**
- 小伙伴们想要其他功能可以留言哦🏆
- 有任何问题可以随时联系我(863909694@qq.com)

为了方便大家交流，我新建了一个QQ群💬：**474379264**

大家有任何想法、建议或bug可以群里反馈给我

[//]: # (<img src="doc/images/qq.jpg" height=480/>)

## 效果

<details>

<img alt="聊天界面" src="doc/images/chat_.png"/>

<img alt="image-20230520235113261" src="doc/images/image-20230520235113261.png"/>

![image-20230520235220104](doc/images/image-20230520235220104.png)

![image-20230520235338305](doc/images/image-20230520235338305.png)

![image-20230520235351749](doc/images/image-20230520235351749.png)

![image-20230520235400772](doc/images/image-20230520235400772.png)

![image-20230520235409112](doc/images/image-20230520235409112.png)

![image-20230520235422128](doc/images/image-20230520235422128.png)

![image-20230520235431091](doc/images/image-20230520235431091.png)

</details>

# 使用

## 解密PC版微信数据库

<details>

### 1. 安装

```shell
git clone https://github.com/LC044/WeChatMsg
cd WeChatMsg
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 使用

1. 登录微信
2. 运行程序
   ```shell
   python decrypt_window.py
   ```
3. 点击获取信息

   ![](./doc/images/pc_decrypt_info.png)
4. 设置微信安装路径
   可以到微信->设置->文件管理查看
   ![](./doc/images/setting.png)

   点击**设置微信路径**按钮，选择该文件夹路径下的带有wxid_xxx的路径
   ![](./doc/images/path_select.png)

5. 获取到密钥和微信路径之后点击开始解密
6. 解密后的数据库文件保存在./app/DataBase/Msg路径下

### 3. 查看

随便下载一个SQLite数据库查看软件就能打开数据库，例如[DB Browser for SQLite](https://sqlitebrowser.org/dl/)

* [数据库功能介绍](./doc/数据库介绍.md)
* [更多功能介绍](./doc/电脑端使用教程.md)

显示效果
<img alt="聊天界面" src="doc/images/chat_.png"/>

</details>

### 使用模拟器

<details>

1. 根据[教程](https://blog.csdn.net/m0_59452630/article/details/124222235?spm=1001.2014.3001.5501)获得两个文件
    - auth_info_key_prefs.xml——解析数据库密码
    - EnMicroMsg.db——聊天数据库
    - **上面这两个文件就可以**
2. 安装依赖库

python版本>=3.10

**说明:用到了python3.10的match语法，不方便更换python版本的小伙伴可以把match(运行报错的地方)更改为if else**

命令行运行以下代码（**建议使用Pycharm打开项目，Pycharm会自动配置好所有东西，直接运行main.py即可**）

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

运行main.py

```bash
python main.py
```

3. 出现解密界面

![image-20230521001305274](doc/images/image-20230521001305274.png)

按照提示选择上面获得的两个文件，等待解密完成，重新运行程序

4. 进入主界面

这时候不显示头像，因为头像文件没有导入进来

![image-20230521001547481](doc/images/image-20230521001547481.png)

根据[教程](https://blog.csdn.net/m0_59452630/article/details/124222235?spm=1001.2014.3001.5501)
将头像文件夹avatar复制到工程目录./app/data/目录下

![image-20230521001726799](doc/images/image-20230521001726799.png)

如果想要显示聊天图像就把[教程](https://blog.csdn.net/m0_59452630/article/details/124222235?spm=1001.2014.3001.5501)
里的image2文件夹复制到./app/data文件夹里，效果跟上图一样

复制进来之后再运行程序就有图像了

![image-20230520235113261](doc/images/image-20230520235113261.png)

</details>

## 项目还有很多bug，希望大家能够及时反馈

项目地址：https://github.com/LC044/WeChatMsg

# 致谢

* PC微信解密工具:[https://github.com/xaoyaoo/PyWxDump](https://github.com/xaoyaoo/PyWxDump)

---

> 说明：该项目仅可用于交流学习，禁止任何非法用途，创作者不承担任何责任🙄

[![Star History Chart](https://api.star-history.com/svg?repos=LC044/WeChatMsg&type=Date)](https://star-history.com/?utm_source=bestxtools.com#LC044/WeChatMsg&Date)
