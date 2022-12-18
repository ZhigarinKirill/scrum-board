import json
from typing import Any, Dict
from flask import abort, Blueprint, request, render_template, redirect, url_for, jsonify
from models import User, Task, UserTask, db
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from flask_cors import cross_origin
from sqlalchemy.exc import IntegrityError
import bcrypt


user_pages = Blueprint('users', __name__)


def extend_dict(source_dict: Dict[Any, Any], key: Any, value: Any) -> Dict[Any, Any]:
    copied_dict = source_dict.copy()  # NOT DEEP
    copied_dict[key] = value
    return copied_dict


@user_pages.route('/register', methods=['POST'])
@cross_origin()
def register():
    try:
        username = request.json.get('username', None)
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        if username is None:
            return abort(401, description='Username missing')
        if email is None:
            return abort(401, description='Email missing')
        if password is None:
            return abort(401, description='Password missing')

        password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        user = User(username=username, email=email,
                    password=password.decode('utf8'))
        db.session.add(user)
        db.session.commit()

        return {'msg': 'User successfully registered'}, 201

    except IntegrityError:
        db.session.rollback()
        return abort(400, description='Username or email already used')


@user_pages.route('/login', methods=['POST'])
@cross_origin()
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if username is None:
        return abort(401, description='Username missing')
    # if not email:
    #     return abort(400, description='Email missing')
    if password is None:
        return abort(401, description='Password missing')

    user = User.query.filter_by(username=username).first()
    if user is None:
        return abort(404, description='User not found')

    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        access_token = create_access_token(identity=user.id)

        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    else:
        return abort(401, description='Invalid password')


@user_pages.route('//refresh', methods=['POST'])
@jwt_required(refresh=True)
@cross_origin()
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify(access_token=access_token)


@cross_origin()
@user_pages.route('', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return json.dumps([user.serialize for user in users]), 200


# @cross_origin()
# @user_pages.route('/tasks', methods=['GET'])
# def get_all_tasks():
#     tasks = Task.query.all()
#     return json.dumps([task.serialize for task in tasks])


@user_pages.route('/', methods=['GET'])
@jwt_required()
@cross_origin()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return abort(404, description='User not found')
    return user.serialize, 200


@user_pages.route('/tasks/create', methods=['POST'])
@jwt_required()
@cross_origin()
def create_task():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return abort(404, description='User not found')

    title = request.json.get('title', None)
    description = request.json.get('description', None)
    status = 0

    if title is None or description is None:
        return abort(401, description='Task info missing')

    task = Task(title=title, description=description,
                status=status)
    user_task = UserTask(user_id=user_id, task_id=task.id, owner_id=user_id)
    # db.session.add(task)

    user.users_tasks.append(user_task)
    task.users_tasks.append(user_task)

    db.session.add_all([user, task])
    db.session.commit()

    return extend_dict(task.serialize, 'owner_id', user_id), 201


@user_pages.route('/tasks', methods=['GET'])
@jwt_required()
@cross_origin()
def get_user_tasks():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return abort(404, description='User not found')

    user_task_filtered_by_user_id = UserTask.query.filter_by(user_id=user_id)
    task_ids = [user_task.task_id for user_task in user_task_filtered_by_user_id]
    owner_ids = [
        user_task.owner_id for user_task in user_task_filtered_by_user_id]
    owner_names = [User.query.filter_by(
        id=owner_id).first().username for owner_id in owner_ids]
    # return json.dumps([ut.task_id for ut in task_ids])
    tasks = Task.query.filter(Task.id.in_(task_ids))
    return json.dumps([extend_dict(task.serialize, 'shared_by_name', name if user.username != name else None) for task, name in zip(tasks, owner_names)]),  200


@user_pages.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
@cross_origin()
def delete_user_task(task_id: int):
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return abort(404, description='User not found')

    deleting_task = UserTask.query.filter_by(
        user_id=user_id, task_id=task_id).first()
    if deleting_task is None:
        return abort(404, description=f'User does not have task with id={task_id}')

    deleting_task_owner_id = deleting_task.owner_id
    if deleting_task_owner_id == user_id:
        try:
            UserTask.query.filter_by(task_id=task_id).delete()

            Task.query.filter_by(id=task_id).delete()
            db.session.commit()
        except Exception as e:
            abort(409, description=f'Task cannot be deleted: {e}')
        return {'msg': 'Task was successfully deleted for all users', 'task_id': task_id, 'user_id': user_id}, 200

    try:
        UserTask.query.filter_by(
            user_id=user_id, task_id=task_id).delete()
        db.session.commit()
    except:  # find exception name
        abort(409, description='Task cannot be deleted')
    return {'msg': 'Task was successfully deleted', 'task_id': task_id, 'user_id': user_id}, 200


@user_pages.route('/tasks/<int:task_id>', methods=['POST'])
@cross_origin()
@jwt_required()
def share_task_to_user(task_id: int):
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return abort(404, description='User not found')

    destination_user_id = request.json.get('to_user', None)
    if destination_user_id is None:
        abort(404, description='User not found')

    destination_user = User.query.filter_by(id=destination_user_id).first()

    user_task = UserTask(user_id=int(destination_user_id),
                         task_id=task_id, owner_id=user_id)
    task = Task.query.filter_by(id=task_id).first()

    destination_user.users_tasks.append(user_task)
    task.users_tasks.append(user_task)

    db.session.add_all([user, task])
    db.session.commit()

    return extend_dict(task.serialize, 'to_user', destination_user_id), 201


@user_pages.route('/sharing_users', methods=['GET'])
@cross_origin()
@jwt_required()
def get_users_for_sharing():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    users = User.query.filter(User.id != user.id)
    return json.dumps([user.serialize for user in users]), 200


@user_pages.route('/tasks/<int:task_id>/<int:status>', methods=['PATCH'])
@cross_origin()
@jwt_required()
def change_status(task_id: int, status: int):
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return abort(404, description='User not found')

    if status not in (0, 1, 2):
        return abort(404, description='Invalid task status')

    task = Task.query.filter_by(id=task_id).first()
    task.status = status
    db.session.commit()

    return json.dumps({'task': task.serialize, 'msg': 'Status was successfully changed'}), 200
