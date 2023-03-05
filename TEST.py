import os
import openai

print("欢迎使用ChatGPT智能问答，请在Q:后面输入你的问题，输入quit退出！")
openai.api_key = '''eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiI4NjM5MDk2OTRAcXEuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImdlb2lwX2NvdW50cnkiOiJVUyJ9LCJodHRwczovL2FwaS5vcGVuYWkuY29tL2F1dGgiOnsidXNlcl9pZCI6InVzZXItdmdiMG1IeU5MQUNHRG1qRndrekVMNVM3In0sImlzcyI6Imh0dHBzOi8vYXV0aDAub3BlbmFpLmNvbS8iLCJzdWIiOiJhdXRoMHw2M2RjYmNiZWRiNzFkNmVhMzA5YmEzYzciLCJhdWQiOlsiaHR0cHM6Ly9hcGkub3BlbmFpLmNvbS92MSIsImh0dHBzOi8vb3BlbmFpLm9wZW5haS5hdXRoMGFwcC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjc1NDEyNTg2LCJleHAiOjE2NzYwMTczODYsImF6cCI6IlRkSkljYmUxNldvVEh0Tjk1bnl5d2g1RTR5T282SXRHIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBtb2RlbC5yZWFkIG1vZGVsLnJlcXVlc3Qgb3JnYW5pemF0aW9uLnJlYWQgb2ZmbGluZV9hY2Nlc3MifQ.dlTy6oc0eIDIJg0AqlFdarXWh7h-n7C6id3Kv5-uOrASoYB3qtfhPMuj15yV0VOOmFyj_L7v3MCpPEnsJp08NJo1Jn32jKtCkKD-sy8DpT5rafj_B6TKNvEBsqdXgDENg0ly9KiAjS-HDlCmQoBEqg-kc2VaqlpPIfk-164WI2SCTgQb50GNKWu0jwG-lx8BHnY8gUqC7sGVx4Hg9sLHccyAL93kMu4NS-S9CsqNefYAolLbqQLPBOG9MFaTD1jvyZpuqwm3eiv7HwgHempVWAfCK9sfGBblExHRT5zi0oSGwwBGmi2EnBHjEX185RRqtuH_uKRwp47m0TcHulJsfQ'''

start_sequence = "\nA:"
restart_sequence = "\nQ: "
while True:
    prompt = input(restart_sequence)
    if prompt == 'quit':
        break
    else:
        try:
            response = openai.Completion.create(
                model="text-davinci-003",  # 这里我们使用的是davinci-003的模型，准确度更高。
                prompt=prompt,
                temperature=1,
                max_tokens=2000,  # 这里限制的是回答的长度，你可以可以限制字数，如:写一个300字作文等。
                frequency_penalty=0,
                presence_penalty=0
            )
            print(start_sequence, response["choices"][0]["text"].strip())
        except Exception as exc:  # 捕获异常后打印出来
            print(exc)
