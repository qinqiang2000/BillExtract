import json
import os
import logging
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
client = OpenAI(api_key=os.environ['MOONSHOT_API_KEY'], base_url="https://api.moonshot.cn/v1")

# 去除 JSON 字符串中的单行注释
def remove_comments(json_str):
    # 使用正则表达式匹配以 // 开头的注释，并去除这些注释
    # 注意：这可能会误删除字符串内部包含 // 的情况
    no_comments = re.sub(r'//.*', '', json_str)
    return no_comments

class LLMMoonshot:
    def __init__(self, model):
        self.model = model

    def generate_text(self, text, sys_prompt, reqid):
        print("使用模型API：", self.model, reqid)
        try:
            response = client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": text}
                ]
            )
        except Exception as e:
            print(f"调用openai出错：{e}")
            return json.dumps({"error": "fail: 调用大模型接口出错"})

        result = response.choices[0].message.content
        logging.info(f"total tokens: {response.usage.total_tokens}")

        result = result[result.find('['):result.rfind(']') + 1]
        logging.info(result)

        # 去除 JSON 字符串中的单行注释
        result = remove_comments(result)
        logging.info(f"\nclean json:\n{result}")

        # 去除usage产生的可能错误的JSON字符串
        result = re.sub(r'^.*?"Usage": .*? - .*(?=\n|$)', '', result, flags=re.MULTILINE)
        logging.info(f"clean usage: {result}")

        return result
