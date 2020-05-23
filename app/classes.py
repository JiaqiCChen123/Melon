import boto3
from flask_login import UserMixin
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import (
    DateField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, InputRequired

from app import db, login_manager

client = boto3.client(
    's3',
    aws_access_key_id='AKIAIV6CI3ZCHLNH3Q5Q',
    aws_secret_access_key='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'
)


class User(db.Model, UserMixin):
    """create User table with username, email and password_hash"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(80), nullable=True, default="None")
    age = db.Column(db.Integer, nullable=True, default="0")
    city = db.Column(db.String(80), nullable=True, default="None")
    image_file = db.Column(
        db.String(20),
        nullable=False,
        default="melon_pro.jpg"
    )

    def __init__(
        self,
        username,
        email,
        password,
        image_file,
        gender,
        age,
        city
    ):
        """init user"""
        self.username = username
        self.email = email
        self.set_password(password)
        self.image_file = image_file
        self.gender = gender
        self.age = age
        self.city = city

    def set_password(self, password):
        """set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """check password"""
        return check_password_hash(self.password_hash, password)


class Profile(db.Model):
    """create profile table"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column("User", db.String, nullable=False)
    gender = db.Column("Gender", db.String, nullable=True)
    age = db.Column("Age", db.Integer, nullable=True)
    city = db.Column("City", db.String, nullable=True)
    image_file = db.Column("image_file", db.String, nullable=False)

    def __init__(self, username, gender, age, city, image_file):
        """init profile"""
        self.username = username
        self.gender = gender
        self.age = age
        self.city = city
        self.image_file = image_file


class RegistrationForm(FlaskForm):
    """create registration form"""

    username = StringField(
        "Username:",
        validators=[DataRequired()],
        render_kw={"placeholder": "username"}
    )
    email = StringField(
        "Email:",
        validators=[DataRequired()],
        render_kw={"placeholder": "email"}
    )
    password = PasswordField(
        "Password:",
        validators=[DataRequired()],
        render_kw={"placeholder": "password"}
    )
    image_file = FileField(
        "Update Profile Picture",
        validators=[FileAllowed(["jpg", "png"])]
    )
    gender = StringField("Gender:", validators=[])
    age = IntegerField("Age:", validators=[])
    city = StringField("City:", validators=[])
    submit = SubmitField("Submit")


class LogInForm(FlaskForm):
    """create login form"""

    username = StringField(
        "Username:",
        validators=[DataRequired()],
        render_kw={"placeholder": "username"}
    )
    password = PasswordField(
        "Password:",
        validators=[DataRequired()],
        render_kw={"placeholder": "password"}
    )
    submit = SubmitField("Login")


class ProfileForm(FlaskForm):
    """create profile form"""

    gender = StringField("Gender:", validators=[DataRequired()])
    age = IntegerField("Age:", validators=[DataRequired()])
    city = StringField("City:", validators=[DataRequired()])
    image_file = FileField(
        "Update Profile Picture",
        validators=[FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Submit")

class History(db.Model):
    """create melody history table"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column("User", db.String, nullable=False)
    melodyname = db.Column("Filename", db.String, nullable=True)

    def __init__(self, username, melodyname):
        """init profile"""
        self.username = username
        self.melodyname = melodyname

@login_manager.user_loader
def load_user(id):
    """get user id"""
    return User.query.get(int(id))


db.create_all()
db.session.commit()
