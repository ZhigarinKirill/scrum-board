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


@cross_origin()
@user_pages.route("/register", methods=['POST'])
def register():
    try:
        username = request.json.get('username', None)
        email = request.json.get('email', None)
        password = request.json.get('password', None)

        if username is None:
            return abort(401, description="Username missing")
        if email is None:
            return abort(401, description="Email missing")
        if password is None:
            return abort(401, description="Password missing")

        password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        user = User(username=username, email=email,
                    password=password.decode('utf8'))
        db.session.add(user)
        db.session.commit()

        return {"msg": "User successfully registered"}, 201

    except IntegrityError:
        db.session.rollback()
        return abort(400, description="Username or email already used")


@cross_origin()
@user_pages.route("/login", methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if username is None:
        return abort(401, description="Username missing")
    # if not email:
    #     return abort(400, description="Email missing")
    if password is None:
        return abort(401, description="Password missing")

    user = User.query.filter_by(username=username).first()
    if user is None:
        return abort(404, description="User not found")

    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        access_token = create_access_token(identity=user.id)

        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    else:
        return abort(401, description="Invalid password")


@user_pages.route("//refresh", methods=["POST"])
@jwt_required(refresh=True)
@cross_origin()
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify(access_token=access_token)


@cross_origin()
@user_pages.route("", methods=['GET'])
def get_all_users():
    users = User.query.all()
    return json.dumps([user.serialize for user in users])


# @cross_origin()
# @user_pages.route("/tasks", methods=['GET'])
# def get_all_tasks():
#     tasks = Task.query.all()
#     return json.dumps([task.serialize for task in tasks])


@user_pages.route("/", methods=['GET'])
@jwt_required()
@cross_origin()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return abort(404, description="User not found")
    return user.serialize


@user_pages.route("/tasks/create", methods=['POST'])
@jwt_required()
@cross_origin()
def create_task():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return abort(404, description="User not found")

    title = request.json.get('title', None)
    description = request.json.get('description', None)
    status = 0

    if title is None or description is None:
        return abort(401, description="Task info missing")

    task = Task(title=title, description=description,
                status=status)
    user_task = UserTask(user_id=user_id, task_id=task.id, owner_id=user_id)
    # db.session.add(task)

    user.users_tasks.append(user_task)
    task.users_tasks.append(user_task)

    db.session.add_all([user, task])
    db.session.commit()

    return task.serialize


@user_pages.route("/tasks", methods=['GET'])
@jwt_required()
@cross_origin()
def get_user_tasks():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return abort(404, description="User not found")

    user_task_filtered_by_user_id = UserTask.query.filter_by(user_id=user_id)
    task_ids = [user_task.task_id for user_task in user_task_filtered_by_user_id]
    owner_ids = [
        user_task.owner_id for user_task in user_task_filtered_by_user_id]
    # return json.dumps([ut.task_id for ut in task_ids])
    tasks = Task.query.filter(Task.id.in_(task_ids))
    return json.dumps([extend_dict(task.serialize, 'owner_id', owner_id) for task, owner_id in zip(tasks, owner_ids)])


@user_pages.route("/tasks/<int:task_id>", methods=['DELETE'])
@jwt_required()
@cross_origin()
def delete_user_task(task_id: int):
    pass


@jwt_required()
@cross_origin()
@user_pages.route("//tasks/<int:task_id>", methods=['POST'])
def share_task_to_user(task_id: int):
    pass
