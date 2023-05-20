# 微信聊天记录可视化

## 功能

- 显示聊天界面
- 导出聊天记录成Word文档
- 分析聊天数据，做成可视化年报

## 效果

![image-20230520235113261](doc/images/image-20230520235113261.png)

![image-20230520235220104](doc/images/image-20230520235220104.png)

![image-20230520235338305](doc/images/image-20230520235338305.png)

![image-20230520235351749](doc/images/image-20230520235351749.png)

![image-20230520235400772](doc/images/image-20230520235400772.png)

![image-20230520235409112](doc/images/image-20230520235409112.png)

![image-20230520235422128](doc/images/image-20230520235422128.png)

![image-20230520235431091](doc/images/image-20230520235431091.png)

## 使用

1. 根据[教程](https://blog.csdn.net/m0_59452630/article/details/124222235?spm=1001.2014.3001.5501)获得两个文件
    - auth_info_key_prefs.xml——解析数据库密码
    - EnMicroMsg.db——聊天数据库
2. 安装依赖库

命令行运行以下代码

```bash
pip install -r requirements.txt
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

## 项目还有很多bug，希望各位大佬能够共享代码

项目地址：https://github.com/LC044/WeChatMsg
