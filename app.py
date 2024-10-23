from flask import Flask, request, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, DeleteForm, FeedbackForm

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = "oh-so-secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

app.app_context().push()
connect_db(app)


@app.route("/")
def homepage():
    """Site homepage; redirect to register."""

    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a user. Show form and handle form submission"""

    # user already logged in
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        # register() will hash password
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)

        # if username or email is not unique, return to register form.
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username already exists.')
            return render_template('/users/register.html', form=form)
        
        db.session.commit()
        session["username"] = new_user.username

        flash('Welcome! Account successfully created!', "success")

        return redirect(f"/users/{session['username']}")
    
    else:
        return render_template("users/register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """View login form. Handle form submission"""

    # user already logged in
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # authenticate() will return <user> or false
        user = User.authenticate(username, password)
        if user:
            session["username"] = user.username
            flash(f"Welcome {user.full_name}", "success")
            return redirect(f"/users/{session['username']}")
        else:
            form.username.errors = ["Invalid username/password."]
            return render_template("users/login.html", form=form)
    
    return render_template("users/login.html", form=form)


@app.route("/logout")
def logout():
    """Logout user"""

    session.pop("username")
    flash("Goodbye!", "info")
    return redirect("/")


@app.route("/users/<username>")
def show_user(username):
    """Logged-in user info"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get_or_404(username)
    form = FeedbackForm()

    return render_template("users/show.html", user=user, form=form)


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Remove user. Redirect to login."""

    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get_or_404(username)

    db.session.delete(user)
    db.session.commit()

    session.pop("username")
    flash("User deleted", "danger")

    return redirect("/login")


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def new_feedback(username):
    """Show add-feedback form and handle form submission"""


    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
                    title=title,
                    content=content,
                    username=username
        )

        db.session.add(feedback)
        db.session.commit()

        flash("New feedback created!", "success")

        return redirect(f"/users/{feedback.username}")
    
    return render_template("feedback/new.html", form=form)
    

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show update-feedback form and handle form submission"""

    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()    
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        flash("Feedback updated!", "info")

        return redirect(f"/users/{ feedback.username }")
    
    return render_template("feedback/edit.html", form=form, feedback=feedback)
    

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete a specific feedback"""

    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()    
    
    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted!", "danger")

    return redirect(f"/users/{ feedback.username }")