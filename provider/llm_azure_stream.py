import os
import re

from dotenv import load_dotenv
from openai import AzureOpenAI
import json
import logging

load_dotenv(override=True)


client = AzureOpenAI(
    api_key=os.environ['AZURE_OPENAI_API_KEY'],
    api_version=os.environ['OPENAI_API_VERSION'],
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT']
    )


class LLMAzureOpenAIStream:
    def __init__(self, stream=False, socketio=None):
        self.stream = stream
        self.socketio = socketio

    def generate_text(self, text, sys_prompt, reqid):
        logging.info(f"使用模型【Azure OpenAI】stream={self.stream}, f{os.environ['OPENAI_DEPLOYMENT_NAME']}, f{reqid}")
        try:
            response = client.chat.completions.create(
                model=os.environ['OPENAI_DEPLOYMENT_NAME'],  # model = "deployment_name"
                # response_format={"type": "json_object"},  # 用这个格式容易出错
                temperature=0,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": text}
                ],
                stream=self.stream
            )
        except Exception as e:
            print(f"调用openai出错：{e}")
            return json.dumps({"error": "fail: 调用大模型接口出错"})

        result = ""
        if not self.stream:
            result = response.choices[0].message.content
            logging.info(f"total tokens: {response.usage.total_tokens}")
        else:
            for chunk in response:
                if len(chunk.choices) == 0:
                    continue
                if chunk.choices[0].delta.content is not None:
                    result += chunk.choices[0].delta.content
                    if self.socketio:
                        self.socketio.emit('stream_chunk', {'text': result})
                    print(chunk.choices[0].delta.content, end="")

        logging.info(f"raw result: {result}")

        return result
