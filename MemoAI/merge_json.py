import json
import os

data_dir = r'E:\Project\Python\MemoTrace\data\聊天记录'

dev_res = []
train_res = []

for filepath, dirnames, filenames in os.walk(data_dir):
    for filename in filenames:
        if filename.endswith('.json'):
            print(filename, filepath)
            filepath_ = os.path.join(filepath, filename)
            with open(filepath_, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data:
                if filename.endswith('train.json'):
                    train_res += data
                else:
                    dev_res += data

with open('train.json', 'w', encoding='utf-8') as f:
    json.dump(train_res, f, ensure_ascii=False, indent=4)

with open('dev.json', 'w', encoding='utf-8') as f:
    json.dump(dev_res, f, ensure_ascii=False, indent=4)
