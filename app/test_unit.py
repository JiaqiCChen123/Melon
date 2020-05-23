from app import classes


def test_user_Columns():
    """test the column names of the database"""
    assert [i.name for i in classes.User.__table__.columns] == [
        'id', 'username', 'email', 'password_hash', 'gender', 'age', 'city', 'image_file']

def test_profile_Columns():
    assert [
        i.name for i in classes.Profile.__table__.columns] == [
        'id',
        'User',
        'Gender',
        'Age',
        'City',
        'image_file']

def test_history_Columns():
    assert [i.name for i in classes.History.__table__.columns] == ['id', 'User', 'Filename']

# def test_profileform_Columns():
#     assert [i.name for i in classes.ProfileForm.__table__.columns] == ['Genders:', 'Age:',
#      'City:', "Update Profile Picture", "Submit"]


def test_UserFromUser():
    """test user login infomation"""
    # Assuming that "diane, diane@gmail.com≈, 1234" is always in the database
    # Good to have a test user account
    assert classes.User.query.filter_by(
        username='jiaqi').first().username == 'jiaqi'
    assert classes.User.query.filter_by(username='jiaqi').first().email == '123'
    assert classes.User.query.filter_by(
        username='jiaqi').first().check_password('123')


def test_UserFromProfile():
    """test user profile"""
    # Assuming that "diane, diane@gmail.com, 1234" is always in the database
    # Good to have a test user account
    assert classes.Profile.query.filter_by(
        username='jiaqi').first().username == 'jiaqi'
    assert classes.Profile.query.filter_by(username='jiaqi').first().age == 22
    assert classes.Profile.query.filter_by(
        username='jiaqi').first().gender == 'female'
    assert classes.Profile.query.filter_by(username='jiaqi').first().city == 'San Francisco'
