from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


user_task = db.Table(
    'user_task',
    db.Column('id', db.Integer, db.ForeignKey(
        'users.id'), primary_key=True),
    db.Column('id', db.Integer, db.ForeignKey(
        'tasks.id'), primary_key=True),
    db.Column('owner_id', db.Integer, nullable=False)
)


class UserTask(db.Model):
    __tablename__ = 'users_tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    owner_id = db.Column(db.Integer, nullable=False)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True,
                         nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)

    users_tasks = db.relationship('UserTask', backref='user',
                                  primaryjoin=id == UserTask.user_id)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
        }


class Task(db.Model):
    __tablename__ = 'tasks'
    __table_args__ = (
        db.CheckConstraint('status in (0, 1, 2)'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Integer, nullable=False)

    users_tasks = db.relationship('UserTask', backref='task',
                                  primaryjoin=id == UserTask.task_id)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
        }
