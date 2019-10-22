from app import db
from app.main import bp
from flask import request, current_app, render_template, url_for, redirect, flash
from app.main.forms import EditProfileForm, ReminderForm, UserDeactivationForm
from app.models import User, Reminder
from flask_jwt_extended import jwt_required

from flask_login import current_user
from werkzeug.utils import secure_filename
import os


@bp.route('/')
def start_page():
    return render_template('start_page.html')


@bp.route('/homepage', methods=['GET', 'POST'])
@jwt_required
def homepage():
    form = ReminderForm()
    if form.validate_on_submit():
        reminder = Reminder(text=form.reminder.data, creator=current_user)
        db.session.add(reminder)
        db.session.commit()
        flash('Successfully added new reminder!')
        return redirect(url_for('main.homepage'))
    page = request.args.get('page', 1, type=int)
    reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.timestamp.desc()).paginate(
                page, current_app.config['REMINDERS_PER_PAGE'], False)
    next_url = url_for('main.homepage', page=reminders.next_num) \
        if reminders.has_next else None
    prev_url = url_for('main.homepage', page=reminders.prev_num) \
        if reminders.has_prev else None
    return render_template('homepage.html', title='Home', form=form, reminders=reminders.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>', methods=['GET', 'POST'])
@jwt_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = UserDeactivationForm()
    if form.validate_on_submit():
        if form.deactivate.data :
            user.deactivate()
        else:
            user.activate()
        return redirect(url_for('main.users'))
    page = request.args.get('page', 1, type=int)
    reminders = user.reminder.order_by(Reminder.timestamp.desc()).paginate(
                page, current_app.config['REMINDERS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=reminders.next_num) \
        if reminders.has_next else None
    prev_url = url_for('main.user', username=user.username, page=reminders.prev_num) \
        if reminders.has_prev else None
    return render_template('user.html', user=user, reminders=reminders.items, form=form,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>/upload_photo', methods=['GET', 'POST'])
@jwt_required
def upload_photo(username):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and User.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            user = User.query.filter_by(username=username).first_or_404()
            user.save_profile_photo(filename)
            return redirect(url_for('main.edit_profile'))
    return render_template('upload_photo.html')


@bp.route('/users')
@jwt_required
def users():
    users = User.query.order_by(User.username.asc()).all()
    if current_user.admin:
        return render_template('users.html', users=users)
    return redirect(url_for('main.homepage'))


@bp.route('/homepage/edit_reminder/<id>', methods=['GET', 'PUT'])
@jwt_required
def edit_reminder(id):
    form = ReminderForm()
    if form.validate_on_submit():
        current_user.reminder.filter_by(id=id).first().text = form.reminder.data
        db.session.commit()
        flash('Successfully updated reminder!')
        return redirect(url_for('main.homepage'))
    elif request.method == 'GET':
        form.reminder.data = current_user.reminder.filter_by(id=id).first().text
    return render_template('reminder.html', form=form)


@bp.route('/homepage/delete_reminder/<id>', methods=['GET', 'DELETE'])
@jwt_required
def delete_reminder(id):
    reminder = current_user.reminder.filter_by(id=id).first()
    if reminder is None:
        flash('Reminder doesnt exist or deleted')
        return redirect(url_for('main.homepage'))
    db.session.delete(reminder)
    db.session.commit()
    flash('Successfully deleted reminder!')
    return redirect(url_for('main.homepage'))


@bp.route('/homepage/archive_reminder/<id>', methods=['GET', 'PUT'])
@jwt_required
def archive_reminder(id):
    reminder = current_user.reminder.filter_by(id=id).first()
    if reminder.archived:
        flash('Reminder already archived.')
        return redirect(url_for('main.homepage'))
    reminder.archived = True
    db.session.commit()
    return redirect(url_for('main.homepage'))


@bp.route('/edit_profile', methods=['GET', 'POST'])
@jwt_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.user_info = form.about_user.data
        db.session.commit()
        flash('Succesfully updated')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_user.data = current_user.user_info
    return render_template('edit_profile.html', title='Edit Profile', form=form)
