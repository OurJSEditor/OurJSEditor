# OurJSEditor
This repository is for storing the server-side code which powers [OurJSEditor.com](https://ourjseditor.com).

### Local Setup
***Note: This is to get a full database and Django setup working.***
***If you want to work on the editor itself, it's over [here](https://github.com/OurJSEditor/jstinker).***
***If you are only tweaking JS/CSS or fixing a small python bug you probably don't need a whole server to test it.***

This code is written to run on a server, so there's some setup involved to make it run locally. It's still easier than trying to install the full dependencies for the server, however.

The following instructions have been tested on MacOS, but should translate well to Linux by swapping `brew` with `apt-get`.
Windows setup should be roughly similar, but will probably require some Googling.
1. Clone this repository. `git clone https://github.com/OurJSEditor/OurJSEditor.git`
2. Move into the new directory, `cd OurJSEditor`. That's pretty straightforward, I hope.
3. Make sure you have python installed. `python -V` will tell you your version. This code was written for python 2.7.12.
4. Make sure you have `pip`, python's package manager, installed. It comes with python versions greater than 2.7.9 (released 2014), so should have it. If you don't, https://lmgtfy.com?q=Installing+pip.
5. `virtualenv` creates a virtual environment for each one of your python projects you don't have conflicts. Run `pip install virtualenv`.
6. Inside the OurJSEditor directory, create a virtual environment with `virtualenv OurEnv`. The name doesn't really matter, but OurEnv is ignored in `.gitignore` for you.
7. Activate the virtual environment with `source OurEnv/bin/activate`. Once it's activated, you should see `(OurEnv)` appended to the front of your terminal prompt. **Use `deactivate` at any time to exit the virtual environment.**
8. Now, installing requirements. Running `pip install -r requirements.txt` install the correct versions of a list of python requirements.
9. Now, you need a database. The server uses mySQL, but it's far easier to set up `sqlite3` for local development. On Mac, with homebrew installed, `brew install sqlite3`. You'll have to look into doing it on other operating systems. Once it's installed, `sqlite3 -version` from the command line should print the version.
10. Move forward into `django_code`, `cd django_code`.
11. There are a few settings that need to be changed, that are loaded from the `.env` file. There is a basic example of the settings needed for a local server in the `.env.local` file. Rename that to `.env` so Django can find it:
```
cp .env.local .env
```
12. Run database migrations. `python manage.py migrate`
13. Start up a server! `python manage.py runserver`. You should now see you own copy of the website at http://localhost:8000, complete with the ability to create and edit users and stuff! You can stop following these instructions now.

After following these instructions, you can use ctrl+C to stop the server and `deactivate` to exit the virtual environment.
Then, to start the server again, re-activate the virtual environment and use `python manage.py runserver`.
