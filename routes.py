import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flask_mail import Message

from blog import app, db, bcrypt, mail
from blog.forms import RegistrationForm, LoginForm, UpdateAccountForm,RequestResetForm, ResetPasswordForm
from blog.models import User, Items, Itemscart, Count
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        user_id = current_user.id
        c = Count.query.filter_by(id=user_id).all()
        sum = 0
        for ch in c:
            sum = sum + ch.count
        return render_template('home.html', items=Items, Count=Count, sum=sum)
    else:
        return render_template('home.html',items=Items)


@app.route("/contactus")
def contactus():
    return render_template('contactus.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,address=form.address.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/pickup")
def pickup():
    return render_template('pickup.html')

@app.route("/confirmorder",methods=['GET', 'POST'])
def confirmorder():
    user_id = current_user.id
    c = Count.query.filter_by(id=user_id).all()
    price = 0
    for ch in c:
        iid = ch.item_id
        p = Items.query.filter_by(id=iid).first().price
        price = price + p * ch.count
    return render_template('confirmorder.html',Items=Items,Count=Count,sum=sum,price=price)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


# @app.route("/cart<id>", methods=['GET', 'POST'])
@app.route("/cart", methods=['GET', 'POST'])
@login_required
def cart():
    # c = Count.query.all()
    # sum = 0
    # for ch in c:
    #     sum = sum + ch.count
    user_id=current_user.id
    c = Count.query.filter_by(id=user_id).all()
    price= 0
    for ch in c:
        iid=ch.item_id
        p=Items.query.filter_by(id=iid).first().price
        price=price+p*ch.count
    return render_template('cart.html',Items=Items,Count=Count,sum=sum,price=price)


# @app.route("/add<pid>", methods=['GET', 'POST'])
# @login_required
# def cart_add(pid):
#     ct=Count.count
#     ct = ct + 1
#     item=Itemscart.query.filter_by(pid).first()
#     if item:
#         Count.id=pid
#         Count.count=ct
#         return render_template(url_for('home'))
#     else:
#         item = Itemscart(id=pid)
#         db.session.add(item)
#         db.session.commit()
#         flash('item has been added', 'success')
#         Count.count=ct
#         return render_template('home')
#
#     return render_template(url_for('home'))
#
# @app.route("/remove<id>", methods=['GET', 'POST'])
# @login_required
# def cart_remove(id):
#
#
#     return render_template(url_for('home'))


@app.route("/add<pid>", methods=['GET', 'POST'])
@login_required
def add(pid):
    userId = current_user.id
    item = Itemscart.query.filter_by(id=pid,user_id=userId).first()
    if item:
        count = Count.query.filter_by(item_id=pid).first()
        ct=count.count
        ct+=1
        count.count=ct
        db.session.commit()
        return redirect(url_for('home'))
    else:
        ct = 0
        item = Itemscart(id=pid, user_id=userId)
        db.session.add(item)
        db.session.commit()
        ct = ct + 1
        count = Count(id=userId,item_id=pid, count=ct)
        db.session.add(count)
        db.session.commit()
        return redirect(url_for('home'))


@app.route("/remove<pid>", methods=['GET', 'POST'])
@login_required
def remove(pid):
    itemscart=Itemscart.query.filter_by(id=pid).first()
    if itemscart:
        count=Count.query.filter_by(item_id=pid).first()
        if count.count>1:
            count.count=count.count-1
            db.session.commit()
            return redirect(url_for('home'))
        else:
            db.session.delete(count)
            db.session.commit()
            db.session.delete(itemscart)
            db.session.commit()
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)