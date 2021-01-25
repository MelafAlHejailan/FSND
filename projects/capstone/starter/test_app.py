import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from auth import AuthError, requires_auth
from models import setup_db, Actors, Movies


Executive_jwt = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ijl6elZkMGZhUEZYWVdLek5iYmNOSSJ9.eyJpc3MiOiJodHRwczovL2ZzbmQtYmF5YW4udXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVmNGFlNTdjZTllZjVmMDA2N2I1YWRmNiIsImF1ZCI6ImNhcHN0b25lIiwiaWF0IjoxNTk4NzQ0MDE3LCJleHAiOjE1OTg3NTEyMTcsImF6cCI6IlhJVnVhRWNRRDhTckxCUjZtczZqZGdBcVQ4Mk1zSldFIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3JzIiwiZGVsZXRlOm1vdmllcyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiLCJwb3N0Om1vdmllcyJdfQ.S9e35aXVF9C0I-WP_BC852dUGLrIBKY8ppcyBeaFasV7CYEybkyh4GrQDNR87AO-PtG1yi11GqybVcTAVspT29lMosGITSuRc1wnYiDj7GEY47KKG28myX00coqFucTFwcrqFVX3tIKBcMHaGkDrMg5Zz3QijTNdPPF7clMthOE0ItNxZSY-vb9-SMfgWGJjuDvi0fJVYHz7YXU5mrFQLHtGiVawQ5JKrYq8xbTe35AqwzERMpug2EstILxDQsVBBSxWmIPlA82saavEJJ-i908NdObEBUPbZydXdUbLJ96AsTS6OwpdvDqXK-QY-kMLKGYpOwY6H6XE797JJ5taZQ'}

Director_jwt = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ijl6elZkMGZhUEZYWVdLek5iYmNOSSJ9.eyJpc3MiOiJodHRwczovL2ZzbmQtYmF5YW4udXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVmNGFlNGIzMjA3NmE3MDA2NzhlZTM0NyIsImF1ZCI6ImNhcHN0b25lIiwiaWF0IjoxNTk4NzQzODM0LCJleHAiOjE1OTg3NTEwMzQsImF6cCI6IlhJVnVhRWNRRDhTckxCUjZtczZqZGdBcVQ4Mk1zSldFIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3JzIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiLCJwYXRjaDphY3RvcnMiLCJwYXRjaDptb3ZpZXMiLCJwb3N0OmFjdG9ycyJdfQ.n9CyoZnfDJkUawMc3hr-opqLHU3Aawki30gSkhZ4NmGw4WIXoK3uV8lfbSedUy0nK7_pQLHZ2GJwpLvk7oWeDKf83TQNoG5bQ_Vkpbs1_bj-dz9lSsCRGg9j4CRfp9P3nL93kQV0zyUvXRkpWGmSXQRCSs9QWuQ-5bc1wgCYUoa5IlggtQKscgKHZiFxtE_qtQT7LfBoEpchzOLk6NdBujLZErfKETNLGJ9dqzxklEiamxJXM9eXnXaxcPB0ESOw1mrsmVFd-HNCEUKJ65PcvW0XZJRTIWjbNGjztit5kfMVMrqvh7zWz_7DRbvZxtkaBHINe_ojqsqDGk20KN3Z_w'}

Assistant_jwt = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ijl6elZkMGZhUEZYWVdLek5iYmNOSSJ9.eyJpc3MiOiJodHRwczovL2ZzbmQtYmF5YW4udXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDVmNGFlNjVmYzY0NzhiMDA2N2Q4NmU4YiIsImF1ZCI6ImNhcHN0b25lIiwiaWF0IjoxNTk4NzQ0MjI2LCJleHAiOjE1OTg3NTE0MjYsImF6cCI6IlhJVnVhRWNRRDhTckxCUjZtczZqZGdBcVQ4Mk1zSldFIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyJdfQ.EeBOgN4rVzEjmzzliaTBdsBjvd9KI453HDWOtgdPg0ukHXo-43KX9Bw8sMIMd6auEs0paVI8sBwsk8Nmti6EQ15-Jkgr_Gsnzu6LyyG-Solc-lgdybU99FZoxiHa-dBkUr_MeOBSfiQNPq4kwBvFHiuMEAATMD3F1NyTdNs9P49RmkKbSxv1DbgJDoDdUX9JAqwPrRW9XOj_7FzqSySv58wDW5pL0LQVxkyEkrlGG73A9JN38GKfiJJJEXovl3_ccSkd1vKcnc_NfHSlhHMwumI1blrWNCDSGFEGeZ9H13JgAzwZNE-qrkp4qpXdauVvN5gXj7DRxWP0yixCz14B4Q'}

class CapstoneTestCase(unittest.TestCase):
    """This class represents the Capstone test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "capstone_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', '123', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

# Test for each test for successful operation and for expected errors.

# Get test 

    def test_unauthorized_get_actors(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['code'], 'authorization_header_missing')

        
    # test to get all actors by Assistant role
    def test_get_actors(self):
        res = self.client().get('/actors', headers=Assistant_jwt)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['actors'])

    def test_unauthorized_get_movies(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['code'], 'authorization_header_missing')

    def test_get_movies(self):
        res = self.client().get('/movies', headers=Assistant_jwt)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['movies'])

# Post set 


# Actors

def test_unauthorized_post_actors(self):

        num_before = len(Actor.query.all())

        res = self.client().post('/actors', json={
                                        'name': 'new name',
                                        'age': '20',
                                        'gender': 'female',
                                        'movie_id': 1
                                    })

        data = json.loads(res.data)
        num_after = len(Actor.query.all())

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['code'], 'authorization_header_missing')
        self.assertEqual(num_before, num_after)


    def test_post_actors(self):

        num_before = len(Actor.query.all())

        res = self.client().post('/actors', headers=Director_jwt,
                                    json={
                                        'name': 'new name',
                                        'age': '20',
                                        'gender': 'female',
                                        'movie_id': 2
                                    })

        data = json.loads(res.data)

        num_after = len(Actor.query.all())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(num_before+1 , num_after)
        
    def test_failed_post_actors(self):

        num_before = len(Actor.query.all())

        res = self.client().post('/actors', headers=Executive_jwt)
        data = json.loads(res.data)
        num_after = len(Actor.query.all())

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(num_before, num_after)

# Movies 

    def test_unauthorized_post_movies(self):

        num_before = len(Movie.query.all())

        res = self.client().post('/movies', json={
                                        'title': 'new movie',
                                        'release_date': '2019-03-07',
                                    })
        data = json.loads(res.data)
        num_after = len(Movie.query.all())

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['code'], 'authorization_header_missing')
        self.assertEqual(num_before, num_after)

    def test_post_movies_by_Assistant(self):

        num_before = len(Movie.query.all())

        res = self.client().post('/movies', headers=Assistant_jwt,
                                    json={
                                        'title': 'new movie by Assistant',
                                        'release_date': '2016-08-01',
                                    })
        data = json.loads(res.data)
        num_after = len(Movie.query.all())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(num_before , num_after)


    def test_post_movies(self):

        num_before = len(Movie.query.all())

        res = self.client().post('/movies', headers=Executive_jwt,
                                    json={
                                        'title': 'new movie',
                                        'release_date': '2019-03-07',
                                    })
        data = json.loads(res.data)

        num_after = len(Movie.query.all())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(num_before+1 , num_after)


    def test_failed_post_movies(self):

        num_before = len(Movie.query.all())

        res = self.client().post('/movies', headers=Executive_jwt)
        data = json.loads(res.data)
        num_after = len(Movie.query.all())

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(num_before, num_after)

# Patch Test

# Actors 

def test_unauthorised_patch_actors(self):
        res = self.client().patch('/actors/2', json={
            'name': 'unauthorised modified name'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['code'], 'authorization_header_missing')

    def test_patch_actors(self):
        res = self.client().patch('/actors/2', headers=Executive_jwt, json={
            'name': 'modified name'
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['actors'])

    def test_empty_patch_actors(self):

        res = self.client().patch('/actors/2', headers=Executive_jwt)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_failed_patch_actors(self):

        res = self.client().patch('/actors/7', headers=Executive_jwt, json={
            'name': 'failed modified name'
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

# Movie 

    def test_unauthorised_patch_movies(self):
        res = self.client().patch('/movies/3', json={
            'title': 'unauthorised modified title'
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['code'], 'authorization_header_missing')

    def test_patch_movies(self):
        res = self.client().patch('/movies/3', headers=Director_jwt, json={
            'title': 'modified title'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['movies'])

    def test_empty_patch_movies(self):
        res = self.client().patch('/movies/3', headers=Director_jwt)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_failed_patch_movies(self):
        res = self.client().patch('/movies/6', headers=Director_jwt, json={
            'title': 'failed modified title'
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

# Delete Test 

# Actors

    def test_unauthorised_delete_actors(self):
        res = self.client().delete('/actors/3')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['code'], 'authorization_header_missing')

    def test_delete_actors(self):
        num_before = len(Actor.query.all())
        res = self.client().delete('/actors/3', headers=Director_jwt)
        data = json.loads(res.data)
        num_after = len(Actor.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('delete', data)
        self.assertEqual(num_before-1, num_after)

    def test_failed_delete_actors(self):
        num_before = len(Actor.query.all())
        res = self.client().delete('/actors/6', headers=Executive_jwt)
        data = json.loads(res.data)
        num_after = len(Actor.query.all())

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(num_before, num_after)

# Movies

    def test_unauthorised_delete_movies(self):
        res = self.client().delete('/movies/1')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['code'], 'authorization_header_missing')

    def test_delete_movies_by_Director(self):
        num_before = len(Movie.query.all())
        res = self.client().delete('/movies/1', headers=Director_jwt)
        data = json.loads(res.data)
        num_after = len(Movie.query.all())

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(num_before, num_after)

    def test_delete_movies(self):
        num_before = len(Movie.query.all())
        res = self.client().delete('/movies/1', headers=Executive_jwt)
        data = json.loads(res.data)
        num_after = len(Movie.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('delete', data)
        self.assertEqual(num_before-1, num_after)

    def test_failed_delete_movies(self):
        num_before = len(Movie.query.all())
        res = self.client().delete('/movies/6', headers=Executive_jwt)
        data = json.loads(res.data)
        num_after = len(Movie.query.all())

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(num_before, num_after)


        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()