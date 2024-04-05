import json
from uuid import uuid4

from flask import Blueprint, request, jsonify, Response
from db.models import Extractor, get_session


# todo: 未考虑多用户
prompt_template = ""
# 创建 Blueprint
extractor = Blueprint('extractor', __name__)


# 定义路由和视图函数
@extractor.route('/extractor', methods=['POST'])
def create():
    """Endpoint to create an extractor."""
    create_request = request.get_json()

    instance = Extractor(
        name=create_request['name'],
        owner_id=request.headers.get('x-key'),
        uuid=str(uuid4()),
        instruction=create_request['instruction'],
        # schema=json.dumps(create_request['schema']),
        # description=create_request['description'],
    )

    with get_session() as session:
        session.add(instance)
        session.flush()  # 强制执行数据库操作但不提交
        uuid_str = instance.uuid

    return jsonify({'status': 'success', "uuid": uuid_str}), 201


@extractor.route('/extractor', methods=['PUT'])
def update():
    """Endpoint to update an extractor."""
    update_request = request.get_json()

    with get_session() as session:
        instance = session.query(Extractor).filter_by(uuid=update_request['uuid']).first()
        if instance:
            instance.name = update_request['name']
            instance.owner_id = request.headers.get('x-key')
            instance.instruction = update_request['instruction']
            # instance.schema = json.dumps(update_request['schema'])
            # instance.description = update_request['description']
            session.commit()
            return jsonify({'status': 'success', "uuid": instance.uuid}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Extractor not found'}), 404


@extractor.route('/extractor/<uuid>', methods=['DELETE'])
def delete(uuid):
    """Endpoint to delete an extractor."""
    with get_session() as session:
        instance = session.query(Extractor).filter_by(uuid=uuid).first()
        if instance:
            session.delete(instance)
            session.commit()
            return jsonify({'status': 'success', "message": "Extractor deleted"}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Extractor not found'}), 404


@extractor.route('/extractor', methods=['GET'])
def get():
    response_data = []
    """Endpoint to get all extractors."""
    with get_session() as session:
        extractors = session.query(Extractor).all()
        # extractors按照updated_at从大到小排序
        extractors.sort(key=lambda x: x.updated_at, reverse=True)

        response_data = {"data":
            [{
                "uuid": e.uuid,
                "name": e.name,
                "description": e.description,
                "instruction": e.instruction,
                "selected": e.selected,
            } for e in extractors]
        }

        # 设置默认值
        global prompt_template
        for e in extractors:
            if e.selected:
                prompt_template = e.instruction
                break

    # json.dumps 序列化数据，避免中文乱码
    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json')


@extractor.route('/extractor/selected', methods=['POST'])
def select():
    """Endpoint to select an extractor."""
    select_request = request.get_json()

    with get_session() as session:
        instance = session.query(Extractor).filter_by(uuid=select_request['uuid']).first()
        if not instance:
            return jsonify({'status': 'error', 'message': 'Extractor not found'}), 404

        instance.selected = True
        # 将所有列表中的selected设为False
        session.query(Extractor).filter(Extractor.uuid != select_request['uuid']).update({Extractor.selected: False})
        session.commit()

        # 设置默认值
        global prompt_template
        prompt_template = instance.instruction

        return jsonify({'status': 'success', "uuid": instance.uuid}), 200


def get_prompt_template():
    return prompt_template


def init():
    with get_session() as session:
        instance = session.query(Extractor).filter_by(selected=True).first()
        if instance:
            # 设置默认值
            global prompt_template
            prompt_template = instance.instruction

init()