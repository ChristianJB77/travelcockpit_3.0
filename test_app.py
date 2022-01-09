import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import session
import auth.constants as constants

from app import create_app
from database.models import setup_db, db, Month, User, UserHistory, Secret

# Travel Cockpit endpoints test class


class TravelCockpitTestCase(unittest.TestCase):

    def setUp(self):
        # Auth0 JWTs: User, Manager, Director
        self.test_user = os.environ['JWT_USER']
        self.test_manager = os.environ['JWT_MANAGER']
        self.test_director = os.environ['JWT_DIRECTOR']
        # Define test variable and initialize app
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "travel_cockpit_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            'postgres', 'secret', 'localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)
        # Binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        pass

    """Endpoint testing (without login/logout)"""

    def test_start_page(self):
        res = self.client().get('/')
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('https://www.reise-klima.de/urlaub/', str(data))

    def test_404_start_page(self):
        res = self.client().get('/_')

        self.assertEqual(res.status_code, 404)

    def test_vision(self):
        res = self.client().get('/vision')
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('Vision', str(data))

    def test_404_vision(self):
        res = self.client().get('/vision_')

        self.assertEqual(res.status_code, 404)

    def test_contact(self):
        res = self.client().get('/contact')
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('Contact', str(data))

    def test_404_contact(self):
        res = self.client().get('/contact_')

        self.assertEqual(res.status_code, 404)

    """Requires AUTH0, w/o RBAC -> every user"""

    def test_get_home(self):
        res = self.client().get(
                            '/home',
                            headers={'Authorization': 'Bearer '+self.test_user}
                                )
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('https://www.reise-klima.de/urlaub/', str(data))

    def test_401_get_home(self):
        res = self.client().get('/home', headers={'Authorization': 'Bearer '})
        data = res.data

        self.assertEqual(res.status_code, 401)
        self.assertNotIn('https://www.reise-klima.de/urlaub/', str(data))

    def test_post_home(self):
        res = self.client().post(
                        '/home',
                        headers={'Authorization': 'Bearer '+self.test_user},
                        data={"destination": "Spain"}
                                )
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('spain', str(data))

    # Invalid header
    def test__401_post_home(self):
        res = self.client().post('/home', headers={'Authorization': 'Bearer '},
                                 data={"destination": "Spain"})
        data = res.data

        self.assertEqual(res.status_code, 401)
        self.assertNotIn('spain', str(data))

    def test_get_history(self):
        res = self.client().get(
                            '/history',
                            headers={'Authorization': 'Bearer '+self.test_user}
                                )
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('Spain', str(data))

    # Invalid header
    def test_401_get_history(self):
        res = self.client().get(
                                '/history',
                                headers={'Authorization': 'Bearer '}
                                )
        data = res.data

        self.assertEqual(res.status_code, 401)
        self.assertNotIn('Spain', str(data))

    # Manager
    def test_get_history_all(self):
        res = self.client().get(
                        '/history-all',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                )
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('Germany', str(data))

    # Director
    def test_get_history_all(self):
        res = self.client().get(
                        '/history-all',
                        headers={'Authorization': 'Bearer '+self.test_director}
                                )
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('Germany', str(data))

    # Unauthorized
    def test_403_get_history_all(self):
        res = self.client().get(
                            '/history-all',
                            headers={'Authorization': 'Bearer '+self.test_user}
                                )
        data = res.data

        self.assertEqual(res.status_code, 403)
        self.assertNotIn('Secret', str(data))

    """CRUD API endpoint testing (Secret Model)"""

    # CREATE
    # Before POST, test get form html page
    def test_create_blog(self):
        res = self.client().get(
                        '/blog/create',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                )

        self.assertEqual(res.status_code, 200)

    def test_404_create_blog(self):
        res = self.client().get(
                        '/blog/create/1',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                )

        self.assertEqual(res.status_code, 404)

    # Unauthorized
    def test_403_create_blog(self):
        res = self.client().get(
                            '/blog/create',
                            headers={'Authorization': 'Bearer '+self.test_user}
                                )

        self.assertEqual(res.status_code, 403)

    def test_create_blog_manager(self):
        res = self.client().post(
                        '/blog/create',
                        headers={'Authorization': 'Bearer '+self.test_manager},
                        data={
                                "title": "Valpolicella",
                                "why1": "Amarone",
                                "why2": "Superb food",
                                "why3": "Lake Garda",
                                "text": "Wine, food, lake & mountains!",
                                "link": "Verona"
                            })

        self.assertEqual(res.status_code, 302)

    # Unauthorized
    def test_403_create_blog(self):
        res = self.client().post(
                        '/blog/create',
                        headers={'Authorization': 'Bearer '+self.test_user},
                        data={
                                "title": "Valpolicella",
                                "why1": "Amarone",
                                "why2": "Superb food",
                                "why3": "Lake Garda",
                                "text": "Wine, food, lake & mountains!",
                                "link": "Verona"
                            })

        self.assertEqual(res.status_code, 403)

    def test_404_create_blog_manager(self):
        res = self.client().post(
                        '/blog/create/1',
                        headers={'Authorization': 'Bearer '+self.test_manager},
                        data={
                                "title": "Valpolicella",
                                "why1": "Amarone",
                                "why2": "Superb food",
                                "why3": "Lake Garda",
                                "text": "Wine, food, lake & mountains!",
                                "link": "Verona"
                            })

        self.assertEqual(res.status_code, 404)

    def test_create_blog_director(self):
        res = self.client().post(
                    '/blog/create',
                    headers={'Authorization': 'Bearer '+self.test_director},
                    data={
                            "title": "Parma",
                            "why1": "Parmegiano",
                            "text": "Cheeeeeeeese",
                            "link": "Parma"
                        })

        self.assertEqual(res.status_code, 302)

    # READ
    # User
    def test_get_blog_user(self):
        res = self.client().get(
                        '/blog/user',
                        headers={'Authorization': 'Bearer '+self.test_user}
                                )
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('Valpolicella', str(data))

    def test_401_get_blog_user(self):
        res = self.client().get(
                                '/blog/user',
                                headers={'Authorization': 'Bearer '}
                                )
        data = res.data

        self.assertEqual(res.status_code, 401)
        self.assertNotIn('Valpolicella', str(data))

    def test_404_get_blog_user(self):
        res = self.client().get(
                            '/blog/user/1',
                            headers={'Authorization': 'Bearer '+self.test_user}
                                )
        data = res.data

        self.assertEqual(res.status_code, 404)
        self.assertNotIn('Valpolicella', str(data))

    def test_get_blog_manager(self):
        res = self.client().get(
                        '/blog',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                )
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('Valpolicella', str(data))

    def test_get_blog_director(self):
        res = self.client().get(
                        '/blog',
                        headers={'Authorization': 'Bearer '+self.test_director}
                                )
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertIn('Valpolicella', str(data))

    # Unauthorized
    def test_403_get_blog(self):
        res = self.client().get(
                            '/blog',
                            headers={'Authorization': 'Bearer '+self.test_user}
                                )
        data = res.data

        self.assertEqual(res.status_code, 403)
        self.assertNotIn('Valpolicella', str(data))

    def test_404_get_blog_manager(self):
        res = self.client().get(
                        '/blog/1',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                )
        data = res.data

        self.assertEqual(res.status_code, 404)
        self.assertNotIn('Valpolicella', str(data))

    # UPDATE
    def test_get_edit_blog_director(self):
        res = self.client().get(
                        '/blog/69/edit',
                        headers={'Authorization': 'Bearer '+self.test_director}
                                )
        data = res.data
        self.assertEqual(res.status_code, 200)
        self.assertIn('Parma', str(data))

    def test_404_get_edit_blog_director(self):
        res = self.client().get(
                        '/blog/68/edit',
                        headers={'Authorization': 'Bearer '+self.test_director}
                                )
        data = res.data
        self.assertEqual(res.status_code, 404)
        self.assertNotIn('Parma', str(data))

    def test_get_edit_blog_manager(self):
        res = self.client().get(
                        '/blog/70/edit-own',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                )
        data = res.data
        self.assertEqual(res.status_code, 200)
        self.assertIn('Valpolicella', str(data))

    def test_404_get_edit_blog_manager(self):
        res = self.client().get(
                        '/blog/68/edit-own',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                )
        data = res.data
        self.assertEqual(res.status_code, 404)
        self.assertNotIn('Valpolicella', str(data))

    def test_403_get_edit_blog_manager(self):
        res = self.client().get(
                        '/blog/69/edit-own',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                )
        data = res.data
        self.assertEqual(res.status_code, 403)
        self.assertNotIn('Valpolicella', str(data))

    def test_patch_edit_blog_director(self):
        res = self.client().patch(
                    '/blog/69/edit/submission',
                    headers={'Authorization': 'Bearer '+self.test_director},
                    json={
                            "title": "Parma",
                            "why1": "Parmegiano",
                            "why2": "Emilia Romagnia",
                            "text": "Home of the best cheese!",
                            "link": "Parma"
                        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_405_patch_edit_blog_director(self):
        res = self.client().patch(
                    '/blog/68/edit/submission',
                    headers={'Authorization': 'Bearer '+self.test_director},
                    json={
                            "title": "Parma",
                            "why1": "Parmegiano",
                            "why2": "Emilia Romagnia",
                            "text": "Home of the best cheese!",
                            "link": "Parma"
                        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    def test_patch_edit_blog_manager(self):
        res = self.client().patch(
                        '/blog/70/edit-own/submission',
                        headers={'Authorization': 'Bearer '+self.test_manager},
                        json={
                                "title": "Valpolicella",
                                "why1": "Amarone wine",
                                "why2": "Superb low priced food",
                                "why3": "Lake Garda",
                                "text": "Wine, food, lake & mountains :)",
                                "link": "Verona"
                            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_405_patch_edit_blog_manager(self):
        res = self.client().patch(
                        '/blog/68/edit-own/submission',
                        headers={'Authorization': 'Bearer '+self.test_manager},
                        json={
                                "title": "Valpolicella",
                                "why1": "Amarone wine",
                                "why2": "Superb low priced food",
                                "why3": "Lake Garda",
                                "text": "Wine, food, lake & mountains :)",
                                "link": "Verona"
                            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    # Test if Manager can patch Director's post -> Should not be possible
    def test_not_own_patch_edit_blog_manager(self):
        res = self.client().patch(
                        '/blog/69/edit-own/submission',
                        headers={'Authorization': 'Bearer '+self.test_manager},
                        json={
                                "title": "Valpolicella",
                                "why1": "Amarone wine",
                                "why2": "Superb low priced food",
                                "why3": "Lake Garda",
                                "text": "Wine, food, lake & mountains :)",
                                "link": "Verona"
                            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    # DELETE
    def test_delete_blog_director(self):
        res = self.client().delete(
                        '/blog/85/delete',
                        headers={'Authorization': 'Bearer '+self.test_director}
                                  )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_delete_blog_director(self):
        res = self.client().delete(
                        '/blog/68/delete',
                        headers={'Authorization': 'Bearer '+self.test_director}
                                  )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    # Unauthorized
    def test_403_delete_blog_manager(self):
        res = self.client().delete(
                        '/blog/69/delete',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                  )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)

    def test_delete_blog_manager(self):
        res = self.client().delete(
                        '/blog/86/delete-own',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                  )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_403_delete_blog_manager(self):
        res = self.client().delete(
                        '/blog/68/delete',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                  )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)

    # Test if Manager can delete Director's blog -> should not be possinle
    def test_not_own_delete_blog_manager(self):
        res = self.client().delete(
                        '/blog/69/delete',
                        headers={'Authorization': 'Bearer '+self.test_manager}
                                  )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
