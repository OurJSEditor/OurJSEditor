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
# WINDOWS: OurEnv/Scripts/activate.bat

# Install python requirements into the virtual environment
pip install -r requirements.txt

# Configuration settings are loaded from the `.env` file.
# There is a basic example of the settings needed for a local server in the `.env.local` file.
# Rename that to `.env` so Django uses it.
cd django_code
cp .env.local .env
# WINDOWS: copy .env.local .env

# Run database migrations.
# Migrations allow Django to know about the state of the SQL database.
# Running them the first time will create and configure a database for you.
python django_code/manage.py migrate

# The frontend of the website is a relatively separate [Preact](https://github.com/developit/preact) framework
# Install dependencies and build the frontend
npm install
npm run build

# Or to have webpack watch the JS files and automatically rebuild when they change.
npm run build-watch
```

You can now run a server!
Use the following command to start your own version of the server on http://localhost:8000.
```sh
python manage.py runserver
```
Use ctrl+c to stop the server and `deactivate` to exit the virtual environment. To start the server again, re-activate the virtual environment and use `runserver` again.

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
