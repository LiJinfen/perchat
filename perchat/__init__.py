# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import os

import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from perchat.blueprints.admin import admin_bp
from perchat.blueprints.auth import auth_bp
from perchat.blueprints.chat import chat_bp
from perchat.extensions import db, login_manager, csrf, socketio, moment, oauth,migrate
from perchat.models import User, Message, Room,User_Has_Room
from perchat.settings import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'production')

    app = Flask('perchat')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_commands(app)

    return app


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)
    moment.init_app(app)
    oauth.init_app(app)
    migrate.init_app(app,db)




def register_blueprints(app):
    app.register_blueprint(auth_bp)

    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', description=e.description, code=e.code), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', description=e.description, code=e.code), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', description='Internal Server Error', code='500'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('error.html', description=e.description, code=e.code), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:

            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--message', default=300, help='Quantity of messages, default is 300.')
    def forge(message):
        """Generate fake data."""
        import random
        from sqlalchemy.exc import IntegrityError

        from faker import Faker

        fake = Faker()

        click.echo('Initializing the database...')
        db.drop_all()
        db.create_all()

        click.echo('Forging the data...')
        admin = User(nickname='admin', email='admin@qq.com')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()

        click.echo('Generating users...')
        users = []
        for i in range(50):
            user = User(nickname='u'+str(i),
                        bio=fake.sentence(),
                        github=fake.url(),
                        website=fake.url(),
                        email=fake.email()
                        )
            user.set_password('123456')
            db.session.add(user)
            users.append(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

        user = User(nickname='wangjutou',
                    email='wang@qq.com'
                    )
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()


        # click.echo('Generating messages...')
        # messages=[]
        # for i in range(message):
        #     message = Message(
        #         sender=User.query.get(random.randint(1, User.query.count())),
        #         body=fake.sentence(),
        #         timestamp=fake.date_time_between('-30d', '-2d'),
        #         persuasive=0
        #     )
        #     db.session.add(message)
        #     messages.append(message)
        #
        # db.session.commit()

        click.echo('Generating rooms...')
        rooms=[]
        # click.echo(messages)
        for i in range(10):

            room = Room(
            name = i,
            description = i,
            owner = admin.nickname,
            # first_owner_id = admin.id
            # messages = messages[i:i+20]

            )

            db.session.add(room)
            db.session.commit()
            userhasroom = User_Has_Room(user_id=admin.id, room_id=room.id, room_type=0, status=1, user=admin, room=room)
            db.session.add(userhasroom)
            db.session.commit()
            rooms.append(room)
            # try:
            #     db.session.commit()
            # except IntegrityError:
            #     db.session.rollback()

        click.echo('Generating userhasroom...')
        # u0,u1->private room 0

        message = Message(
                    sender_id=users[0].id,
                    body=fake.sentence(),
                    timestamp=fake.date_time_between('-34d', '-32d'),
                    persuasive=0,room_id=rooms[0].id
                )
        db.session.add(message)
        message = Message(
            sender_id=users[1].id,
            body=fake.sentence(),
            timestamp=fake.date_time_between('-30d', '-2d'),
            persuasive=0, room_id=rooms[0].id
        )
        db.session.add(message)
        rooms[0].owner=''
        user_has_room = User_Has_Room(status=0,room_type=1,quit_time=fake.date_time_between('-32d', '-30d'))
        user_has_room.user = users[0]
        rooms[0].first_owner_id = users[0].id
        user_has_room.room = rooms[0]
        db.session.add(user_has_room)
        user_has_room = User_Has_Room(status=0, room_type=1)
        user_has_room.user = users[1]
        rooms[0].second_owner_id = users[1].id
        user_has_room.room = rooms[0]
        db.session.add(user_has_room)

        # u0,u2->private room 1
        message = Message(
            sender_id=users[0].id,
            body=fake.sentence(),
            timestamp=fake.date_time_between('-30d', '-2d'),
            persuasive=0, room_id=rooms[1].id
        )
        db.session.add(message)
        message = Message(
            sender_id=users[2].id,
            body=fake.sentence(),
            timestamp=fake.date_time_between('-30d', '-2d'),
            persuasive=0, room_id=rooms[1].id
        )
        db.session.add(message)
        rooms[1].owner=''
        user_has_room = User_Has_Room(status=0, room_type=1)
        user_has_room.user = users[0]
        rooms[1].first_owner_id = users[0].id
        user_has_room.room = rooms[1]
        db.session.add(user_has_room)
        user_has_room = User_Has_Room(status=0, room_type=1)
        user_has_room.user = users[2]
        rooms[1].second_owner_id = users[2].id
        user_has_room.room = rooms[1]
        db.session.add(user_has_room)

        # u1,u2->private room 3
        message = Message(
            sender_id=users[1].id,
            body=fake.sentence(),
            timestamp=fake.date_time_between('-30d', '-2d'),
            persuasive=0, room_id=rooms[3].id
        )
        db.session.add(message)
        message = Message(
            sender_id=users[2].id,
            body=fake.sentence(),
            timestamp=fake.date_time_between('-30d', '-2d'),
            persuasive=0, room_id=rooms[3].id
        )
        db.session.add(message)
        rooms[3].owner=''
        user_has_room = User_Has_Room(status=1, room_type=1)
        user_has_room.user = users[1]
        rooms[3].first_owner_id = users[1].id
        user_has_room.room = rooms[3]
        db.session.add(user_has_room)
        user_has_room = User_Has_Room(status=1, room_type=1)
        user_has_room.user = users[2]
        rooms[3].second_owner_id = users[2].id
        user_has_room.room = rooms[3]
        db.session.add(user_has_room)
        db.session.commit()

        # u0,u1,u2->group room 2
        message = Message(
            sender_id=users[0].id,
            body=fake.sentence(),
            timestamp=fake.date_time_between('-34d', '-32d'),
            persuasive=0, room_id=rooms[2].id
        )
        db.session.add(message)
        message = Message(
            sender_id=users[1].id,
            body=fake.sentence(),
            timestamp=fake.date_time_between('-30d', '-2d'),
            persuasive=0, room_id=rooms[2].id
        )
        db.session.add(message)
        message = Message(
            sender_id=users[2].id,
            body=fake.sentence(),
            timestamp=fake.date_time_between('-30d', '-2d'),
            persuasive=0, room_id=rooms[2].id
        )
        db.session.add(message)
        user_has_room = User_Has_Room(status=1, room_type=0,quit_time=fake.date_time_between('-32d', '-30d'))
        user_has_room.user = users[0]
        rooms[2].first_owner_id = admin.id
        user_has_room.room = rooms[2]
        db.session.add(user_has_room)
        user_has_room = User_Has_Room(status=1, room_type=0)
        user_has_room.user = users[1]
        user_has_room.room = rooms[2]
        db.session.add(user_has_room)
        user_has_room = User_Has_Room(status=1, room_type=0)
        user_has_room.user = users[2]
        user_has_room.room = rooms[2]
        db.session.add(user_has_room)
        db.session.commit()
        click.echo('Done.')
