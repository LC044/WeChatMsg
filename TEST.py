from snownlp import SnowNLP

# 文本
text = u'🙄”'
# 分析
s = SnowNLP(text)
# 输出情绪为积极的概率
print(s)
