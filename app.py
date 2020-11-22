import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


#home page
@app.route("/")
@app.route("/index")
def index():
    endangered_birds = list(mongo.db.endangered_birds.find())
    return render_template("index.html", endangered_birds=endangered_birds)


@app.route("/index")
def about_bird():
    endangered_birds = mongo.db.endangered_birds.find_one(
        {"url": request.form.get("url")})

    return render_template("endangared_birds.html", endangered_birds=endangered_birds)


#register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # register the new user 
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for('my_sightings', username=session["user"]))
    return render_template("register.html")


#login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # check if password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        'my_sightings', username=session["user"]))

            else:
                # invalid password 
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")

# my sightings page
@app.route("/my_sightings/<username>",methods=["GET", "POST"])
def my_sightings(username):
        # grab the session user's username from db ENTER NEW VSLUES HERE
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("my_sightings.html", username=username)
    
    return redirect(url_for("login"))

#log out page
@app.route("/logout")
def logout():
    # remove user's ALTERANTIVE cookies session.clear()
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))



    
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)