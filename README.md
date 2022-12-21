# Travel Cockpit 2.0
#### Full Stack Web Developer CAPSTONE PROJECT
To finally be able to deploy my own web app, I took this Nanondegree. Based on my CS50 final project Flask app 'Travel Cockpit', I have rebuild the entire app to finally deploy it for desktop and mobile usage. As well added a travel suggestion blog functionality to share our personal 'travel secrets' (CRUD app).

## URL
https://travelcockpit.ddnss.ch/

## Purpose
As passionate travelers my wife and me were continuously looking for a central
Travel Cockpit to get all essential information necessary to plan a trip in one
tool or view. To avoid the tedious googling for each source and forgetting
always at least one important info.
Then especially in COVID-19 times it was waste of time to prepare long time
planned trips.
As nothing similar is existing, I have developed a Travel Cockpit, which makes
a spontaneous trip planning easy and efficient.

## Concept
User can search for his desired travel destination or get a suggestion of currently
warm places on the planet. The destination can be a country (German/English), city (English) or for a good
luck search any place/region.
To get inspired for new, but less mainstream targets, the user can browse the 'Travel Secrets'. The blog is managed by 2 roles: Manager (can create/edit/delete own secrets), Director (all rights).
Based on the user's search a desktop consisting of tailored widgets and direct link buttons appear. As the main target is to inform the user with all essential travel information in one view or one direct click away.

This Web (HTML) based dashboard, which works on a Smart TV, Desktop and mobile
device focuses the European and especially German traveler. Therefore the dashboard
search function works in German and English with language specific travel links.

### Functionality
- Auth0 user authentication
- Gunicorn WSGI
- Flask API/web server
- HTML/CSS frontend
- Postgres SQL database
- Custom Python functions.


## Frontend
- HTML pages with Bootstrap powered styling and own customization in CSS
- Conditional logic for a smart and flexible HTML to adapt on existing content
with Jinja
- Icons from Font Awesome
- Background pictures from private picture collection

## Data input

With thankful acknowledgement for the public free provided data:
- Weather by openweathermap.org
- FX-rates by exchangesrateapi
- Main infos by World Bank
- COVID19 data by covid19api
- National holidays by https://date.nager.at/Api/v2/NextPublicHolidays


## Backend

### Installing Dependencies

#### Python 3.9.0

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)
Buildpack for Heroku deployment is included with file 'runtime.txt'

#### Virtual Enviornment

I recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the work directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

#### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.
- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the Postgres database.

#### Environment variables
(Git Bash terminal)

All necessary secret keys, AUTH0 variables and JWT are stored in setup.sh. The file is added in the project commit comments and for confidentiality not uploaded to Git Hub.

```bash
source setup.sh
```

#### Running the server

From within your work directory first ensure you are working using your created virtual environment and run flask server, which is running on debug mode:

```bash
python app.py
```

#### Setup your own Auth0 3rd party authentification

1. Create a new Auth0 Account
2. Select a unique tenant domain
3. Create a new, regular web application
4. Create a new API
    - in API Settings:
        - Enable RBAC
        - Enable Add Permissions in the Access Token
5. Create new API permissions (Permission, Description):
    - `get:history-all`, Read user history of all users
    - `delete:master`, Delete selected blog post of any Manager
    - `patch:master`, Edit selected blog of any Manager
    - `delete:own`, Delete own blog post
    - `patch:own`, Edit own blog post
    - `post:blog` Post new blog post
    - `get:blog`, Read all bog posts

6. Create new roles for:
    - Manager
        - can perform all actions, except: `patch:master`, `delete:master`
    - Director
        - can perform all actions

## Testing with unittest

### Database setup for testing

#### Setup Postgres database:
```
dropdb travel_cockpit_test
createdb travel_cockpit_test
```
Windows (Git Bash terminal):
Login to Postgres first
```
psql -U postgres
```
Create new database
```
drop database travel_cockpit_test
create database travel_cockpit_test
```
The first time you run the tests, omit the dropdb command.

With Postgres running and created test database, restore a database using the 'database/210308_travel_cockpit.sql.backup' file provided. From the main work folder in terminal run:
```bash
pg_restore -U postgres --dbname=travel_cockpit_test --verbose database/travel_cockpit_test.sql
```
### Run tests

Run command in work directory (42 tests)
```
python test_app.py
```
All tests are kept in that file and should be maintained as updates are made to app functionality.


## API Reference

### Base URL
Local: http://localhost:5000/
Hosted: https://travelcockpit.herokuapp.com/

### Authentication with Auth0
Set up of Authetication defined in chapter 'Installing Dependencies'

### Errors

App error handler returns HTTP status codes and json objects in following format:

{
    "success": False,
    "error": 400,
    "message": "bad request"
}

#### Client errors
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden access
- 404: Resource NOT found
- 405: Method NOT allowed
- 422: Unprocessable
- 500: Internal database error

### Resource endpoint library (w/o login/logout endpoints)

Pages are directly html rendered with attached data (e.g. render_template("history.html", rows=history). JSON objects are only returned where necessary or efficient in combination with frontend (patch, delete). Returning JSON objects would make a diffrent frontend necessary, or would need a if/else condition to split between a pure JSON API requests or html frontend rendering, only to enable an API function without frontend.

#### GET /vision
- Render html template "vision.html"

#### GET /contact
- Render html template "contact.html"

#### GET /home
- Requires authentication (RBAC not required)
- Render html template "home.html" with data: go_warm (link address)

#### POST /home
- Requires authentication (RBAC not required), e.g. (headers={'Authorization': 'Bearer '+token})
- Requests "destination" from html form, e.g. (data={"destination: "Spain"})
- Render template "my_dashboard.html" with data: switch, loc_classes, links_dic, info, options, covid, holidays

#### GET /history
- Requires authentication (RBAC not required), e.g. (headers={'Authorization': 'Bearer '+token})
- Render template "history.html" with data: rows (search history)

#### GET /history-all
- Requires authentication with RBAC premission ('get:history-all'), e.g. (headers={'Authorization': 'Bearer '+token})
- Render template "history_all.html" with data: data (search history of all users)

### Resource endpoint library - CRUD app

#### GET /blog/user
- Requires authentication (RBAC not required), e.g. (headers={'Authorization': 'Bearer '+token})
- Render template "blog_user.html" with data: blogs, userinfo

#### GET /blog
- Requires authentication with RBAC premission ('get:blog'), e.g. (headers={'Authorization': 'Bearer '+token})
- Render template "blog.html" with data: blogs, userinfo, permi, id

#### GET /blog/create
- Requires authentication with RBAC premission ('post:blog'), e.g. (headers={'Authorization': 'Bearer '+token})
- Render template "blog_create.html" to create form

#### POST /blog/create
- Requires authentication with RBAC premission ('post:blog'), e.g. (headers={'Authorization': 'Bearer '+token})
- Get user input data from html form or e.g.:
                            data={
                                "title": "Valpolicella",
                                "why1": "Amarone",
                                "why2": "Superb food",
                                "why3": "Lake Garda",
                                "text": "Wine, food, lake & mountains!",
                                "link": "Verona"
                            })
 - flash message "Blog was successfully added!"
 - Redirect to "/blog"

#### GET /blog/<int:id>/edit
- Requires authentication with RBAC premission ('patch:master'), e.g. (headers={'Authorization': 'Bearer '+token})
- Role: Director
- Example path for test database: /blog/69/edit
- Render template "blog_edit.html" with data: blog (excisitng blog data of selected id)

#### POST /blog/<int:id>/edit
- Requires authentication with RBAC premission ('patch:master'), e.g. (headers={'Authorization': 'Bearer '+token})
- Role: Director
- Example path for test database: /blog/69/edit
- Get user input data from html form or e.g.:
                            data={
                                "title": "Valpolicella",
                                "why1": "Amarone",
                                "why2": "Superb food",
                                "why3": "Lake Garda",
                                "text": "Wine, food, lake & mountains!",
                                "link": "Verona"
                            })
- return JSON object: {'success': True}

#### GET /blog/<int:id>/edit-own
- Requires authentication with RBAC premission ('patch:own'), e.g. (headers={'Authorization': 'Bearer '+token})
- Role: Manager
- Example path for test database: /blog/70/edit-own
- Render template "blog_edit_own.html" with data: blog (excisitng blog data of selected id)

#### POST /blog/<int:id>/edit-own
- Requires authentication with RBAC premission ('patch:own'), e.g. (headers={'Authorization': 'Bearer '+token})
- Role: Manager
- Manager can only update own created blogs with his user_id
- Example path for test database: /blog/70/edit-own
- Get user input data from html form or e.g.:
                            data={
                                "title": "Valpolicella",
                                "why1": "Amarone",
                                "why2": "Superb food",
                                "why3": "Lake Garda",
                                "text": "Wine, food, lake & mountains!",
                                "link": "Verona"
                            })
- return JSON object: {'success': True}

#### DELETE /blog/<int:id>/delete
- Requires authentication with RBAC premission ('delete:master'), e.g. (headers={'Authorization': 'Bearer '+token})
- Role: Director
- Delete in frontend by click event
- Example path for test database: /blog/85/delete
- return JSON object: {'success': True}

`curl -X DELETE http://localhost:5000/blog/85/delete`
```
{
  "success": true
}
```

#### DELETE /blog/<int:id>/delete-own
- Requires authentication with RBAC premission ('delete:own'), e.g. (headers={'Authorization': 'Bearer '+token})
- Role: Manager
- Delete in frontend by click event, only available if blog has been created with his own user_id
- Example path for test database: /blog/86/delete-own
- return JSON object: {'success': True}

`curl -X DELETE http://localhost:5000/blog/86/delete-own`
```
{
  "success": true
}
```


## Hosting 

Hostig on own Linux server...

### If you encounter any errors, trying checking the following:

- sudo less /var/log/nginx/error.log: checks the Nginx error logs.
- sudo less /var/log/nginx/access.log: checks the Nginx access logs.
- sudo journalctl -u nginx: checks the Nginx process logs.
- sudo journalctl -u travelcockpit: checks your Flask app’s Gunicorn logs.


## Authors
Christian Johann Bayerle
Based on the Udacity Nanodegree 'Full Stack Web Development'

## Acknowledgements
Thanks to Udacity
 
 
Concept & Copyrights by Christian Johann Bayerle
