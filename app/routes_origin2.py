from app import application, classes, db, search_lyrics
from app.Melon_Model.Melon.generate import *

import os
import secrets

from flask import Flask, flash, url_for, request
from flask import render_template, render_template_string, redirect, session
from flask_login import current_user, login_user, login_required, logout_user
from PIL import Image


@application.route("/", methods=["GET", "POST"])
@application.route("/index", methods=["GET", "POST"])
def index():
    """render the main page of index.html."""
    if current_user.is_authenticated:
        user = current_user.username
    else:
        user = "Anonymous"
    return render_template(
        "index.html",
        user=user,
        authenticated_user=current_user.is_authenticated
    )


@application.route("/player", methods=["GET", "POST"])
def player():
    return render_template('player.html')

@application.route("/flow", methods=["GET", "POST"])
def flow():
    return render_template('flow.html')

@application.route("/register", methods=("GET", "POST"))
def register():
    """display register page for new users"""
    registration_form = classes.RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        password = registration_form.password.data
        email = registration_form.email.data
        image_file = registration_form.image_file.data
        gender = registration_form.gender.data
        age = registration_form.age.data
        city = registration_form.city.data

        user_count = (
            classes.User.query.filter_by(username=username).count()
            + classes.User.query.filter_by(email=email).count()
        )
        if user_count > 0:
            flash("Error - Existing user : " + username + " OR " + email)
        else:
            user = classes.User(
                username, email, password, image_file, gender, age, city
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template(
        "register.html",
        form=registration_form,
        authenticated_user=current_user.is_authenticated,
    )


@application.route("/login", methods=["GET", "POST"])
def login():
    """display login page for registered users"""
    login_form = classes.LogInForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data

        user = classes.User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for("user"))
        else:
            flash("Invalid username and password combination!")
    return render_template(
        "login.html",
        form=login_form,
        authenticated_user=current_user.is_authenticated
    )


@application.route("/logout")
def logout():
    """execute logout for current user"""
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("index"))


@application.route("/user")
@login_required
def user():
    """display user profile of certain user"""
    if current_user.is_authenticated:
        user = current_user
        username = user.username
        profile = classes.Profile.query.filter_by(username=username).first()
        image_file = url_for(
            "static", filename="profile_pics/" + current_user.image_file
        )
        return render_template(
            "user.html",
            user=user,
            profile=profile,
            image_file=image_file,
            authenticated_user=current_user.is_authenticated,
        )
    else:
        user = "Anonymous"
        return render_template(
            "index.html",
            user=user,
            authenticated_user=current_user.is_authenticated
        )


@application.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """display profile page for users to edit personal information"""
    user = current_user
    username = user.username
    profile_form = classes.ProfileForm()
    if profile_form.validate_on_submit():
        if profile_form.image_file.data:
            picture_file = save_picture(profile_form.image_file.data)
            current_user.image_file = picture_file
        if profile_form.gender.data:
            current_user.gender = profile_form.gender.data
        if profile_form.age.data:
            current_user.age = profile_form.age.data
        if profile_form.city.data:
            current_user.city = profile_form.city.data

        profile_prev = classes.Profile.query.\
            filter_by(username=username).first()
        if profile_prev:
            db.session.delete(profile_prev)
        profile_new = classes.Profile(
            username,
            current_user.gender,
            current_user.age,
            current_user.city,
            current_user.image_file,
        )
        db.session.add(profile_new)
        db.session.commit()
        return redirect(url_for("user"))
    return render_template(
        "profile.html",
        form=profile_form,
        authenticated_user=current_user.is_authenticated,
    )


@application.route("/search", methods=["GET", "POST"])
def search():
    """display webpage for users to search for lyrics"""
    lyrics = ""
    if current_user.is_authenticated:
        user = current_user
        print(1)
    else:
        user = "Anonymous"

    if request.method == 'POST':
        if request.form["submit"] == 'search':
            try:
                singer = request.form["singer"]
                song = request.form["song"]            
                if singer and song:
                    lyrics = search_lyrics.get_lyrics(singer, song)
                return render_template(
                    "search.html",
                    user=user,
                    lyrics=lyrics,
                    singer=singer,
                    song=song,
                    authenticated_user=current_user.is_authenticated
                )
            except Exception as e:
                print(e)
            return render_template(
                "search.html",
                user=user,
                authenticated_user=current_user.is_authenticated
            )
        if request.form["submit"] == 'Confirm your lyrics':
            input_lyrics = request.form['input_lyrics']
            if not input_lyrics:
                flash('Please enter the lyrics you like')
            else:
                session['input_lyrics'] = input_lyrics
                flash('Successfully store the lyrics!')
            return render_template('search.html', user=user, authenticated_user=current_user.is_authenticated,
                    input_lyrics=input_lyrics)

    return render_template(
            "search.html",
            user=user,
            authenticated_user=current_user.is_authenticated)

@application.route("/generate", methods=["GET", "POST"])
def generate():
    if current_user.is_authenticated:
        user = current_user
    else:
        user = "Anonymous"
    if request.method == 'POST' and request.form["submit"] == 'Generate!':
        try:
            base_dir = os.path.abspath(os.path.dirname(__file__))
            syll_model_path = (
                base_dir +
                "/Melon_Model/data/pretrained/encoding" +
                "/syllEncoding_20190419.bin"
            )
            word_model_path = (
                base_dir +
                "/Melon_Model/data/pretrained/encoding" +
                "/wordLevelEncoder_20190419.bin"
            )
            model_path = (
                base_dir +
                "/Melon_Model/data/pretrained/melody" +
                "/epochs_models/model_epoch395"
            )
            lyrics = session.get('input_lyrics', 'Happy birthday to you') # if no lyrics input, try a random generation
            syllables = create_syllable(lyrics)
            melody_midi = create_melody(
                syll_model_path, word_model_path, model_path, syllables
            )
        
            try:
                target_key = request.form["key"]
                instrument = request.form['instrument']
                output_stream = create_harmonization(melody_midi, target_key)
                # Add instrument in the model
            except Exception as e:
                target_key = "Default"
                instrument = 'Default'
                output_stream = create_harmonization(melody_midi)

            save_mp3(output_stream)
            return render_template(
                "generate.html",
                user=user,
                syllables=syllables,
                target_key=target_key,
                instrument=instrument,
                authenticated_user=current_user.is_authenticated,
            )

        except Exception as e:
            print(e)

    return render_template(
        "generate.html",
        user=user,
        authenticated_user=current_user.is_authenticated
    )


def save_picture(form_picture):
    """save the picture to static folder"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        application.root_path, "static/profile_pics", picture_fn
    )

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@application.errorhandler(401)
def re_route(e):
    """redirect to handle 401"""
    return redirect(url_for("login"))
