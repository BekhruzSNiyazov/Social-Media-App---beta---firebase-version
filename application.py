from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from firebase import firebase
from datetime import datetime
import smtplib
import random
import pyrebase

app = Flask(__name__)
app.secret_key = b"_5#y2L'F4Q8z\n\xec]/"
firebase = firebase.FirebaseApplication("https://test-30d03.firebaseio.com/", None)

config = {
	"apiKey": "AIzaSyCcyRivX98VxvhYFTY1AAR0vRPwOM4Tmho",
	"authDomain": "social-media-app-b7343.firebaseapp.com",
	"databaseURL": "https://social-media-app-b7343.firebaseio.com",
	"projectId": "social-media-app-b7343",
	"storageBucket": "social-media-app-b7343.appspot.com",
	"messagingSenderId": "333439697229",
	"appId": "1:333439697229:web:556da6346baaab8ca2b704",
	"measurementId": "G-4XFJ4E6FWH"
}
pyrebase = pyrebase.initialize_app(config=config)
storage = pyrebase.storage()

code = random.randrange(1000, 5000)
login_message = "You need to login or sign up first!"

def all_users():
	if firebase.get("/users", None): return firebase.get("/users", None)
	return []

def all_posts():
	if firebase.get("/posts", None): return firebase.get("/posts", None)
	return []

def all_groups():
	if firebase.get("/groups", None): return firebase.get("/groups", None)
	return []

def all_comments():
	if firebase.get("/comments", None): return firebase.get("/comments", None)
	return []

def get_user(column, value):
	try:
		if column == "_id": return firebase.get("/users/", value)
		if column == "username":
			for _id in all_users():
				if all_users()[_id]["username"] == value: return all_users()[_id]
		if column == "email": 
			for _id in all_users():
				if all_users()[_id]["email"] == value: return all_users()[_id]
		if column =="first":
			for _id in all_users():
				if all_users()[_id]["first"] == value: return all_users()[_id]
		if column == "last": 
			for _id in all_users():
				if all_users()[_id]["last"] == value: return all_users()[_id]
	except: return False

def get_id(username):
	try: 
		for user in all_users():
			if all_users()[user]["username"] == username: return all_users()[user]["_id"]
	except: return False

def get_email(_id):
	try:
		for user in all_users():
			if user["_id"] == _id: return all_users()[user]["email"]
	except: return False

def get_password(_id):
	try:
		for user in all_users():
			if user["_id"] == _id: return all_users()[user]["password"]
	except: return False

def get_first(_id):
	try:
		for user in all_users():
			if user["_id"] == _id: return all_users()[user]["first"]
	except: return False

def get_last(_id):
	try:
		for user in all_users():
			if user["_id"] == _id: return all_users()[user]["last"]
	except: return False

def get_post(column, value):
	try:
		if column == "_id": return firebase.get("/posts/" + value, None)
		if column == "username":
			posts = []
			for post in all_posts():
				if all_posts()[post]["username"] == value: posts.append(all_posts()[post])
			return posts
		if column == "group":
			posts = []
			for post in all_posts():
				if all_posts()[post]["group"] == value: posts.append(all_posts()[post])
			return posts
	except: return False

def get_group(column, value):
	try:
		if column == "_id": return firebase.get("/groups", value)
	except: return False

def get_comment(column, value):
	try:
		if column == "_id": return firebase.get("/comments", value)
		if column == "username":
			comments = []
			for comment in all_comments():
				if all_comments()[comment]["username"] == value: comments.append(all_comments()[comment])
			return comments
		if column == "post_id":
			comments = []
			for comment in all_comments():
				if all_comments()[comment]["post_id"] == value: comments.append(all_comments()[comment])
			return comments
	except: return []

@app.route("/")
def index():
	if "username" in session:
		users = all_users()
		groups = all_groups()
		psts = all_posts()
		li_psts = list(reversed(list(psts)))
		posts = []
		grps = []
		for post in li_psts:
			post = psts[post]
			num = 97
			if len(post["body"]) > 100:
				if post["body"][:num] == ".": post["body"] += ".."
				else: post["body"] = post["body"][:num] + "..."
			if post["group"]:
				if get_group("_id", post["group"])["status"] == "public":
					posts.append(post)
					grps.append(get_group("_id", post["group"]))
			else:
				posts.append(post)
				grps.append(None)
		if len(posts) == 0: posts = False
		return render_template("index.html", posts=posts, user=get_user("username", session["username"]), groups=groups, grps=grps)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/notifications")
def notifications():
	notifications = False
	friend_notifications = []
	user = get_user("username", session["username"])
	for _id in user["friend_notifications"].split():
		friend_notifications.append(get_user("_id", _id))
		notifications = True
	share_notifications = {}
	for info in user["share_notifications"].split():
		_id = int(info.split(":")[0])
		user_id = int(info.split(":")[1])
		share_notifications[get_post("_id", _id)] = get_user("_id", user_id)
		notifications = True
	now_friend_notifications = []
	for _id in user["now_friend_notifications"].split():
		now_friend_notifications.append(get_user("_id", _id))
		notifications = True
	follower_notifications = []
	for _id in user["follower_notifications"].split():
		follower_notifications.append(get_user("_id", _id))
		notifications = True
	added_post_notifications = []
	for _id in user["post_added_notifications"].split():
		added_post_notifications.append(get_post("_id", _id))
		notifications = True
	return render_template("notifications.html", notifications=notifications, friend_notifications=friend_notifications,\
		share_notifications=share_notifications, now_friend_notifications=now_friend_notifications, follower_notifications=follower_notifications,\
		added_post_notifications=added_post_notifications)

@app.route("/delete-notification-friend-<_id>")
def delete_notification_friend(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		friend_notifications = user["friend_notifications"].replace(_id + " ", "")
		firebase.put("/users/" + str(user["_id"]), "friend_notifications", friend_notifications)
		return redirect("/add-friend-" + _id)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-notification-now-friend-<_id>")
def delete_notification_now_friend(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		now_friend_notifications = user["now_friend_notifications"].replace(_id + " ", "")
		firebase.put("/users/" + str(user["_id"]), "now_friend_notifications", now_friend_notifications)
		return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-notification-post-<info>")
def delete_notification_post(info):
	if "username" in session:
		user = get_user("username", session["username"])
		received_posts = user["received_posts"] + info + " "
		firebase.put("/users/" + str(user["_id"]), "received_posts", received_posts)
		share_notifications = user["share_notifications"].replace(info + " ", "")
		firebase.put("/users/" + str(user["_id"]), "share_notifications", share_notifications)
		return redirect(info.split(":")[1] + "-post")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-notification-now-following-<_id>")
def delete_notification_now_following(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		follower_notifications = user["follower_notifications"].replace(_id + " ", "")
		firebase.put("/users/" + str(user["_id"]), "follower_notifications", follower_notifications)
		return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-notification-added-post-<_id>")
def delete_notification_added_post(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		post_added_notifications = user["post_added_notifications"].replace(_id + " ", "")
		firebase.put("/users/" + str(user["_id"]), "post_added_notifications", post_added_notifications)
		return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/users")
def users():
	if "username" in session:
		users = all_users()
		return render_template("users.html", users=users, user=get_user("username", session["username"]), keys=list(users.keys()), values=list(users.values()))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/signup")
def signup():
	if "username" in session: return redirect(url_for("index"))
	return render_template("signup.html", user="")

@app.route("/login")
def login():
	if "username" in session: return redirect(url_for("index"))
	return render_template("login.html", user="")

@app.route("/loggingin", methods=["POST", "GET"])
def loggingin():
	if "username" in session: return redirect(url_for("index"))
	username = request.form["username"]
	password = request.form["password"]
	found_user = get_user("username", username)
	if found_user and found_user["password"] == password:
		_id = get_id(username)
		session["username"] = username
		session["email"] = get_email(found_user["_id"])
		session["password"] = get_password(_id)
		session["first"] = get_first(_id)
		session["last"] = get_last(_id)
		session["result"] = found_user["_id"]
		return redirect(url_for("index"))
	else:
		flash("Incorrect username or password. Sign up if you haven't got an account.")
		return redirect(url_for("login"))

@app.route("/signingup", methods=["POST", "GET"])
def signingup():
	if "username" in session: return redirect(url_for("index"))
	username = request.form["username"]
	email = request.form["email"]
	password = request.form["password"]
	apassword = request.form["apassword"]
	first = request.form["first"]
	last = request.form["last"]
	found_user = get_user("username", username)
	found_email = get_user("email", email)
	if found_user:
		flash("This username is already taken. Try another one.")
		return redirect(url_for("signup"))
	elif found_email:
		flash("This email is already in use. Try another one.")
		return redirect(url_for("signup"))
	else:
		if username != "" and password != "" and email != "" and first != "" and last != "":
			if password != apassword:
				flash("Passwords don't match. Please, try again.")
				return redirect(url_for("signup"))
			session["username"] = username
			session["email"] = email
			session["password"] = password
			session["first"] = first
			session["last"] = last
			return redirect(url_for("verify"))
		else:
			flash("You need to fill all the fields!")
			return redirect(url_for("signup"))

body = f"""{code} We need to verify your email. Please, copy and paste this code in your browser."""
message = f"""\
Subject: Email verification (Social Media App)

{body}
"""

@app.route("/verify")
def verify():
	flash(code)
	try:
		server = smtplib.SMTP("smtp.outlook.com", 587)
		server.starttls()
		server.login("email@outlook.com", "password")
		server.sendmail("email@outlook.com", session["email"], message)
	except: pass
	return render_template("verify.html", user="")

@app.route("/verifying", methods=["POST", "GET"])
def verifying():
	flash(code)
	try:
		if int(request.form["code"]) == int(code):
			username = session["username"]
			email = session["email"]
			password = session["password"]
			first = session["first"]
			last = session["last"]
			user = {
				"_id": "",
				"username": username,
				"email": email,
				"password": password,
				"first": first,
				"last": last,
				"posts": 0,
				"liked_items": "",
				"saved_items": "",
				"commented_items": "",
				"friends": "",
				"groups": "",
				"friend_notifications": "",
				"share_notifications": "",
				"now_friend_notifications": "",
				"follower_notifications": "",
				"post_added_notifications": "",
				"half_friends": "",
				"received_posts": "",
				"followers": "",
				"following": ""
			}
			result = firebase.post("/users", user)
			session["result"] = result["name"]
			firebase.put("/users/" + session["result"], "_id", session["result"])
			return redirect(url_for("index"))
		else:
			flash("We were not able to verify your email. Please, sign up again.")
			session.pop("username", None)
			session.pop("email", None)
			session.pop("password", None)
			session.pop("first", None)
			session.pop("last", None)
			return redirect(url_for("signup"))
	except:
		flash("We were not able to verify your email. Please, sign up again.")
		session.pop("username", None)
		session.pop("email", None)
		session.pop("password", None)
		session.pop("first", None)
		session.pop("last", None)
		return redirect(url_for("signup"))

@app.route("/add")
def add():
	if "username" in session: return render_template("add.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/adding", methods=["POST", "GET"])
def adding():
	if "username" in session:
		post = request.form["post"]
		title = request.form["title"]
		if post != "" and title != "":
			date = str(datetime.now())[:10]
			date = f"{date[5]}{date[6]}/{date[-2]}{date[-1]}/{date[0]}{date[1]}{date[2]}{date[3]}"
			user = get_user("username", session["username"])
			posts = user["posts"] + 1
			firebase.put("/users/" + user["_id"], "posts", posts)
			for _id in user["followers"].split():
				follower = get_user("_id", _id)
				post_added_notifications = follower["post_added_notifications"] + str(len(all_posts())+1) + " "
				firebase.put("/users/" + str(follower["_id"]), "post_added_notifications", post_added_notifications)
			_file = ""
			if "file" in request.files: _file = request.files["file"].filename
			pst = {
				"_id": "",
				"username": session["username"],
				"user_id": get_id(session["username"]),
				"title": title,
				"body": post,
				"pub_date": date,
				"likes": 0,
				"saved": 0,
				"comments": 0,
				"group": "",
				"file": _file
			}
			result = firebase.post("/posts", pst)
			firebase.put("/posts/" + result["name"], "_id", result["name"])
			if _file: _file = request.files["file"]
			storage.child(f"/{result['name']}/" + _file.filename).put(_file)
			return redirect(f"/{result['name']}-post")
		else:
			flash("You need to fill all the fields!")
			return redirect(url_for("add"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/settings")
def settings():
	if "username" in session:
		posts = len(get_post("username", session["username"]))
		user = get_user("username", session["username"])
		if posts > 0: delete = True
		else: delete = False
		return render_template("settings.html", user=user, delete=delete)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/logout")
def logout():
	session.pop("username", None)
	session.pop("email", None)
	session.pop("password", None)
	session.pop("first", None)
	session.pop("last", None)
	session.pop("result", None)
	return redirect(url_for("login"))

@app.route("/change")
def change():
	if "username" in session:
		username = session["username"]
		email = session["email"]
		first = session["first"]
		last = session["last"]
		return render_template("change.html", username=username, email=email, first=first, last=last, user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/changing", methods=["POST", "GET"])
def changing():
	if "username" in session:
		username = request.form["username"]
		first = request.form["first"]
		last = request.form["last"]
		user = get_user("username", session["username"])
		firebase.put("/users/" + str(user["_id"]), "username", username)
		firebase.put("/users/" + str(user["_id"]), "first", first)
		firebase.put("/users/" + str(user["_id"]), "last", last)
		session["username"] = username
		session["first"] = first
		session["last"] = last
		return redirect(url_for("settings"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-account")
def delete_account():
	if "username" in session: return render_template("delete_account.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/deleting-account", methods=["POST", "GET"])
def deleting_account():
	if "username" in session:
		password = request.form["password"]
		usr = get_user("username", session["username"])
		if password == usr["password"]:
			if usr["posts"] > 0:
				users = all_users()
				posts = get_post("username", session["username"])
				ids = []
				for post in posts: ids.append(post["_id"])
				for user in users:
					for _id in ids:
						if _id in users[user]["liked_items"].split():
							liked_items = users[user]["liked_items"].replace(f"{_id} ", "")
							firebase.put("/users/" + user, "liked_items", liked_items)
						if _id in users[user]["saved_items"].split():
							saved_items = users[user]["saved_items"].replace(f"{_id} ", "")
							firebase.put("/users/" + user, "saved_items", saved_items)
						if _id in users[user]["commented_items"].split():
							commented_items = users[user]["commented_items"].replace(f"{_id} ", "")
							firebase.put("/users/" + user, "commented_items", commented_items)
				for post in posts:
					if post["group"]:
						group = get_group("_id", post["group"])
						posts = group["posts"].replace(post["_id"] + " ", "")
						firebase.put("/group/" + group["_id"], "posts", posts)
				for post in posts: firebase.delete("/posts", post["_id"])
			if usr["liked_items"] != "":
				for _id in usr["liked_items"].split():
					if _id != "":
						post = get_post("_id", _id)
						likes = post["likes"] - 1
						firebase.put("/posts/" + str(post["_id"]), "likes", likes)
			if usr["saved_items"] != "":
				for _id in usr["saved_items"].split():
					if _id != "":
						post = get_post("_id", _id)
						saved = post["saved"] - 1
						firebase.put("/posts/" + str(post["_id"]), "saved", saved)
			if usr["commented_items"] != "":
				for _id in usr["commented_items"].split():
					if _id != "":
						post = get_post("_id", _id)
						comments = post["comments"] - 1
						firebase.put("/posts/" + str(post["_id"]), "comments", comments)
				for comment in get_comment("username", session["username"]): firebase.delete("/comments", comment["_id"])
			session.pop("username", None)
			session.pop("email", None)
			session.pop("password", None)
			session.pop("first", None)
			session.pop("last", None)
			if len(usr["friends"].split()) > 0:
				for _id in usr["friends"].split():
					if _id != "":
						friend = get_user("_id", _id)
						friends = friend["friends"].replace(f"{str(usr._id)} ", "")
						firebase.put("/users/" + str(friend["_id"]), "friends", friends)
			for _id in usr["groups"].split():
				group = get_group("_id", _id)
				for i in group["members"].split():
					user = get_user("_id", int(i))
					groups = user["groups"].replace(_id + " ", "")
					firebase.put("/users/" + str(user["_id"]), "groups", groups)
				for i in group["posts"].split():
					post = get_post("_id", int(i))
					user = get_user("_id", post["user_id"])
					user["posts"] -= 1
					users = all_users()
					for user in users:
						if _id in user["liked_items"].split():
							liked_items = user["liked_items"].replace(f"{_id} ", "")
							firebase.put("/users/" + str(user["_id"]), "liked_items", liked_items)
						if _id in user["saved_items"].split():
							saved_items = user["saved_items"].replace(f"{_id} ", "")
							firebase.put("/users/" + str(user["_id"]), "saved_items", saved_items)
						if _id in user["commented_items"].split():
							commented_items = user["commented_items"].replace(f"{_id} ", "")
							firebase.put("/users/" + str(user["_id"]), "commented_items", commented_items)
					firebase.delete("/posts", post["_id"])
			firebase.delete("/users", usr["_id"])
		else:
			flash("Incorrect password. Try again.")
			return redirect(url_for("delete_account"))
		flash("Your account was successfully deleted.")
		return redirect(url_for("signup"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-all-password")
def delete_all_password():
	if "username" in session: return render_template("delete_all_password.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-all", methods=["POST", "GET"])
def delete_all():
	if "username" in session:
		usr = get_user("username", session["username"])
		if usr["password"] == request.form["password"]:
			usr["posts"] = 0
			posts = get_post("username", session["username"])
			ids = []
			for post in posts: ids.append(str(post["_id"]))
			users = all_users()
			for user in users:
				for _id in ids:
					if _id in users[user]["liked_items"].split():
						liked_items = users[user]["liked_items"].replace(f"{_id} ", "")
						firebase.put("/users/" + user, "liked_items", liked_items)
					if _id in users[user]["saved_items"].split():
						saved_items = users[user]["saved_items"].replace(f"{_id} ", "")
						firebase.put("/users/" + user, "saved_items", saved_items)
					if _id in users[user]["commented_items"].split():
						commented_items = users[user]["commented_items"].replace(f"{_id} ", "")
						firebase.put("/users/" + user, "commented_items", commented_items)
			for post in posts:
				if post["group"]:
					group = get_group("_id", post["group"])
					posts = group["posts"].replace(post["_id"], " ")
					firebase.put("/groups/" + str(group["_id"]), "posts", posts)
			for post in posts: firebase.delete("/posts", post["_id"])
			return redirect(url_for("settings"))
		else: return redirect(url_for("delete_all_password"))
		return render_template("error.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-<_id>")
def delete(_id):
	if "username" in session:
		post = get_post("_id", _id)
		user = get_user("username", session["username"])
		posts= user["posts"] - 1
		firebase.put("/users/" + user["_id"], "posts", posts)
		users = all_users()
		li_users = list(users)
		for user in li_users:
			user = users[user]
			if _id in user["liked_items"].split():
				liked_items = user["liked_items"].replace(f"{_id} ", "")
				firebase.put("/users/" + user["_id"], "liked_items", liked_items)
			if _id in user["saved_items"].split():
				saved_items = user["saved_items"].replace(f"{_id} ", "")
				firebase.put("/users/" + user["_id"], "saved_items", saved_items)
			if _id in user["commented_items"].split():
				commented_items = user["commented_items"].replace(f"{_id} ", "")
				firebase.put("/users/" + user["_id"], "commented_items", commented_items)
		if post["group"]:
			group = get_group("_id", post["group"])
			posts = group["posts"].replace(_id + " ", "")
			firebase.put("/groups/" + group["_id"], "posts", posts)
		firebase.delete("/posts", post["_id"])
		return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-comment-<_id>")
def delete_comment(_id):
	if "username" in session:
		comment = get_comment("_id", _id)
		user = get_user("username", session["username"])
		post = get_post("_id", comment["post_id"])
		comments = post["comments"] - 1
		firebase.put("/posts/" + str(post["_id"]), "comments", comments)
		firebase.delete("/comments", comment["_id"])
		return redirect(f"/{comment['post_id']}-post")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/search")
def search():
	if "username" in session: return render_template("search.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/searching")
def searching():
	if "username" in session:
		query = request.args["q"].lower()
		posts = []
		users = []
		groups = []
		psts = all_posts()
		for _id in psts:
			if psts[_id]["title"].lower().startswith(query): posts.append(psts[_id])
			for q in query.split():
				if psts[_id] in posts: break
				for word in psts[_id]["title"].lower().split():
					if q == word or word.startswith(q) or q.startswith(word) or word.endswith(q) or q.endswith(word):
						posts.append(psts[_id])
						break
		usrs = all_users()
		for _id in usrs:
			if usrs[_id]["username"].lower().startswith(query): users.append(usrs[_id])
			if usrs[_id]["first"].lower().startswith(query) and usrs[_id] not in users: users.append(usrs[_id])
			if usrs[_id]["last"].lower().startswith(query) and usrs[_id] not in users: users.append(usrs[_id])
		grps = all_groups()
		for _id in grps:
			if grps[_id]["name"].lower().startswith(query) or group[_id]["name"].lower().endswith(query): groups.append(grps[_id])
			for q in query.split():
				if grps[_id] in groups: break
				for word in grps[_id]["description"].lower().split():
					if q == word:
						groups.append(grps[_id])
						break
		return render_template("result.html", posts=posts, users=users, groups=groups, user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/change-password")
def change_password():
	if "username" in session: return render_template("password.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/changing-password", methods=["POST", "GET"])
def changing_password():
	if "username" in session:
		old_password = request.form["old_password"]
		new_password = request.form["new_password"]
		user = get_user("username", session["username"])
		if user["password"] == old_password:
			firebase.put("/users/" + str(user["_id"]), "password", new_password)
			flash("Successefully changed password.")
			return redirect(url_for("settings"))
		else:
			flash("Incorrect old password. Try again.")
			return redirect(url_for("change_password"))
		return render_template("error.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/library")
def library():
	if "username" in session:
		posts = get_post("username", session["username"])
		user = get_user("username", session["username"])
		friends = []
		for _id in user["friends"].split():
			if _id != "":
				friend = get_user("_id", _id)
				if str(user["_id"]) in friend["friends"].split(): friends.append(friend)
		liked_posts = []
		for _id in user["liked_items"].split():
			if _id != "": liked_posts.append(get_post("_id", _id))
		saved_posts = []
		for _id in user["saved_items"].split():
			if _id != "": saved_posts.append(get_post("_id", _id))
		received_posts = {}
		for info in user["received_posts"].split():
			user_id = int(info.split(":")[0])
			post_id = int(info.split(":")[1])
			usr = get_user("_id", user_id)
			post = get_post("_id", post_id)
			received_posts[post] = usr
		users = []
		for post in received_posts:
			usr = get_user("_id", post["user_id"])
			users.append(usr)
		l_r_p = list(received_posts)
		groups = []
		for _id in user["groups"].split(): groups.append(get_group("_id", _id))
		followers = []
		for _id in user["followers"].split(): followers.append(get_user("_id", _id))
		following = []
		for _id in user["following"].split(): following.append(get_user("_id", _id))
		return render_template("library.html",\
			posts=posts, liked_posts=liked_posts, saved_posts=saved_posts, friends=friends, groups=groups,\
				user=user, received_posts=received_posts, users=users, l_r_p=l_r_p, followers=followers, following=following)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/share-<_id>")
def share(_id):
	if "username" in session:
		post = get_post("_id", _id)
		friends = []
		user = get_user("username", session["username"])
		for _id in user["friends"].split():
			if _id != "":
				friend = get_user("_id", _id)
				friends.append(friend)
		return render_template("share.html", post=post, friends=friends, user=user)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/sharing-<info>")
def sharing(info):
	if "username" in session:
		user_id = info.split(":")[0]
		_id = info.split(":")[1]
		post_id = info.split(":")[2]
		user = get_user("_id", user_id)
		shared_notifications = str(_id) + ":" + str(post_id) + " "
		firebase.put("/users/" + str(user["_id"]), "shared_notifications", shared_notifications)
		return redirect(f"share-{_id}")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/add-comment-<_id>", methods=["POST", "GET"])
def add_comment(_id):
	if "username" in session:
		text = request.form["text"]
		date = str(datetime.now())[:10]
		date = f"{date[5]}{date[6]}/{date[-2]}{date[-1]}/{date[0]}{date[1]}{date[2]}{date[3]}"
		comment = {
			"_id": "",
			"username": session["username"],
			"text": text,
			"pub_date": date,
			"post_id": _id
		}
		result = firebase.post("/comments", comment)
		firebase.put("/comments/" + result["name"], "_id", result["name"])
		user = get_user("username", session["username"])
		commented_items = user["commented_items"] + f"{_id} "
		firebase.put("/users/" + user["_id"], "commented_items", commented_items)
		post = get_post("_id", _id)
		post_comments = post["comments"] + 1
		firebase.put("/posts/" + post["_id"], "comments", post_comments)
		return redirect(f"{_id}-post")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/<_id>-post")
def post(_id):
	if "username" in session:
		post = get_post("_id", _id)
		if not post: return render_template("error.html")
		user = get_user("username", session["username"])
		group = None
		if post["group"]:
			group = get_group("_id", post["group"])
			if group["status"] == "private":
				if str(user["_id"]) not in group["members"].split(): return redirect(url_for("index"))
		url = ""
		download = ""
		if post["file"]:
			ext = post["file"].split(".")[1]
			imgs = ["jpg", "png", "raw", "bmp", "jfif", "gif"]
			if ext in imgs: url = f"https://firebasestorage.googleapis.com/v0/b/test-30d03.appspot.com/o/{post['_id']}%2F{post['file']}?alt=media&"
			else: download = f"https://firebasestorage.googleapis.com/v0/b/test-30d03.appspot.com/o/{post['_id']}%2F{post['file']}?alt=media&"
		liked_items = user["liked_items"].split()
		saved_items = user["saved_items"].split()
		likeable = True
		saveable = True
		if str(_id) in liked_items: likeable = False
		if str(_id) in saved_items: saveable = False
		cmmnts = get_comment("post_id", _id)
		comments = []
		delete = []
		if cmmnts:
			for comment in list(reversed(cmmnts)): comments.append(comment)
		else: comments = []
		if comments:
			for comment in comments:
				if comment["username"] == session["username"]: delete.append(comment)
		return render_template("post.html", post=post, likeable=likeable, saveable=saveable,\
			comments=comments, delete=delete, user=user, _id=post["user_id"], group=group, url=url, download=download)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/<_id>-save")
def save(_id):
	if "username" in session:
		post = get_post("_id", _id)
		user = get_user("username", session["username"])
		if str(post["_id"]) not in user["saved_items"].split():
			saved_items = user["saved_items"] + str(post["_id"]) + " "
			saved = post["saved"] + 1
			firebase.put("/users/" + str(user["_id"]), "saved_items", saved_items)
			firebase.put("/posts/" + str(post["_id"]), "saved", saved)
		return jsonify(post["saved"])
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/<_id>-like")
def like(_id):
	if "username" in session:
		post = get_post("_id", _id)
		user = get_user("username", session["username"])
		if str(post["_id"]) not in user["liked_items"].split():
			liked_items = user["liked_items"] + str(post["_id"]) + " "
			likes = post["likes"] + 1
			firebase.put("/users/" + str(user["_id"]), "liked_items", liked_items)
			firebase.put("/posts/" + str(post["_id"]), "likes", likes)
		return jsonify(post["likes"])
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/add-friend-<_id>")
def add_friend(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		if str(_id) not in user["friends"].split():
			friend = get_user("_id", _id)
			if str(user["_id"]) not in friend["half_friends"].split():
				if str(_id) not in user["half_friends"].split():
					half_friends = user["half_friends"] + str(_id) + " "
					friend_notifications = friend["friend_notifications"] + str(user["_id"]) + " "
					firebase.put("/users/" + str(user["_id"]), "half_friends", half_friends)
					firebase.put("/users/" + str(friend["_id"]), "friend_notifications", friend_notifications)
					flash(f"Waiting for @{friend['username']} to accept your friendship.")
				return redirect(f"/{friend['_id']}")
			else:
				half_friends = friend["half_friends"].replace(str(user["_id"]) + " ", "")
				friends_friends = friend["friends"] + str(_id) + " "
				friends = user["friends"] + str(_id) + " "
				now_friend_notifications = friend["now_friend_notifications"] + str(user["_id"]) + " "
				firebase.put("/users/" + str(friend["_id"]), "half_friends", half_friends)
				firebase.put("/users/" + str(user["_id"]), "friends", friends)
				firebase.put("/users/" + str(friend["_id"]), "friends", friends_friends)
				firebase.put("/users/" + str(friend["_id"]), "now_friend_notifications", now_friend_notifications)
				flash(f"@{friend['username']} is now your friend.")
				return redirect(url_for("index"))
		else: return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-friend-<_id>")
def delete_friend(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		friend = get_user("_id", _id)
		friends = user["friends"].replace(f"{str(_id)} ", "")
		friends_friends = friend["friends"].replace(f"{str(user['_id'])} ", "")
		firebase.put("/users/" + str(user["_id"]), "friends", friends)
		firebase.put("/users/" + str(friend["_id"]), "friends", friends_friends)
		return redirect(url_for("library"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/create-group")
def create_group():
	if "username" in session:
		return render_template("create_group.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/creating-group", methods=["POST", "GET"])
def creating_group():
	if "username" in session:
		name = request.form["name"]
		description = request.form["description"]
		try: status = request.form["status"]
		except:
			flash("You need to select the status of the group!")
			return redirect(url_for("create_group"))
		if name != "" and description != "" and status != "":
			user = get_user("username", session["username"])
			group = {
				"_id": "",
				"name": name,
				"admin": user["_id"],
				"description": description,
				"members": str(user["_id"]) + " ",
				"status": status,
				"posts": ""
			}
			result = firebase.post("/groups", group)
			firebase.put("/groups/" + result["name"], "_id", result["name"])
			group = get_group("_id", "")
			groups = user["groups"] + result["name"] + " "
			firebase.put("/users/" + str(user["_id"]), "groups", groups)
			return redirect(f"{result['name']}-group")
		else:
			flash("You need to fill all the fields!")
			return redirect(url_for("create_group"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/<_id>-group")
def group(_id):
	if "username" in session:
		group = get_group("_id", _id)
		if not group: return redirect(url_for("index"))
		user = get_user("username", session["username"])
		member = False
		if str(group["_id"]) in user["groups"].split(): member = True
		if not member and group["status"] == "private":
			flash("You cannot see the posts inside of this group because this group is private.")
			return redirect(url_for("index"))
		members = []
		admin = False
		if group["admin"] == user["_id"]: admin = True
		for i in group["members"].split():
			if i != "":
				mmbr = get_user("_id", i)
				members.append(mmbr)
		administrator = get_user("_id", group["admin"])["username"]
		psts = get_post("group", _id)
		posts = []
		delete = []
		if psts:
			for post in psts:
				if post["username"] == session["username"]: delete.append(post)
				num = 97
				if len(post["body"]) > 100:
					if post["body"][:num] == ".": post["body"] += ".."
					else: post["body"] = post["body"][:num] + "..."
				posts.append(post)
		return render_template("group.html", group=group, members=members, len=len(members), member=member, admin=admin, user=user, administrator=administrator, posts=posts, delete=delete)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/invite-<_id>")
def invite(_id):
	if "username" in session:
		group = get_group("_id", _id)
		user = get_user("username", session["username"])
		friends = []
		for _id in user["friends"].split():
			if _id != "":
				friend = get_user("_id", _id)
				if str(group["_id"]) not in friend["groups"].split(): friends.append(friend)
		return render_template("invite.html", group=group, friends=friends, user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/inviting-<info>")
def inviting(info):
	if "username" in session:
		friend_id = int(info.split(":")[0])
		_id = int(info.split(":")[1])
		group = get_group("_id", _id)
		members = group["members"] + f"{friend_id} "
		firebase.put("/groups/" + str(group["_id"]), "members", members)
		user = get_user("_id", friend_id)
		users_groups = user["groups"] + f"{group['_id']} "
		firebase.put("/users/" + str(user["_id"]), "groups", users_groups)
		return redirect(f"/{_id}-group")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/invite-users-<_id>")
def invite_users(_id):
	if "username" in session:
		group = get_group("_id", _id)
		user = get_user("username", session["username"])
		if user["_id"] == group["admin"]:
			users = []
			for user in all_users():
				if str(group["_id"]) not in user["groups"].split(): users.append(user)
			return render_template("invite_users.html", group=group, users=users, user=user)
		else:
			flash("You cannot invite users to this group unless they are your friends.")
			return redirect(f"/{_id}-group")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/remove-from-group-<info>")
def remove_from_group(info):
	if "username" in session:
		user_id = int(info.split(":")[0])
		_id = int(info.split(":")[1])
		user = get_user("_id", user_id)
		group = get_group("_id", _id)
		groups = user["groups"].replace(f"{str(_id)} ", "")
		firebase.put("/users/" + str(user["_id"]), "groups", groups)
		members = group["members"].replace(f"{user_id} ", "")
		firebase.put("/groups/" + str(group["_id"]), "members", members)
		return redirect(f"/{_id}-group")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/change-admin-<_id>")
def change_admin(_id):
	if "username" in session:
		group = get_group("_id", _id)
		members = []
		for _id in group["members"].split():
			member = get_user("_id", _id)
			members.append(member)
		return render_template("change_admin.html", group=group, members=members)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/changing-admin-<info>")
def changing_admin(info):
	if "username" in session:
		user_id = int(info.split(":")[0])
		group_id = int(info.split(":")[1])
		group = get_group("_id", group_id)
		firebase.put("/groups/" + str(group["_id"]), "admin", user_id)
		return redirect(f"/{group_id}-group")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/add-<_id>")
def add_post_group(_id):
	if "username" in session: return render_template("add_inside_group.html", _id=_id, user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/adding-inside-<_id>", methods=["POST", "GET"])
def adding_post_group(_id):
	if "username" in session:
		title = request.form["title"]
		body = request.form["post"]
		if title != "" and body != "":
			date = str(datetime.now())[:10]
			date = f"{date[5]}{date[6]}/{date[-2]}{date[-1]}/{date[0]}{date[1]}{date[2]}{date[3]}"
			user = get_user("username", session["username"])
			_file = ""
			if "file" in request.files: _file = request.files["file"].filename
			post = {
				"_id": "",
				"username": session["username"],
				"user_id": user["_id"],
				"title": title,
				"body": body,
				"pub_date": date,
				"likes": 0,
				"saved": 0,
				"comments": 0,
				"group": "",
				"file": _file
			}
			result = firebase.post("/posts", post)
			firebase.put("/posts/" + result["name"], "_id", result["name"])
			if _file: _file = request.files["file"]
			storage.child(f"/{result['name']}/" + _file.filename).put(_file)
			group = get_group("_id", _id)
			post = get_post("_id", result["name"])["_id"]
			group_posts = group["posts"] + str(post) + " "
			firebase.put("/groups/" + str(group["_id"]), "posts", group_posts)
			firebase.put("/posts/" + result["name"], "group", _id)
			user = get_user("username", session["username"])
			user_posts = user["posts"] + 1
			firebase.put("/users/" + str(user["_id"]), "posts", user_posts)
			return redirect(f"/{_id}-group")
		else:
			flash("You need to fill all the fields!")
			return redirect(f"/add-{_id}")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/add-follower-<info>")
def add_follower(info):
	if "username" in session:
		user = get_user("_id", info.split(":")[0])
		follower = get_user("_id", info.split(":")[1])
		if follower["_id"] not in user["following"].split():
			following = user["following"] + follower["_id"] + " "
			followers = follower["followers"] + user["_id"] + " "
			firebase.put("/users/" + user["_id"], "following", following)
			firebase.put("/users/" + follower["_id"], "followers", followers)
		follower_notifications = follower["follower_notifications"] + str(user["_id"]) + " "
		firebase.put("/users/" + follower["_id"], "follower_notifications", follower_notifications)
		return redirect("/" + follower["_id"])
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/unfollow-<_id>")
def unfollow(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		following = user["following"].replace(_id + " ", "")
		firebase.put("/users/" + user["_id"], "following", following)
		following_user = get_user("_id", _id)
		followers = following_user["followers"].replace(user["_id"] + " ", "")
		firebase.put("/users/" + following_user["_id"], "followers", followers)
		return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-group-password-<_id>")
def delete_group_password(_id):
	if "username" in session: return render_template("delete_group.html", _id=_id, user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-group-<_id>", methods=["POST", "GET"])
def delete_group(_id):
	if "username" in session:
		password = request.form["password"]
		user = get_user("username", session["username"])
		if user["password"] == password:
			group = get_group("_id", _id)
			for i in group["members"].split():
				usr = get_user("_id", int(i))
				groups = usr["groups"].replace(str(_id) + " ", "")
				firebase.put("/users/" + str(usr["_id"]), "groups", groups)
			for i in group["posts"].split():
				post = get_post("_id", int(i))
				usr = get_user("_id", post["user_id"])
				posts = usr["posts"] - 1
				firebase.put("/users/" + str(usr["_id"]), "posts", posts)
				users = all_users()
				for user in users:
					if _id in user["liked_items"].split():
						liked_items = user["liked_items"].replace(f"{_id} ", "")
						firebase.put("/users/" + user["_id"], "liked_items", liked_items)
					if _id in user["saved_items"].split():
						saved_items = user["saved_items"].replace(f"{_id} ", "")
						firebase.put("/users/" + user["_id"], "saved_items", saved_items)
					if _id in user["commented_items"].split():
						commented_items = user["commented_items"].replace(f"{_id} ", "")
						firebase.put("/users/" + user["_id"], "commented_items", commented_items)
						firebase.put("/users/" + user["_id"], "comments", comments)
				firebase.delete("/posts", post["_id"])
			firebase.delete("/groups", group["_id"])
			return redirect(url_for("index"))
		else:
			flash("Incorrect password.")
			return redirect(f"/{_id}-group")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/searching-<info>")
def searching_friends(info):
	if "username" in session:
		usrs = info.split(":")[0]
		_id = int(info.split(":")[1])
		user = get_user("username", session["username"])
		group = get_group("_id", _id)
		query = request.args["q"].lower()
		l = []
		if usrs == "friends":
			for _id in user["friends"].split():
				friend = get_user("_id", _id)
				l.append(friend)
		else:
			tmp = all_users()
			tmp.remove(user)
			l = tmp
		users = []
		for u in l:
			if u["username"].lower().startswith(query): users.append(u)
			if u["first"].lower().startswith(query) and u not in users: users.append(u)
			if u["last"].lower().startswith(query) and u not in users: users.append(u)
		return render_template("result_invite.html", users=users, group=group)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/<_id>")
def user(_id):
	if "username" in session:
		user = get_user("_id", _id)
		if user:
			psts = get_post("username", user["username"])
			posts = []
			num = 97
			for post in list(reversed(psts)):
				if len(post["body"]) > 100:
					if post["body"][:num] == ".": post["body"] += ".."
					else: post["body"] = post["body"][:num] + "..."
				posts.append(post)
			friend = True
			follower = False
			followers = []
			following = []
			current_user = get_user("username", session["username"])
			if user["_id"] != current_user["_id"] and str(user["_id"]) not in current_user["friends"].split(): friend = False
			if str(current_user["_id"]) in user["followers"].split(): follower = True
			friends = []
			if friend or session["username"] == user["username"]:
				for _id in user["friends"].split(): friends.append(get_user("_id", _id))
			groups = []
			for _id in user["groups"].split(): groups.append(get_group("_id", _id))
			for _id in user["followers"].split(): followers.append(get_user("_id", _id))
			for _id in user["following"].split(): following.append(get_user("_id", _id))
			return render_template("user.html",\
				username=user["username"], email=user["email"], first=user["first"], last=user["last"], number=user["posts"], posts=posts, friend=friend, friends=friends, user=current_user, groups=groups, _id=user["_id"], follower=follower, followers=followers, followers_num=len(followers), following=following, following_num=len(following))
		return render_template("error.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

if __name__ == "__main__":
	app.run(debug=True)
