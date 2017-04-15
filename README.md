# OurJSEditor
This repository is for storing the server-side code which powers [OurJSEditor.com](http://ourjseditor.com).

### Local Setup
***Note: This is to get a full database and django setup working.***
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
6. Inside the OurJSEditor directory, create a virtual environment with `virtualenv NAME_HERE`. I'll leave naming it up to you, but it doesn't really matter.
7. Activate the virtual environment with `source NAME_HERE/bin/activate`. Once it's activated, you should see `(NAME_HERE)` appended to the front of your terminal propmt. Use `deactivate` at any time to exit the virtual environment. 
8. Now, installing Django. `pip install Django`. 
9. Now, you need a database. The server uses mySQL, but it's far easier to set up `sqlite3` for local development. On Mac, with homebrew installed, `brew install sqlite3`. You'll have to look into doing it on other operating systems. Once it's installed, `sqlite3 -version` from the command line should print the version.
10. Point Django at the new database by replacing the [`DATABASE` config](https://github.com/OurJSEditor/OurJSEditor/blob/0768f0126042193b6aa1e51605c74cc49c2850dc/django_code/ourjseditor/settings.py#L90) with:
```py
'default': {
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    'ENGINE': 'django.db.backends.sqlite3',
}
```
11. Remove or comment out the code that grabs the mySQL password, [here](https://github.com/OurJSEditor/OurJSEditor/blob/0768f0126042193b6aa1e51605c74cc49c2850dc/django_code/ourjseditor/settings.py#L86), or it will error. You could also give it a database_password.txt, but this seems easier.
12. Create a secret key. This is a random string of charectors, and unless you plan on actually hosting a server isn't importand to keep secret. The following will work.
```sh
echo "(0(ymvwi+b!qckrk&_i2fmnqr5#v938-#b6srb)8%b16^@!*a7" > ourjseditor/secret_key.txt
```
13. Run database migrations. `python manage.py runmigrations`
14. Start up a server! `python manage.py runserver`. You should now see you own copy of the website at http://localhost:8000, complete with the ability to create and edit users and stuff! You can stop following these instuctions now.
