from app.auth import bp
from app import jwt
from flask import make_response, render_template, url_for, redirect, flash, jsonify
from app.auth.forms import SignInForm, RegisterForm
from app.models import User
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    jwt_refresh_token_required, get_jwt_identity, get_raw_jwt,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies
    )
from flask_login import current_user, login_user, logout_user


@bp.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        if current_user.admin:
            return redirect(url_for('main.users'))
        else:
            return redirect(url_for('main.homepage'))
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Invalid username or password.')
            return redirect(url_for('auth.signin'))
        elif not user.active:
            flash('User account "{}" is deactivated. Please contact Administrator'.format(user.username))
            return redirect(url_for('auth.signin'))
        if user.check_password(form.password.data):
            access_token = create_access_token(identity=form.username.data)
            refresh_token = create_refresh_token(identity=form.username.data)
            login_user(user)
            if current_user.admin:
                resp = make_response(redirect(url_for('main.users')))
            else:
                resp = make_response(redirect(url_for('main.homepage')))
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            return resp
        else:
            return {'message': 'Wrong credentials'}
    return render_template('auth/signin.html', title='Sign In', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.admin:
            return redirect(url_for('main.users'))
        else:
            return redirect(url_for('main.homepage'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already in use, please choose another')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already in use')
            return redirect(url_for('auth.register'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.save_to_db()
        return redirect(url_for('auth.signin'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/refresh_token')
@jwt_refresh_token_required
def refresh_token():
    user = get_jwt_identity()
    access_token = create_access_token(identity=user)
    resp = make_response(redirect(url_for('main.homepage')))
    set_access_cookies(resp, access_token)
    if access_token:
        flash('Token successfully updated')
    return resp


@bp.route('/signout')
@jwt_required
def signout():
    resp = make_response(redirect(url_for('auth.signin')))
    unset_jwt_cookies(resp)
    logout_user()
    return resp


@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    resp = make_response(redirect(url_for('main.start_page')))
    unset_jwt_cookies(resp)
    logout_user()
    return resp
