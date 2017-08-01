from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'super_secret_key'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime)

    def __init__(self, title, body, owner_id, date=None):
        self.title = title
        self.body = body
        self.owner_id = owner_id
        if date is None:
            date = datetime.utcnow()
        self.date = date


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signUp', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/blog')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/signUp', methods=['POST', 'GET'])
def signUp():
    verify_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            if verify != password:
                flash('Passwords do not match', 'error')
            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()

                session['username'] = username
                return redirect('/blog')
        else:
            flash('Duplicate User', 'error')

    return render_template('signup.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')


@app.route('/')
def index():
    
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.args:
        blog_id = request.args.get("id")
        user_username = request.args.get("user")

        if blog_id:
            blog = Blog.query.get(blog_id)
            return render_template('singleBlogEntries.html', blog=blog)

        if user_username:
            user = User.query.filter_by(username=user_username).first()
            blogs = Blog.query.filter_by(owner_id=user.id).order_by(Blog.date.desc()).all()
            return render_template('mainBlogPage.html', blogs=blogs)

    blogs = Blog.query.order_by(Blog.date.desc()).all()
    return render_template('mainBlogPage.html', title="Build a Blog", blogs=blogs)


@app.route('/addBlogEntry', methods=['POST', 'GET'])
def addBlogEntry():
    title_error = ''
    blog_error = ''

    if request.method == 'POST':
        blog_name_title = request.form['blog_title']
        blog_name_body = request.form['blog_body']

        if len(blog_name_title) == 0:
            title_error = 'Please enter a title'
        elif len(blog_name_body) == 0:
            blog_error = 'Please write your blog'
        elif not title_error and not blog_error:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_name_title, blog_name_body, owner.id)
            db.session.add(new_blog)
            db.session.commit()

            return render_template('singleBlogEntries.html', blog=new_blog)

    return render_template('addBlogEntry.html', title_error=title_error, blog_error=blog_error)


if __name__ == '__main__':
    app.run()
