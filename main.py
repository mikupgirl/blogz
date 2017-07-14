from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] =  True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    submitted = db.Column(db.Boolean)
    owner_id =  db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.submitted = False
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():

    allowed_routes = ['login', 'signUp', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():

    username_error = ''
    password_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if len(username) == 0:
            username_error = 'Please enter your username'

        if len(password) == 0:
            password_error = 'Please enter your password'
        
        if not username_error and not password_error:
            session['username'] = username
            flash("Logged in")
            return redirect('/blog')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            
    return render_template('login.html', username_error=username_error, password_error=password_error)

@app.route('/signUp', methods=['POST', 'GET'])
def signUp():

    username_error = ''
    password_error = ''
    verify_error = ''    

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) == 0 or len(username) < 3:
            username_error = 'Invalid Username'

        if len(password) == 0 or len(password) < 3:
            password_error = 'Invalid Password'

        if str(verify) != str(password):
            verify_error = 'Passwords do not match.'
        
        existing_user = User.query.filter_by(username=username).first()

        if not username_error and not password_error and not verify_error:
        
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog')
        else:
            if existing_user:
                flash('Duplicate User', 'error')

    return render_template('signup.html', verify_error=verify_error, password_error=password_error, username_error=username_error)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')


@app.route('/', methods=['POST','GET'])
def index():

    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blogs = Blog.query.filter_by(submitted=False).all()
    return render_template('mainBlogPage.html',title="Build a Blog", blogs=blogs)

@app.route('/addBlogEntry', methods=['POST', 'GET'])
def addBlogEntry():
    
    title_error = ''
    blog_error = ''
    blog_title = ''
    blog_body = ''

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_name_title = request.form['blog_title']
        blog_name_body = request.form['blog_body']

        if len(blog_name_title) == 0:
            title_error = 'Please enter a title'

        if len(blog_name_body) == 0:
            blog_error = 'Please write your blog'

        if not title_error and not blog_error:
            new_blog = Blog(blog_name_title, blog_name_body, owner)
            db.session.add(new_blog)
            db.session.commit()     
           
            return render_template('singleBlogEntries.html', blog=new_blog, owner=owner)   
    
    blogs = Blog.query.filter_by(completed=False,owner=owner).all()
    return render_template('addBlogEntry.html', title_error=title_error, blog_error=blog_error, owner=owner, blogs=blogs)


@app.route('/singleBlogs')
def singleBlogs():
    
    blog_id = request.args.get("id")       
    blog = Blog.query.get(blog_id)
    return render_template('singleBlogEntries.html', blog=blog)


if __name__ == '__main__':
    app.run()

