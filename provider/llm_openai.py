import json
import logging

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
client = OpenAI()


class LLMOpenAI:
    def __init__(self, model, stream=False, socketio=None):
        self.model = model
        self.socketio = socketio
        self.stream = stream

    def generate_text(self, text, sys_prompt, reqid):
        print("使用模型API：", self.model, reqid)
        try:
            response = client.chat.completions.create(
                model=self.model,
                # response_format={"type": "json_object"},
                temperature=0,
                stream=self.stream,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": text}
                ]
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
