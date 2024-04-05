import json
import logging
from uuid import uuid4

from dotenv import load_dotenv
from openai import OpenAI
from flask import Blueprint, request, jsonify, abort
from db.models import Extractor, get_session

load_dotenv(override=True)

logging.basicConfig(level=logging.DEBUG, force=True)

extract = Blueprint('extract', __name__)

tools_template = [{
  'type': 'function',
  'function': {
    'name': 'extractor',
    'description': 'Extract information matching the given schema.',
    'parameters': {
      'type': 'object',
      'properties': {
        'data': {
          'type': 'array',
          'items': None
        }
      },
      'required': ['data']
    }
  }
}]

tool_choice = {"type": "function", "function": {"name": "extractor"}}

client = OpenAI()


def chat_completion_request(messages, tools=None, tool_choice=None, model="gpt-3.5-turbo"):
    logging.info(f"Requesting ChatCompletion : \nmessages: {messages} \n tools: {tools} \n {tool_choice}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=0.0,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return None


def extract_from_content(text_, schema, instruction):
    messages = [{"role": "system",
                 "content": "You are a top-tier algorithm for extracting information from text. Only extract "
                            "information that is relevant to the provided text. If no information is relevant, "
                            "use the schema and output an empty list where appropriate.\n\n"
                            + instruction},
                {"role": "user", "content": f"I need to extract information from the following text: ```\n{text_}\n```"}
                ]

    tools = tools_template.copy()
    tools[0]['function']['parameters']['properties']['data']['items'] = json.loads(schema)

    response = chat_completion_request(messages, tools=tools, tool_choice=tool_choice, )
    if response is None:
        abort(500, description="Unable to generate ChatCompletion response")

    print(response)
    if not response.choices[0].message.tool_calls:
        return abort(500, description="Unable to generate ChatCompletion function call")

    return response.choices[0].message.tool_calls[0].function.arguments


# 定义路由和视图函数
@extract.route('/extract', methods=['POST'])
def extract_using_existing_extractor():
    """Endpoint that is used with an existing extractor.

    This endpoint will be expanded to support upload of binary files as well as
    text files.
    """
    # 获取表单数据
    extractor_id = request.form.get('extractor_id')
    text = request.form.get('text', None)
    mode = request.form.get('mode', "entire_document")
    file = request.files.get('file', None)
    user_id = request.headers.get('x-key')

    if text is None and file is None:
        abort(422, description="No text or file provided.")

    with get_session() as session:
        extractor = session.query(Extractor).filter_by(uuid=extractor_id, owner_id=user_id).scalar()
        if extractor is None:
            abort(404, description="Extractor not found for owner.")
        # 在 session 结束之前获取必要的属性
        instruction = extractor.instruction
        schema = extractor.schema

    if text:
        text_ = text
    else:
        # documents = parse_binary_input(file)
        # text_ = "\n".join([document.page_content for document in documents])
        text_ = text

    return extract_from_content(text_, schema, instruction)
