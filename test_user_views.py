import os
from unittest import TestCase
from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):

    def setup(self):
        db.drop_all()
        db.create_all()

       self.client = app.test_client()

        #create multiple test users
        self.user1 = User.signup("test1", "test1@email.com", "password", None)
        self.user1_id = 1234
        self.user1.id = self.user1_id

        self.user2 = User.signup("test2", "test2@email.com", "password", None)
        self.user2_id = 4321
        self.user2.id = self.user2_id

        self.user3 = User.signup("test3", "test3@email.com", "password", None)
        self.user3_id = 5678
        self.user3.id = self.user3_id

        self.user4 = User.signup("test4", "test4@email.com", "password", None)
        self.user4_id = 8765
        self.user4.id = self.user4_id

        db.session.commit()

    def teardown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_user_list(self):
        with self.client as c:
            resp = c.get("/users")
        #assertIn is used to test if option 1 is in option 2
        #this is testing to see if these users are within the response data(to see if they show up)
        #"str" makes sure to turn the data into a string
            self.assertIn("@test1", str(resp.data))
            self.assertIn("@test2", str(resp.data))
            self.assertIn("@test3", str(resp.data))
            self.assertIn("@test4", str(resp.data))

    def test_search1(self):
        with self.client as c:
            resp = c.get("users?q=test")
            self.assertIn("@test1", str(resp.data))
            self.assertIn("@test2", str(resp.data))
            self.assertIn("@test3", str(resp.data))
            self.assertIn("@test4", str(resp.data))

    def test_search2(self):
        with self.client as c:
            resp = c.get("users?q=test1")
            self.assertIn("@test1", str(resp.data))

            self.assertNotIn("@test2", str(resp.data))
            self.assertNotIn("@test3", str(resp.data))
            self.assertNotIn("@test4", str(resp.data))

    def test_user_page(self):
        #make sure the user specific page responds with that user's info
        with self.client as c:
            resp = c.get(f"users/{self.test1_id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test1", str(resp.data))

   def setup_followers(self):
    """Add followers to test a couple follow functions """
        f1 = Follows(user_being_followed_id=self.user1_id, user_following_id=self.user2_id)
        f2 = Follows(user_being_followed_id=self.user3_id, user_following_id=self.user2_id)
        f3 = Follows(user_being_followed_id=self.user2_id, user_following_id=self.user1_id)

        db.session.add_all([f1,f2,f3])
        db.session.commit()

    def test_following_display(self):
        self.setup_followers()
        with self.client as c:
            resp = c.get(f"/users/{self.user2}/following")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test1", str(resp.data))
            self.assertIn("@test3", str(resp.data))
            self.assertNotIn("@test4", str(resp.data))

    def test_followers_display(self):
        self.setup_followers()
        with self.client as c:
            resp = c.get(f"/users/{self.user2}/followers")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test1", str(resp.data))
            self.assertNotIN("@test4", str(resp.data))        

    def test_like_post(self):
        #create message to test like
        newMessage = Message(id=21894, text="Hello World!", user_id = self.user1_id)
        db.session.add(newMessage)
        db.commit()

        with self.client as c:
            resp = c.post("/messages/21894/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            #filter to make sure to get the message id that needs to be used
            likes = Likes.query.filter(Likes.message_id==21894).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.user1_id)



    
