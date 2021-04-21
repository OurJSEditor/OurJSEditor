# OurJSEditor
This repository is for storing the code which powers [OurJSEditor.com](https://ourjseditor.com).
Feel free to ask any questions or get help in the Discord server (linked from the home page).

## Build Instructions

#### Prerequisites

 - Node and npm
 - Python 3 and `pip` (theoretically, Python 2 will work as well, but is not supported)
 - SQLite (`sqlite3 --version`)

#### Build Instructions
The following instructions are for MacOS or Linux, with notes on changes for Windows.

```sh
# Clone this repository and move into the directory.
# If you don't have git, you can of course download it as a ZIP, extract, and move into the directory
git clone https://github.com/OurJSEditor/OurJSEditor.git
cd OurJSEditor

# `venv` creates a virtual environment for each one of your python projects
# so you don't have package/version conflicts.
# Create a virtual environment inside the OurJSEditor directory.
python3 -m venv OurEnv
# If `python3` doesn't work, try just `python`. Python 3 can be either, depending on your setup
# For Python 2 (not recommended) use `python -m virtualenv OurEnv`

# Activate the virtual environment
# Once it's activated, you should see `(OurEnv)` appended to the front of your terminal prompt.
# **Use `deactivate` at any time to exit the virtual environment.**
source OurEnv/bin/activate
# WINDOWS: OurEnv\Scripts\activate

# Install python requirements into the virtual environment
pip install -r requirements.txt

# The frontend of the website is a relatively separate [Preact](https://github.com/developit/preact) framework
# Install dependencies and build the frontend
npm install
npm run build

# Configuration settings are loaded from the `.env` file.
# There is a basic example of the settings needed for a local server in the `.env.local` file.
# Rename that to `.env` so Django uses it.
cd django_code
cp .env.local .env
# WINDOWS: copy .env.local .env

# Run database migrations.
# Migrations allow Django to know about the state of the SQL database.
# Running them the first time will create and configure a database for you.
python manage.py migrate

# Collect static resources
# Django copies static resources from their respective directories in the project to one central place for serving
python manage.py collectstatic
```

You can now run a server!
Use the following command to start your own version of the server on http://localhost:8000.
```sh
python manage.py runserver
```
Use ctrl+c to stop the server and `deactivate` to exit the virtual environment. To start the server again, re-activate the virtual environment and use `runserver` again.

## Understanding the Code

Django is the web framework that organizes the site. It is divided into apps, where each app is a folder that contains models, views, and templates.
 - A model is a Python class that represents data in the database.
 - A view is a Python function that handles a request and returns a response.
 - A template is an HTML file (which can also include special tags `{% %}` or `{{ }}` to dynamically insert content).

Additionally, the website makes use of Preact (an alternative to React) JSX components (located in the `js` folder). When JSX is compiled (with `npm run build`):
 1. `js/entries` is traversed.
 2. Each entry loads the components it needs from `components`.
 3. Each entry is transformed into a single `.js` which can be loaded as static.

In general, when you make a request, the following steps occur:

 1. After being passed through Apache and WSGI to Django, the url gets matched against a bunch of regular expressions until Django finds a matching view.
    1. The entry point for this is django_code/ourjseditor/urls.py
    2. This then checks all api urls, and then calls the urls.py files in the other apps. 
 2. Once a matching view is found, it is called with the `request` information.
 3. The view then renders a template, and returns it. (API endpoints don't use HTML templates, but return raw JSON text.)
 4. The template can request static content (CSS/JS).
    1. Many pages follow the paradigm of having a template set a JSON string with page information to a global JS variable
    2. The page then loads a JS file (which was compiled from JSX).
    3. This JSX code can then access the global variable and use it to build components for the page.

Notably, the main program page `templates/program/index.html` does not use any Preact/JSX code. `program.js` is handwritten ES5.


## Contributing

This project will only ever be finished with community contributions. As you use the website, please submit issues, either with feature requests, bugs, or even parts of the UI that are ugly or intuitive.

#### Guidelines for PRs
 - Pull Requests are more than welcome.
 - Please address one issue per pull request (so that if there are issues with one fix, it doesn't block merging another one).
 - Please match the code style for the rest of the repository. In brief:
```js
// Good.
function myFunc (a) {
    //4 spaces
}
```
```js
//awful
var my_func =function ( a )
{
	//a tab
}
```
