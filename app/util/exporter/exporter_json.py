import json
import random
import os

from app.DataBase import msg_db
from app.person import Me
from .exporter import ExporterBase


def merge_content(conversions_list) -> list:
    """
    合并一组对话中连续发送的句子
    @param conversions_list:
    @return:
    """
    merged_data = []
    current_role = None
    current_content = ""
    str_time = ''
    for item in conversions_list:
        if 'str_time' in item:
            str_time = item['str_time']
        else:
            str_time = ''
        if current_role is None:
            current_role = item["role"]
            current_content = item["content"]
        elif current_role == item["role"]:
            current_content += "\n" + item["content"]
        else:
            # merged_data.append({"role": current_role, "content": current_content, 'str_time': str_time})
            merged_data.append({"role": current_role, "content": current_content})
            current_role = item["role"]
            current_content = item["content"]
            str_time = item.get('str_time')

    # 处理最后一组
    if current_role is not None:
        # merged_data.append({"role": current_role, "content": current_content,'str_time': str_time})
        merged_data.append({"role": current_role, "content": current_content})
    return merged_data


def system_prompt():
    system = {
        "role": "system",
        # "content": f"你是{Me().name}，一个聪明、热情、善良的男大学生，后面的对话来自{self.contact.remark}(！！！注意：对方的身份十分重要，你务必记住对方的身份，因为跟不同的人对话要用不同的态度、语气)，你要认真地回答他"
        "content": f"你是{Me().name}，一个聪明、热情、善良的人，后面的对话来自你的朋友，你要认真地回答他"
    }
    return system


def message_to_conversion(group):
    conversions = [system_prompt()]
    while len(group) and group[-1][4] == 0:
        group.pop()
    for message in group:
        is_send = message[4]
        if len(conversions) == 1 and is_send:
            continue
        if is_send:
            json_msg = {
                "role": "assistant",
                "content": message[7]
            }
        else:
            json_msg = {
                "role": "user",
                "content": message[7]
            }
        json_msg['str_time'] = message[8]
        conversions.append(json_msg)
    if len(conversions) == 1:
        return []
    return merge_content(conversions)


class JsonExporter(ExporterBase):
    def split_by_time(self, length=300):
        messages = msg_db.get_messages_by_type(self.contact.wxid, type_=1, time_range=self.time_range)
        start_time = 0
        res = []
        i = 0
        while i < len(messages):
            message = messages[i]
            timestamp = message[5]
            is_send = message[4]
            group = [
                system_prompt()
            ]
            while i < len(messages) and timestamp - start_time < length:
                if is_send:
                    json_msg = {
                        "role": "assistant",
                        "content": message[7]
                    }
                else:
                    json_msg = {
                        "role": "user",
                        "content": message[7]
                    }
                group.append(json_msg)
                i += 1
                if i >= len(messages):
                    break
                message = messages[i]
                timestamp = message[5]
                is_send = message[4]
            while is_send:
                json_msg = {
                    "role": "assistant",
                    "content": message[7]
                }
                group.append(json_msg)
                i += 1
                if i >= len(messages):
                    break
                message = messages[i]
                timestamp = message[5]
                is_send = message[4]
            start_time = timestamp
            res.append(
                {
                    "conversations": group
                }
            )
        res_ = []
        for item in res:
            conversations = item['conversations']
            res_.append({
                'conversations': merge_content(conversations)
            })
        return res_

    def split_by_intervals(self, max_diff_seconds=300):
        messages = msg_db.get_messages_by_type(self.contact.wxid, type_=1, time_range=self.time_range)
        res = []
        i = 0
        current_group = []
        while i < len(messages):
            message = messages[i]
            timestamp = message[5]
            is_send = message[4]
            while is_send and i + 1 < len(messages):
                i += 1
                message = messages[i]
                is_send = message[4]
            current_group = [messages[i]]
            i += 1
            while i < len(messages) and messages[i][5] - current_group[-1][5] <= max_diff_seconds:
                current_group.append(messages[i])
                i += 1
            while i < len(messages) and messages[i][4]:
                current_group.append(messages[i])
                i += 1
            res.append(current_group)
        res_ = []
        for group in res:
            conversations = message_to_conversion(group)
            if conversations:
                res_.append({
                    'conversations': conversations
                })
        return res_

    def to_json(self):
        print(f"【开始导出 json {self.contact.remark}】")
        origin_path = self.origin_path
        os.makedirs(origin_path, exist_ok=True)
        filename = os.path.join(origin_path, f"{self.contact.remark}")

        # res = self.split_by_time()
        res = self.split_by_intervals(60)
        # 打乱列表顺序
        random.shuffle(res)

        # 计算切分比例
        split_ratio = 0.2  # 20% for the second list

        # 计算切分点
        split_point = int(len(res) * split_ratio)

        # 分割列表
        train_data = res[split_point:]
        dev_data = res[:split_point]
        with open(f'{filename}_train.json', "w", encoding="utf-8") as f:
            json.dump(train_data, f, ensure_ascii=False, indent=4)
        with open(f'{filename}_dev.json', "w", encoding="utf-8") as f:
            json.dump(dev_data, f, ensure_ascii=False, indent=4)
        self.okSignal.emit(1)

    def run(self):
        self.to_json()
