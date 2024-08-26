from flask import Blueprint, jsonify, request, current_app
from src.tasks.saveTaskTime import saveTaskLongTime
from marshmallow_dataclass import class_schema
from dataclasses import dataclass
from celery.result import AsyncResult
from celery.app.control import Inspect
from celery.contrib.abortable import AbortableAsyncResult

@dataclass
class TextBody:
    text: str

TextBodySchema = class_schema(TextBody)()


task_bp = Blueprint("task", __name__, url_prefix="/task")

@task_bp.post('/add-task/')
def add_task():
    body = request.get_json()
    validated_data: TextBody = TextBodySchema.load(body)
    task: AsyncResult = saveTaskLongTime.apply_async(args=[validated_data.text], retry=True, retry_policy={'max_retries': 3})
    return jsonify({"task_id": task.id}), 200


@task_bp.route('/<task_id>', methods=['GET'])
def get_task_info(task_id: str):
    result = AsyncResult(task_id)
    response = {
        'task_id': task_id,
        'state': result.state,
        'result': result.result
    }
    return jsonify(response)


@task_bp.route('/reserved', methods=['GET'])
def list_reserved_tasks():
    i: Inspect = current_app.celery.control.inspect()
    reserved_tasks = i.active_queues()
    return jsonify(reserved_tasks)


@task_bp.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.json.get('task_id')
    if not task_id:
        return jsonify({"error": "task_id is required"}), 400
    
    # celery: Celery = current_app.celery  # Access Celery instance
    # control: Control =  celery.control
    # control.revoke(task_id, terminate=True)  # or use terminate=False
    task = AbortableAsyncResult(task_id)
    # print(result.)
    # task.abort(terminate=True,signal='SIGTERM')
    task.abort()
    
    return jsonify({"message": f"Task {task_id} has been revoked and terminated."}), 200