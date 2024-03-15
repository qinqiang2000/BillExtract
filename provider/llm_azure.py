import os
import re

from dotenv import load_dotenv
from openai import AzureOpenAI
import json

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


class LLMAzureOpenAI:
    def generate_text(self, text, sys_prompt, reqid):
        print("使用模型【Azure OpenAI】", os.environ['OPENAI_DEPLOYMENT_NAME'], reqid)
        try:
            response = client.chat.completions.create(
                model=os.environ['OPENAI_DEPLOYMENT_NAME'],  # model = "deployment_name"
                # response_format={"type": "json_object"},  # 用这个格式容易出错
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
        print("total tokens:", response.usage.total_tokens)

        result = result[result.find('['):result.rfind(']') + 1]
        print(result)

        # 去除 JSON 字符串中的单行注释
        result = remove_comments(result)
        print("\nclean json:\n", result)

        # 去除usage产生的可能错误的JSON字符串
        result = re.sub(r'^.*?"Usage": .*? - .*(?=\n|$)', '', result, flags=re.MULTILINE)
        print("clean Usage:", result)

        return result
