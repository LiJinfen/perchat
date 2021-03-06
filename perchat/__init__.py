# -*- coding: utf-8 -*-
"""
    :author: Jinfen Li
    :url: https: // github.com / LiJinfen
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

    # @app.cli.command()
    # @click.option('--message', default=300, help='Quantity of messages, default is 300.')
    # def forge(message):
    #     """Generate fake data."""
    #     import random
    #     from sqlalchemy.exc import IntegrityError
    #
    #     from faker import Faker
    #
    #     fake = Faker()
    #
    #     click.echo('Initializing the database...')
    #     db.drop_all()
    #     db.create_all()
    #
    #     click.echo('Forging the data...')
    #     admin = User(nickname='admin', email='admin@qq.com')
    #     admin.set_password('admin')
    #     db.session.add(admin)
    #     db.session.commit()
    #
    #     click.echo('Generating users...')
    #     users = []
    #     for i in range(50):
    #         user = User(nickname='u'+str(i),
    #                     bio=fake.sentence(),
    #                     github=fake.url(),
    #                     website=fake.url(),
    #                     email=fake.email()
    #                     )
    #         user.set_password('123456')
    #         db.session.add(user)
    #         users.append(user)
    #         try:
    #             db.session.commit()
    #         except IntegrityError:
    #             db.session.rollback()
    #
    #     user = User(nickname='wangjutou',
    #                 email='wang@qq.com'
    #                 )
    #     user.set_password('123456')
    #     db.session.add(user)
    #     db.session.commit()
    #
    #
    #     # click.echo('Generating messages...')
    #     # messages=[]
    #     # for i in range(message):
    #     #     message = Message(
    #     #         sender=User.query.get(random.randint(1, User.query.count())),
    #     #         body=fake.sentence(),
    #     #         timestamp=fake.date_time_between('-30d', '-2d'),
    #     #         persuasive=0
    #     #     )
    #     #     db.session.add(message)
    #     #     messages.append(message)
    #     #
    #     # db.session.commit()
    #
    #     click.echo('Generating rooms...')
    #     rooms=[]
    #     # click.echo(messages)
    #     for i in range(10):
    #
    #         room = Room(
    #         name = i,
    #         description = i,
    #         owner = admin.nickname,
    #         room_type=0,
    #             isShow=1
    #         # first_owner_id = admin.id
    #         # messages = messages[i:i+20]
    #
    #         )
    #
    #         db.session.add(room)
    #         db.session.commit()
    #         userhasroom = User_Has_Room(user_id=admin.id, room_id=room.id, status=1, user=admin, room=room)
    #         db.session.add(userhasroom)
    #         db.session.commit()
    #         rooms.append(room)
    #         # try:
    #         #     db.session.commit()
    #         # except IntegrityError:
    #         #     db.session.rollback()
    #
    #     click.echo('Generating userhasroom...')
    #     # u0,u1->private room 0
    #
    #     message = Message(
    #                 sender_id=users[0].id,
    #                 body=fake.sentence(),
    #                 timestamp=fake.date_time_between('-34d', '-32d'),
    #                 persuasive=0,room_id=rooms[0].id
    #             )
    #     db.session.add(message)
    #     message = Message(
    #         sender_id=users[1].id,
    #         body=fake.sentence(),
    #         timestamp=fake.date_time_between('-30d', '-2d'),
    #         persuasive=0, room_id=rooms[0].id
    #     )
    #     db.session.add(message)
    #     rooms[0].owner=''
    #     rooms[0].room_type = 1
    #     user_has_room = User_Has_Room(status=0,quit_time=fake.date_time_between('-32d', '-30d'))
    #     user_has_room.user = users[0]
    #     rooms[0].first_owner_id = users[0].id
    #     user_has_room.room = rooms[0]
    #     db.session.add(user_has_room)
    #     user_has_room = User_Has_Room(status=0)
    #     user_has_room.user = users[1]
    #     rooms[0].second_owner_id = users[1].id
    #     user_has_room.room = rooms[0]
    #     db.session.add(user_has_room)
    #
    #     # u0,u2->private room 1
    #     message = Message(
    #         sender_id=users[0].id,
    #         body=fake.sentence(),
    #         timestamp=fake.date_time_between('-30d', '-2d'),
    #         persuasive=0, room_id=rooms[1].id
    #     )
    #     db.session.add(message)
    #     message = Message(
    #         sender_id=users[2].id,
    #         body=fake.sentence(),
    #         timestamp=fake.date_time_between('-30d', '-2d'),
    #         persuasive=0, room_id=rooms[1].id
    #     )
    #     db.session.add(message)
    #     rooms[1].owner=''
    #     rooms[1].room_type = 1
    #     user_has_room = User_Has_Room(status=0)
    #     user_has_room.user = users[0]
    #     rooms[1].first_owner_id = users[0].id
    #     user_has_room.room = rooms[1]
    #     db.session.add(user_has_room)
    #     user_has_room = User_Has_Room(status=0)
    #     user_has_room.user = users[2]
    #     rooms[1].second_owner_id = users[2].id
    #     user_has_room.room = rooms[1]
    #     db.session.add(user_has_room)
    #
    #     # u1,u2->private room 3
    #     message = Message(
    #         sender_id=users[1].id,
    #         body=fake.sentence(),
    #         timestamp=fake.date_time_between('-30d', '-2d'),
    #         persuasive=0, room_id=rooms[3].id
    #     )
    #     db.session.add(message)
    #     message = Message(
    #         sender_id=users[2].id,
    #         body=fake.sentence(),
    #         timestamp=fake.date_time_between('-30d', '-2d'),
    #         persuasive=0, room_id=rooms[3].id
    #     )
    #     db.session.add(message)
    #     rooms[3].owner=''
    #     rooms[3].room_type=1
    #     user_has_room = User_Has_Room(status=1)
    #     user_has_room.user = users[1]
    #     rooms[3].first_owner_id = users[1].id
    #     user_has_room.room = rooms[3]
    #     db.session.add(user_has_room)
    #     user_has_room = User_Has_Room(status=1)
    #     user_has_room.user = users[2]
    #     rooms[3].second_owner_id = users[2].id
    #     user_has_room.room = rooms[3]
    #     db.session.add(user_has_room)
    #     db.session.commit()
    #
    #     # u0,u1,u2->group room 2
    #     message = Message(
    #         sender_id=users[0].id,
    #         body=fake.sentence(),
    #         timestamp=fake.date_time_between('-34d', '-32d'),
    #         persuasive=0, room_id=rooms[2].id
    #     )
    #     db.session.add(message)
    #     message = Message(
    #         sender_id=users[1].id,
    #         body=fake.sentence(),
    #         timestamp=fake.date_time_between('-30d', '-2d'),
    #         persuasive=0, room_id=rooms[2].id
    #     )
    #     db.session.add(message)
    #     message = Message(
    #         sender_id=users[2].id,
    #         body=fake.sentence(),
    #         timestamp=fake.date_time_between('-30d', '-2d'),
    #         persuasive=0, room_id=rooms[2].id
    #     )
    #     db.session.add(message)
    #     user_has_room = User_Has_Room(status=1, quit_time=fake.date_time_between('-32d', '-30d'))
    #     user_has_room.user = users[0]
    #     rooms[2].first_owner_id = admin.id
    #     user_has_room.room = rooms[2]
    #     db.session.add(user_has_room)
    #     user_has_room = User_Has_Room(status=1)
    #     user_has_room.user = users[1]
    #     user_has_room.room = rooms[2]
    #     db.session.add(user_has_room)
    #     user_has_room = User_Has_Room(status=1)
    #     user_has_room.user = users[2]
    #     user_has_room.room = rooms[2]
    #     db.session.add(user_has_room)
    #     db.session.commit()
    #     click.echo('Done.')

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
        # admin = User(nickname='user100', email='user100@qq.com')
        # admin.set_password('12345')
        # db.session.add(admin)
        # db.session.commit()

        click.echo('Generating users...')
        users = []
        for i in range(79, 202):
            user = User(nickname='user' + str(i),
                        bio='',
                        github='',
                        website='',
                        email='user' + str(i+1)+'@qq.com'
                        )
            if i==201:
                user.set_password('admin')
            else:
                user.set_password('12345')
            db.session.add(user)
            users.append(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()



        click.echo('Generating rooms...')
        rooms = []
        # click.echo(messages)
        for i in range(79, 201):
            if i in [1,2,3,5,8,9,10,11,12,14,15,18,20,26,27,28,30,32,33,36,39,41,43,46,50,52,57,58,65,66,67,68,69,71,72,73,75,77,78,79,82,83,84,
                     89,90,92,93,94,95,96,97,98,99,101,102,103,104,107,109,110,111,116,117,118,119,120,122,125,126,128,129,130,131,133,137,138,139,
                     143,146,150,151,153,154,155,156,158,159,162,163,166,167,168,169,170,172,174,175,176,186,188,191,194,196,197,198,199,200]:

                room = Room(
                    name='09-01--A-user'+str(i),
                    description='',
                    owner='user201',
                    room_type=0,
                    isShow=1


                )
            else:
                room = Room(
                    name='09-01--B-user'+str(i),
                    description='',
                    owner='user201',
                    room_type=0,
                    isShow=0

                )
            common_user = User.query.filter_by(nickname='user'+str(i)).first()
            admin_user = User.query.filter_by(nickname='user201').first()
            db.session.add(room)
            db.session.commit()
            userhasroom = User_Has_Room( room_id=room.id, status=1, user=common_user, room=room)
            db.session.add(userhasroom)
            userhasroom = User_Has_Room(room_id=room.id, status=1, user=admin_user, room=room)
            db.session.add(userhasroom)
            db.session.commit()
            rooms.append(room)

        click.echo('Done.')

    @app.cli.command()
    @click.option('--message', default=300, help='Quantity of messages, default is 300.')
    def migrateroom(message):

        
        room=Room.query.filter_by(owner='admin').all()
        for r in room:
            user = User.query.filter_by(nickname='admin').first()
            user100 = User.query.filter_by(nickname='user100').first()
            uhr=User_Has_Room.query.filter_by(room_id=r.id, user_id=user.id).first()

            uhr.user_id=user100.id
            uhr.user = user100
            r.owner='user100'
            
            ms=Message.query.filter_by(room_id=r.id).all()
            for m in ms:
                if m.sender_id==user.id:
                    m.sender_id = user100.id
                    m.sender = user100
                    db.session.add(m)
            
            db.session.add(r)
            db.session.add(uhr)
        db.session.commit()
        
        click.echo('Done.')