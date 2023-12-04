from collections import Counter

from PyQt5.QtCore import QFile, QTextStream, QIODevice

from app.DataBase import msg_db, MsgType
from app.person_pc import ContactPC
import jieba
from pyecharts import options as opts
from pyecharts.charts import Pie, WordCloud, Calendar, Bar, Line, Timeline, Grid
from app.resources import resource_rc

var = resource_rc.qt_resource_name
charts_width = 800
charts_height = 450
wordcloud_width = 780
wordcloud_height = 720


def wordcloud(wxid):
    import jieba
    txt_messages = msg_db.get_messages_by_type(wxid, MsgType.TEXT)
    text = ''.join(map(lambda x: x[7], txt_messages))
    total_msg_len = len(text)
    # 使用jieba进行分词，并加入停用词
    words = jieba.cut(text)
    # 统计词频
    word_count = Counter(words)
    # 过滤停用词
    stopwords_file = './app/data/stopwords.txt'
    try:
        with open(stopwords_file, "r", encoding="utf-8") as stopword_file:
            stopwords = set(stopword_file.read().splitlines())
    except:
        file = QFile(':/data/stopwords.txt')
        if file.open(QIODevice.ReadOnly | QIODevice.Text):
            stream = QTextStream(file)
            stream.setCodec('utf-8')
            content = stream.readAll()
            file.close()
            stopwords = set(content.splitlines())
    filtered_word_count = {word: count for word, count in word_count.items() if len(word) > 1 and word not in stopwords}

    # 转换为词云数据格式
    data = [(word, count) for word, count in filtered_word_count.items()]
    # text_data = data
    data.sort(key=lambda x: x[1], reverse=True)

    text_data = data[:100] if len(data) > 100 else data
    # 创建词云图
    keyword, max_num = text_data[0]
    w = (
        WordCloud(init_opts=opts.InitOpts(width=f"{wordcloud_width}px", height=f"{wordcloud_height}px"))
        .add(series_name="聊天文字", data_pair=text_data, word_size_range=[20, 100])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"词云图", subtitle=f"总计{total_msg_len}字",
                title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    # return w.render_embed()
    return {
        'chart_data': w.dump_options_with_quotes(),
        'keyword': keyword,
        'max_num': str(max_num),
        'dialogs': msg_db.get_messages_by_keyword(wxid, keyword, num=5)
    }


class Analysis:
    pass


if __name__ == '__main__':
    msg_db.init_database(path='../DataBase/Msg/MSG.db')
    w = wordcloud('wxid_0o18ef858vnu22')
    print(w)
