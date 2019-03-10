# OurJSEditor
This repository is for storing the server-side code which powers [OurJSEditor.com](https://ourjseditor.com).

### Local Setup
***Note: This is to get a full database and Django setup working.***
***If you want to work on the editor itself, it's over [here](https://github.com/OurJSEditor/jstinker).***
***If you are only tweaking JS/CSS or fixing a small python bug you probably don't need a whole server to test it.***

This code is written to run on a server, so there's some setup involved to make it run locally. It's still easier than trying to install the full dependencies for the server, however.

The following instructions have been tested on MacOS, but should translate well to Linux.
Windows setup should be roughly similar, but will probably require some searching.
1. Clone this repository. `git clone https://github.com/OurJSEditor/OurJSEditor.git`
2. Move into the new directory, `cd OurJSEditor`. That's pretty straightforward, I hope.
3. Make sure you have python 2.7 (& pip) installed (`python -V; pip -V`), and install them if you don't.
4. `virtualenv` creates a virtual environment for each one of your python projects so you don't have conflicts. Run `pip install virtualenv`.
5. Inside the OurJSEditor directory, create a virtual environment with `virtualenv OurEnv`. The name doesn't really matter, but OurEnv is ignored in `.gitignore` for you.
6. Activate the virtual environment with `source OurEnv/bin/activate`. Once it's activated, you should see `(OurEnv)` appended to the front of your terminal prompt. **Use `deactivate` at any time to exit the virtual environment.**
7. Now, installing requirements. Running `pip install -r requirements.txt` install the correct versions of a list of python requirements.
8. Make sure you have sqlite installed (`sqlite3 -version`). The server uses mySQL, but it's far easier to set up `sqlite3` for local development.
9. There are a few settings that need to be changed, that are loaded from the `.env` file. There is a basic example of the settings needed for a local server in the `.env.local` file. Rename that to `.env` so Django can find it:
```
cp django_code/.env.local django_code/.env
```
10. The frontend of the website is a relatively separate [Preact](https://github.com/developit/preact) framework, managed with npm and webpack.
11. Make sure you have node (& npm) installed (`npm -v`), and install them if you don't.
12. Run `npm install` to install JS requirements.
13. Use `npm run build` to build the build the frontend.
14. Run database migrations. `python django_code/manage.py migrate`
15. Start up a server! `python django_code/manage.py runserver`. You should now see you own copy of the website at http://localhost:8000, complete with the ability to create and edit users and stuff! You can stop following these instructions now.

After following these instructions, you can use ctrl+C to stop the server and `deactivate` to exit the virtual environment.
Then, to start the server again, re-activate the virtual environment and use `python django_code/manage.py runserver`.
