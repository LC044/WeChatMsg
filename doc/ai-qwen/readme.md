**鉴于** 本仓库原来的训练模型 `Chatllm3-6b` 在低性能机器上部署比较困难,我在原基础上使用微型模型 `Qwen2-0.5b-Instruct` 模型完成模型训练到部署到免费 
Modelspace 创空间中，比较简单，`并且可做到全程免费` 下面是流程：
***
# 第一步，[创建 Modelspace 免费 GPU](https://www.modelscope.cn/my/mynotebook/preset)
![GPU](/MemoAI/img/img3.png)

# 开始训练
**可以参照训练[模板](/MemoAI/qwen2-0.5b/train.md)**
<br>
把 `train.json` 上传,一步步点击即可<br>
最后把模型上传到 `Modelspace`
<br />
![训练](/MemoAI/img/img4.png)
# 部署到创空间
编辑 `di_config.json` 的一下两个字段
`model_space: YOUR-NAME-SPACE` 
`model_name: YOUR-MODEL-NAME`

**然后把一下MemoAI/qwen2-0.5b的三个文件:`di_config.json`,`app.py`,`requirements.txt`上传到创空间,点击部署！**

**最后看看成品吧：**[成品](https://www.modelscope.cn/studios/sanbei101/qwen-haoran/summary)