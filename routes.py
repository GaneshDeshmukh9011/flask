from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models import User, Post
from utils import admin_required

def register_routes(app):

    @app.route('/')
    def home():
        posts = Post.query.order_by(Post.date_posted.desc()).all()
        return render_template('home.html', posts=posts)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        if request.method == 'POST':
            username = request.form.get('username').strip()
            email = request.form.get('email').strip()
            password = request.form.get('password')
            if not username or not email or not password:
                flash('Please fill all fields', 'danger')
                return render_template('register.html')

            if User.query.filter((User.username==username) | (User.email==email)).first():
                flash('User with that username/email already exists', 'danger')
                return render_template('register.html')

            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(username=username, email=email, password=pw_hash)
            db.session.add(user)
            db.session.commit()
            flash('Account created! Please login.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        if request.method == 'POST':
            email = request.form.get('email').strip()
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                flash('Successfully logged in', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('home'))
            flash('Invalid credentials', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/create', methods=['GET', 'POST'])
    @login_required
    def create_post():
        if request.method == 'POST':
            title = request.form.get('title').strip()
            content = request.form.get('content').strip()
            if not title or not content:
                flash('Title and content required', 'danger')
                return render_template('create_post.html')
            post = Post(title=title, content=content, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Post created', 'success')
            return redirect(url_for('home'))
        return render_template('create_post.html')

    @app.route('/post/<int:post_id>')
    def single_post(post_id):
        post = Post.query.get_or_404(post_id)
        return render_template('single_post.html', post=post)

    @app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_post(post_id):
        post = Post.query.get_or_404(post_id)
        if post.author != current_user and not current_user.is_admin:
            abort(403)
        if request.method == 'POST':
            title = request.form.get('title').strip()
            content = request.form.get('content').strip()
            if not title or not content:
                flash('Title and content required', 'danger')
                return render_template('edit_post.html', post=post)
            post.title = title
            post.content = content
            db.session.commit()
            flash('Post updated', 'success')
            return redirect(url_for('single_post', post_id=post.id))
        return render_template('edit_post.html', post=post)

    @app.route('/post/<int:post_id>/delete', methods=['POST'])
    @login_required
    def delete_post(post_id):
        post = Post.query.get_or_404(post_id)
        if post.author != current_user and not current_user.is_admin:
            abort(403)
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', 'success')
        return redirect(url_for('home'))

    @app.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        users = User.query.order_by(User.id.asc()).all()
        posts = Post.query.order_by(Post.date_posted.desc()).all()
        return render_template('admin/dashboard.html', users=users, posts=posts)

    @app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
    @login_required
    @admin_required
    def admin_delete_user(user_id):
        user = User.query.get_or_404(user_id)
        if user.is_admin:
            flash('Cannot delete another admin', 'danger')
            return redirect(url_for('admin_dashboard'))
        db.session.delete(user)
        db.session.commit()
        flash('User deleted', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/delete_post/<int:post_id>', methods=['POST'])
    @login_required
    @admin_required
    def admin_delete_post(post_id):
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/make_admin/<int:user_id>', methods=['POST'])
    @login_required
    @admin_required
    def admin_make_admin(user_id):
        user = User.query.get_or_404(user_id)
        user.is_admin = True
        db.session.commit()
        flash('User promoted to admin', 'success')
        return redirect(url_for('admin_dashboard'))
