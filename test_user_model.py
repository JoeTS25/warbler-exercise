"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc 

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user1 = User.signup("test1", "test1@email.com", "password", None)
        userId1 = 1234
        user1.id = userId1

        user2 = User.signup("test2", "test2@email.com", "password", None)
        userId2 = 5678
        user2.id = userId2

        db.session.commit()

        user1 = User.query.get(userId1)
        user2 = User.query.get(userId2)

        self.user1 = user1
        self. userId1 = userId1
        
        self.user2 = user2
        self.userId2 = userId2

        self.client = app.test_client()

    def teardown(self):
        db.session.rollback()    

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

#Test the follow functions
    def test_user_follows(self):
         #adds user 2 to user 1's following
        self.user1.following.append(self.user2) 
        db.session.commit()

        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
        #user1's first following must have the same id as the follower
        self.assertEqual(self.user1.following[0].id, self.user2.id)
        self.assertEqual(self.user2.followers[0].id, self.user1.id)

    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))   

    #Test overall valid signup and invalid individual signup categories

    def test_valid():
        user_test = User.signup("test_user", "testmail@email.com", "password", None)
        userId = 12345
        user_test.id = userId
        db.session.commit()

        user_test = User.query.get(userId)
        #make sure there is a test object
        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.username, "test_user")
        self.assertEqual(user_test.email, "testmail@email.com")
        self.assertNotEqual(user_test.password, "password")
        #we want to make sure our password used doesn't show up the same in our database
        #test to make sure the Bcrypt strings are working
        self.assertTrue(user_test.password.startswith("2b$"))

    def test_invalid_username(self):
        invalid = User.signup(None, "testmail@email.com", "password", None)
        userId = 54321
        invalid.id = userId
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email(self):
        invalid = User.signup("test_user", None, "password", None)
        userId = 51234
        invalid.id = userId
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password(self):
        with self.assertRaises(ValueError) as context:
            #makes sure error is raised if an empty space is entered
            User.signup("test_user", "testmail@email.com", "", None)
            #makes sure error is raised if no password is typed
        with self.assertRaises(ValueError) as context:
            User.signup("test_user", "testmail@email.com", None, None)

    def test_authentication(self):
        user = User.authenticate(self.user1.username, "password")    
        self.assertIsNone(user)
        self.assertEqual(user.Id, self.userId1) 

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("invaliduser", "password")) 

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user1.username, "invalidpassword"))          
            
            
                    