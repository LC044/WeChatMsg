import os
import copy
import random
import threading
import subprocess
import gradio as gr
from typing import List, Optional, Tuple, Dict


os.system("pip uninstall -y tensorflow tensorflow-estimator tensorflow-io-gcs-filesystem")
os.environ["LANG"] = "C"
os.environ["LC_ALL"] = "C"

default_system = '你是一个微信聊天机器人'

from dashinfer.helper import EngineHelper, ConfigManager

log_lock = threading.Lock()

config_file = "di_config.json"
config = ConfigManager.get_config_from_json(config_file)

def download_model(model_id, revision, source="modelscope"):
    print(f"Downloading model {model_id} (revision: {revision}) from {source}")
    if source == "modelscope":
        from modelscope import snapshot_download
        model_dir = snapshot_download(model_id, revision=revision)
    elif source == "huggingface":
        from huggingface_hub import snapshot_download
        model_dir = snapshot_download(repo_id=model_id)
    else:
        raise ValueError("Unknown source")

    print(f"Save model to path {model_dir}")

    return model_dir

cmd = f"pip show dashinfer | grep 'Location' | cut -d ' ' -f 2"
package_location = subprocess.run(cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  shell=True,
                                  text=True)
package_location = package_location.stdout.strip()
os.environ["AS_DAEMON_PATH"] = package_location + "/dashinfer/allspark/bin"
os.environ["AS_NUMA_NUM"] = str(len(config["device_ids"]))
os.environ["AS_NUMA_OFFSET"] = str(config["device_ids"][0])

## download original model
## download model from modelscope
original_model = {
    "source": "modelscope",
    "model_id": config["model_space"] + config["model_name"],
    "revision": "master",
    "model_path": ""
}
original_model["model_path"] = download_model(original_model["model_id"],
                                              original_model["revision"],
                                              original_model["source"])

engine_helper = EngineHelper(config)
engine_helper.verbose = True
engine_helper.init_tokenizer(original_model["model_path"])

## convert huggingface model to dashinfer model
## only one conversion is required
engine_helper.convert_model(original_model["model_path"])

engine_helper.init_engine()
engine_max_batch = engine_helper.engine_config["engine_max_batch"]

###################################################

History = List[Tuple[str, str]]
Messages = List[Dict[str, str]]


class Role:
    USER = 'user'
    SYSTEM = 'system'
    BOT = 'bot'
    ASSISTANT = 'assistant'
    ATTACHMENT = 'attachment'


def clear_session() -> History:
    return '', []


def modify_system_session(system: str) -> str:
    if system is None or len(system) == 0:
        system = default_system
    return system, system, []


def history_to_messages(history: History, system: str) -> Messages:
    messages = [{'role': Role.SYSTEM, 'content': system}]
    for h in history:
        messages.append({'role': Role.USER, 'content': h[0]})
        messages.append({'role': Role.ASSISTANT, 'content': h[1]})
    return messages


def messages_to_history(messages: Messages) -> Tuple[str, History]:
    assert messages[0]['role'] == Role.SYSTEM
    system = messages[0]['content']
    history = []
    for q, r in zip(messages[1::2], messages[2::2]):
        history.append([q['content'], r['content']])
    return system, history


def message_to_prompt(messages: Messages) -> str:
    prompt = ""
    for item in messages:
        im_start, im_end = "<|im_start|>", "<|im_end|>"
        prompt += f"\n{im_start}{item['role']}\n{item['content']}{im_end}"
    prompt += f"\n{im_start}assistant\n"
    return prompt


def model_chat(query: Optional[str], history: Optional[History],
               system: str) -> Tuple[str, str, History]:
    if query is None:
        query = ''
    if history is None:
        history = []

    messages = history_to_messages(history, system)
    messages.append({'role': Role.USER, 'content': query})
    prompt = message_to_prompt(messages)

    gen_cfg = copy.deepcopy(engine_helper.default_gen_cfg)
    gen_cfg["max_length"] = 1024
    gen_cfg["seed"] = random.randint(0, 10000)

    request_list = engine_helper.create_request([prompt], [gen_cfg])

    request = request_list[0]
    gen = engine_helper.process_one_request_stream(request)
    for response in gen:
        role = Role.ASSISTANT
        system, history = messages_to_history(messages + [{'role': role, 'content': response}])
        yield '', history, system

    json_str = engine_helper.convert_request_to_jsonstr(request)
    log_lock.acquire()
    try:
        print(f"{json_str}\n")
    finally:
        log_lock.release()

###################################################

with gr.Blocks() as demo:
    demo_title = "<center>微信的你</center>"
    gr.Markdown(demo_title)
    with gr.Row():
        with gr.Column(scale=3):
            system_input = gr.Textbox(value=default_system,
                                      lines=1,
                                      label='System')
        with gr.Column(scale=1):
            modify_system = gr.Button("🛠️ Set system prompt and clear history.", scale=2)
        system_state = gr.Textbox(value=default_system, visible=False)
    chatbot = gr.Chatbot(label=config["model_name"])
    textbox = gr.Textbox(lines=2, label='Input')

    with gr.Row():
        clear_history = gr.Button("🧹清除历史记录")
        sumbit = gr.Button("🚀和我聊天!")

    sumbit.click(model_chat,
                 inputs=[textbox, chatbot, system_state],
                 outputs=[textbox, chatbot, system_input],
                 concurrency_limit=engine_max_batch)
    clear_history.click(fn=clear_session,
                        inputs=[],
                        outputs=[textbox, chatbot],
                        concurrency_limit=engine_max_batch)
    modify_system.click(fn=modify_system_session,
                        inputs=[system_input],
                        outputs=[system_state, system_input, chatbot],
                        concurrency_limit=engine_max_batch)

demo.queue(api_open=False).launch(height=800, share=False, server_name="127.0.0.1", server_port=7860)
