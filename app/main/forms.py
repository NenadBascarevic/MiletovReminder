from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_user = TextAreaField('About user', validators=[Length(min=0, max=200)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use different username!')


class ReminderForm(FlaskForm):
    reminder = TextAreaField('Reminder', validators=[Length(min=1, max=200)])
    submit = SubmitField('Add Reminder')


class UserDeactivationForm(FlaskForm):
    deactivate = BooleanField('Deactivate User')
    submit = SubmitField('Apply changes')