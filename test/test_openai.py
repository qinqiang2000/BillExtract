import json
from dotenv import load_dotenv
from openai import OpenAI
from provider.prompt import base_prompt


load_dotenv(override=True)
client = OpenAI()


class LLMOpenAI:
    def __init__(self, model):
        self.model = model

    def generate_text(self, text, sys_prompt, reqid):
        print("使用模型API：", self.model, reqid)
        try:
            stream = client.chat.completions.create(
                model=self.model,
                # response_format={"type": "json_object"},
                temperature=0,
                stream=True,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": text}
                ]
            )
        except Exception as e:
            print(f"调用openai出错：{e}")
            return json.dumps({"error": "fail: 调用大模型接口出错"})

        ret = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                ret += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="")

        return ret


text = """
聚龙大厦缴费通知书
缴费单位:杭州肯德基有限公司
建筑面积:3391.88㎡²
内容:
1、1月份水费:743.82元
2、1月份电费:19046.19元
共付金额:19790.01元
请贵公司在此通知书发出后15日内前来大厦物管处缴纳
如有疑问,请与物业公司管理处联系
电话:28918868 28918869
注:物业管理收费说明:总建筑面积3391.88㎡×10元×3个月
水电费收费见《水电缴费明细表》
杭州聚龙物业管理有限公司
聚龙大厦管理处
2024年2月26日
"""
result = LLMOpenAI("gpt-4-1106-preview").generate_text(text, base_prompt, "")
print(result)