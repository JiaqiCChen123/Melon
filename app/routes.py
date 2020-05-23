from app import application, classes, db, search_lyrics
from app.Melon_Model.Melon.generate import *

import os
import boto3
import pickle
import secrets

from flask import Flask, flash, url_for, request
from flask import render_template, render_template_string, redirect, session, send_file
from flask_login import current_user, login_user, login_required, logout_user
from PIL import Image

from pydub import AudioSegment
from music21 import *
from datetime import datetime

s3_client = boto3.client(
    's3',
    aws_access_key_id='AKIAIPJCMOYQAROZYDUA',
    aws_secret_access_key='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'
)
#s3_client = boto3.client(
#    's3',
#    aws_access_key_id='AKIAI4DIIOCFHPBZQQBA',
#    aws_secret_access_key='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')
s3_bucket_name = 'melon-bucket-arthur'

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

@application.route("/instruction", methods=["GET", "POST"])
def instruction():
    return render_template('instruction.html')

@application.route("/recorder", methods=["GET", "POST"])
def recorder():
    return render_template('recorder.html')


@application.route("/player", methods=["GET", "POST"])
def player():
    return render_template('player.html')

@application.route("/combine", methods=["GET","POST"])
@login_required
def combine():
    if request.method== 'POST':
        try:
            sound1 = AudioSegment.from_file('./app/static/music/final_output.wav')
            recording = request.files.get('data')
            user_name = current_user.username
            print(user_name)
            if recording:
                if not os.path.exists('./app/static/music/tempfile'):
                    os.mkdir('./app/static/music/tempfile')
                f = open(f'./app/static/music/tempfile/temp_record_{user_name}.wav', 'wb')
                print(1)
                f.write(recording.read())
                f.close()
                print(2)
            sound2 = AudioSegment.from_file(f'./app/static/music/tempfile/temp_record_{user_name}.wav')
            print(3)
            combined = sound1.overlay(sound2)
            print(4)
            # now = datetime.now().strftime("%H%M%S")
            combined.export(f"./app/static/music/combined_{user_name}.wav", format='wav')
            print(5)
            combine_filename = f"./app/static/music/combined_{user_name}.wav"

            combine_filename = combine_filename[6:]
            print(6)
            print('type string', type(combine_filename))
            print(user_name, combine_filename)
            sentence_timestamp = session.get('sentence_timestamp', {'lyrics':[{'line':'', 'time': -1}]})
            print(sentence_timestamp)
            return render_template("generate.html",
                user_name=user_name,
                combine_filename=combine_filename,
                sentence_timestamp=sentence_timestamp)
        except:
            print('some error happend')
            sentence_timestamp = session.get('sentence_timestamp', {'lyrics':[{'line':'', 'time': -1}]})
        return render_template("generate.html",
                user_name=user_name,
                sentence_timestamp=sentence_timestamp)
    else:
        sentence_timestamp = session.get('sentence_timestamp', {'lyrics':[{'line':'', 'time': -1}]})
        return render_template("generate.html",
                user_name=user_name,
                sentence_timestamp=sentence_timestamp)

@application.route("/fetch_combined_recording")
def fetch_combined_recording():
    user_name = current_user.username
    music_path = os.path.join(application.root_path, "static/music/", f'combined_{user_name}.wav')
    return send_file(music_path, cache_timeout=1)

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


        num = classes.History.query.filter_by(username=username).count()
        melody_get = None


        print('user name', username)
        print('num of songs:', num)
        melody_list = []
        melody_filenames = []
        #num = 0
        if num > 0:
            for i in range(1, num+1):
                print(i)
                melody_key = username + str(i)

                print(melody_key)
                melody = s3_client.get_object(Bucket=s3_bucket_name, Key=melody_key)
                melody_body = melody['Body'].read()
                melody_get = pickle.loads(melody_body)
                melody_list.append(melody_get)


            for index, ms in enumerate(melody_list[-3:]):
                filename = str(username) + "_output_" + str(index)
                save_music(ms, filename)
                melody_filenames.append(filename)






            # print('type', melody_get)


        return render_template(
            "user.html",
            user=user,
            profile=profile,
            image_file=image_file,
            authenticated_user=current_user.is_authenticated,
            melody_filenames=melody_filenames[-3:]
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
    song_list = ['Old Town Road', 'Sunflower', 'Without Me', 'Bad Guy', 'Wow',
       'Happier', '7 Rings', 'Talk', 'Sicko Mode', 'Sucker', 'High Hopes',
       'Thank U, Next', 'Truth Hurts', 'Dancing with a Stranger',
       'Señorita', "I Don't Care", 'Eastside', 'Going Bad', 'Shallow',
       'Better', 'No Guidance', 'Girls Like You', 'Sweet but Psycho',
       'Suge', 'Middle Child', 'Drip Too Hard', 'Someone You Loved',
       'Ransom', "If I Can't Have You", 'Goodbyes', 'Zeze', 'Better Now',
       'Youngblood', 'Money in the Grave', 'Speechless',
       "Break Up with Your Girlfriend, I'm Bored", 'Please Me', 'Money',
       'You Need to Calm Down', 'Panini', 'Look Back at It', 'A Lot',
       'Me!', 'Mia', 'Pop Out', 'Beautiful Crazy', 'Thotiana',
       'Lucid Dreams', 'Mo Bamba', 'Beautiful People',
       'Wake Up in the Sky', 'Whiskey Glasses', "God's Country",
       'Be Alright', 'Pure Water', 'The Git Up', 'Taki Taki',
       'Close to Me', 'Envy Me', 'You Say', 'Hey Look Ma, I Made It',
       'Circles', 'Beer Never Broke My Heart', 'The London', 'Con Calma',
       'Murder on My Mind', "When the Party's Over", 'Act Up',
       'I Like It', 'Trampoline', 'Leave Me Alone', 'Breathin',
       'Bury a Friend', 'Close Friends', 'Baby Shark', 'My Type',
       'Worth It', 'Only Human', "Knockin' Boots", 'Trip', 'Rumor',
       'Swervin', 'How Do You Sleep?', 'Baby', 'Look What God Gave Her',
       'Good as You', 'Clout', 'Love Lies', 'One Thing Right',
       'Cash Shit', 'Tequila', 'Shotta Flow', 'Hot Girl Summer',
       'Talk You Out of It', 'Beautiful', 'Eyes on You', 'All to Myself',
       'Boyfriend', 'Walk Me Home', 'Robbery']
    author_list = ['Lil Nas X ', 'Post Malone and Swae Lee', 'Halsey',
       'Billie Eilish', 'Post Malone', 'Marshmello and Bastille',
       'Ariana Grande', 'Khalid', 'Travis Scott', 'Jonas Brothers',
       'Panic! at the Disco', 'Ariana Grande', 'Lizzo',
       'Sam Smith and Normani', 'Shawn Mendes and Camila Cabello',
       'Ed Sheeran and Justin Bieber', 'Benny Blanco, Halsey and Khalid',
       'Meek Mill ', 'Lady Gaga and Bradley Cooper', 'Khalid',
       'Chris Brown ', 'Maroon 5 ', 'Ava Max', 'DaBaby', 'J. Cole',
       'Lil Baby and Gunna', 'Lewis Capaldi', 'Lil Tecca', 'Shawn Mendes',
       'Post Malone ', 'Kodak Black ', 'Post Malone',
       '5 Seconds of Summer', 'Drake ', 'Dan + Shay', 'Ariana Grande',
       'Cardi B and Bruno Mars', 'Cardi B', 'Taylor Swift', 'Lil Nas X',
       'A Boogie wit da Hoodie', '21 Savage', 'Taylor Swift ',
       'Bad Bunny ', 'Polo G ', 'Luke Combs', 'Blueface', 'Juice Wrld',
       'Sheck Wes', 'Ed Sheeran ',
       'Gucci Mane, Bruno Mars and Kodak Black', 'Morgan Wallen',
       'Blake Shelton', 'Dean Lewis', 'Mustard and Migos', 'Blanco Brown',
       'DJ Snake ', 'Ellie Goulding and Diplo ', 'Calboy',
       'Lauren Daigle', 'Panic! at the Disco', 'Post Malone',
       'Luke Combs', 'Young Thug, J. Cole and Travis Scott',
       'Daddy Yankee and Katy Perry ', 'YNW Melly', 'Billie Eilish',
       'City Girls', 'Cardi B, Bad Bunny and J Balvin', 'Shaed',
       'Flipp Dinero', 'Ariana Grande', 'Billie Eilish', 'Lil Baby',
       'Pinkfong', 'Saweetie', 'YK Osiris', 'Jonas Brothers',
       'Luke Bryan', 'Ella Mai', 'Lee Brice', 'A Boogie wit da Hoodie ',
       'Sam Smith', 'Lil Baby and DaBaby', 'Thomas Rhett', 'Kane Brown',
       'Offset ', 'Khalid and Normani', 'Marshmello and Kane Brown',
       'Megan Thee Stallion ', 'Dan + Shay', 'NLE Choppa',
       'Megan Thee Stallion ', 'Florida Georgia Line', 'Bazzi ',
       'Chase Rice', 'Dan + Shay', 'Ariana Grande and Social House',
       'Pink', 'Juice Wrld']
    idxs = random.sample(range(len(song_list)),8)
    send_song = np.array(song_list)[idxs]
    send_author = np.array(author_list)[idxs]
    contents = tuple(zip(send_song,send_author))

    if current_user.is_authenticated:
        user = current_user
    else:
        user = "Anonymous"

    if request.method == 'POST':
        if request.form["submit"] == 'search':
            try:
                singer = request.form["singer"]
                song = request.form["song"]
                if singer and song:
                    lyrics = search_lyrics.get_lyrics(singer, song)
                if 'error' in lyrics:
                    flash('Cannnot find combination of "' + song + '" by "' + singer + '"')
                else:
                    return render_template(
                        "search.html",
                        user=user,
                        lyrics=lyrics,
                        singer=singer,
                        song=song,
                        authenticated_user=current_user.is_authenticated,
                        contents=contents
                    )
            except Exception as e:
                print(e)
            return render_template(
                "search.html",
                user=user,
                authenticated_user=current_user.is_authenticated,
                contents=contents
            )
        if request.form["submit"] == 'Confirm your lyrics':
            input_lyrics = request.form['input_lyrics']
            if not input_lyrics:
                flash('Please enter the lyrics you like')
            else:
                session['input_lyrics'] = input_lyrics
                flash('Successfully store the lyrics!')
            return render_template('search.html', user=user, authenticated_user=current_user.is_authenticated,
                    input_lyrics=input_lyrics, contents=contents)

    return render_template(
            "search.html",
            user=user,
            authenticated_user=current_user.is_authenticated, contents=contents)

@application.route("/generate", methods=["GET", "POST"])
def generate():
    if current_user.is_authenticated:
        user = current_user.username
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
            sentences = create_sentences(lyrics)
            ###
            melody_velocity = 100
            harmonization_velocity = 60
            ###
            try:
                target_key = request.form["key"]
                harm_instrument = request.form['instrument']
                bpm = int(request.form['BPM'])
                print(bpm) ##
                print(harm_instrument)
                melody_midi, syllable_timestamp, sentence_timestamp = create_melody(syll_model_path, word_model_path, model_path, syllables, sentences, bpm)
                output_stream = create_harmonization(melody_midi, target_key)
                # Add instrument in the model
            except Exception as e:
                target_key = "C"
                harm_instrument = 'Piano'
                melody_midi, syllable_timestamp, sentence_timestamp = create_melody(syll_model_path, word_model_path, model_path, syllables, sentences, bpm)
                output_stream = create_harmonization(melody_midi, target_key)
            output_stream = remix(output_stream, melody_velocity, harmonization_velocity, harm_instrument, bpm)

            output_stream.show('text')
            save_midi(output_stream)
            save_mp3(output_stream)

            print(lyrics)
            print(target_key)
            print(harm_instrument)

            username = current_user.username
            num = classes.History.query.filter_by(username=username).count()
            print(num)
            melody_key = username + str(num+1)
            print(melody_key)
            melody_binary = pickle.dumps(output_stream)
            history_new = classes.History(username,
                                          melody_key)
            db.session.add(history_new)
            db.session.commit()
            print('!')
            s3_client.put_object(Body=melody_binary, Bucket=s3_bucket_name, Key=melody_key)
            session['sentence_timestamp'] = sentence_timestamp
            print(session['sentence_timestamp'])
            print(harm_instrument)
            return render_template(
                "generate.html",
                user=user,
                syllables=syllables,
                target_key=target_key,
                instrument=harm_instrument,
                authenticated_user=current_user.is_authenticated,
                sentence_timestamp=sentence_timestamp
            )

        except Exception as e:
            print(e)

    return render_template(
        "generate.html",
        user=user,
        authenticated_user=current_user.is_authenticated
    )



def save_music(stream_object, music_filename):
    out_midi = stream_object.write('midi')
    # out_wav = str(Path(out_midi).with_suffix('.mp3'))
    out_wav = "./app/static/music/" + music_filename + ".wav"
    FluidSynth("./app/Melon_Model/data/soundfonts/FluidR3_GM.sf2").midi_to_audio(out_midi, out_wav)
    return out_wav


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

@application.route('/player_recorder', methods=["GET", "POST"])
def player_recorder(name=None):

    return render_template('player_recorder.html')


@application.errorhandler(401)
def re_route(e):
    """redirect to handle 401"""
    return redirect(url_for("login"))
