import os
import re

from dotenv import load_dotenv
from openai import AzureOpenAI
import json
import logging

load_dotenv(override=True)


# 去除 JSON 字符串中的单行注释
def remove_comments(json_str):
    # 使用正则表达式匹配以 // 开头的注释，并去除这些注释
    # 注意：这可能会误删除字符串内部包含 // 的情况
    no_comments = re.sub(r'//.*', '', json_str)
    return no_comments


client = AzureOpenAI(
    api_key=os.environ['AZURE_OPENAI_API_KEY'],
    api_version=os.environ['OPENAI_API_VERSION'],
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT']
    )


class LLMAzureOpenAIStream:
    def __init__(self, socketio):
        self.socketio = socketio
        pass

    def generate_text(self, text, sys_prompt, reqid):
        print("使用模型【Azure OpenAI】", os.environ['OPENAI_DEPLOYMENT_NAME'], reqid)
        try:
            stream = client.chat.completions.create(
                model=os.environ['OPENAI_DEPLOYMENT_NAME'],  # model = "deployment_name"
                # response_format={"type": "json_object"},  # 用这个格式容易出错
                temperature=0,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": text}
                ],
                stream=True,
            )
        except Exception as e:
            print(f"调用openai出错：{e}")
            return json.dumps({"error": "fail: 调用大模型接口出错"})

        result = ""
        for chunk in stream:
            if len(chunk.choices) == 0:
                continue
            if chunk.choices[0].delta.content is not None:
                result += chunk.choices[0].delta.content
                if self.socketio:
                    self.socketio.emit('stream_chunk', {'text': result})
                print(chunk.choices[0].delta.content, end="")

        result = result[result.find('['):result.rfind(']') + 1]
        logging.info(result)

        # 去除 JSON 字符串中的单行注释
        result = remove_comments(result)
        logging.info(f"\nclean json:\n{result}")

        # 去除usage产生的可能错误的JSON字符串
        result = re.sub(r'^.*?"Usage": .*? - .*(?=\n|$)', '', result, flags=re.MULTILINE)
        logging.info(f"clean usage: {result}")

        return result
