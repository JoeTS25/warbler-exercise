import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db create_all()

class MessageModelTestCase(TestCase):
    """Test message model"""
    def setUp(self):
        db. drop_all()
        db.create_all()

        user = User.signup("test1", "testmail@email.com", "password", None)
        self.userid = 1234
        user.id = self.userid
        db.session.commit()

        self.user = User.query.get(self.userid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown
        db.session.rollback()
        return res

    def test_model(self):
        message1 = Message(
            text = "message here",
            user_id = self.userid 
        )

        message2 = Message(
            text = "another message"
            user_id = self.userid
        )

        user = User.signup("test2", "test2@email.com", "password", None)
        userid = 4321
        user.id = userid
        db.session.add_all([message1, message2, user])
        db.session.commit()

        user.likes.append(message1)
        db.session.commit()

        like = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(like), 1)
        self.assertEqual(like[0].message_id, message1.id)


