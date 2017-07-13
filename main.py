from flask import Flask, request, redirect, render_template, session, flash#can use bcrypt instead of hashlib
from flask_sqlalchemy import SQLAlchemy

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
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/', methods=['GET'])
def index():

    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'POST':
        blog_name_title = request.form['blog_title']
        blog_name_body = request.form['blog_body']        
        new_blog = Blog(blog_name_title, blog_name_body)        
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.filter_by(submitted=False).all()
    return render_template('mainBlogPage.html',title="Build a Blog", blogs=blogs)

@app.route('/addBlogEntry', methods=['POST', 'GET'])
def addBlogEntry():
    
    title_error = ''
    blog_error = ''
    blog_title = ''
    blog_body = ''

    if request.method == 'POST':
        blog_name_title = request.form['blog_title']
        blog_name_body = request.form['blog_body']
        #blog_name_owner = request.form['blog_owner'] - create this in addBlogEntry
        if len(blog_name_title) == 0:
            title_error = 'Please enter a title'

        if len(blog_name_body) == 0:
            blog_error = 'Please write your blog'

        if not title_error and not blog_error:
            new_blog = Blog(blog_name_title, blog_name_body, blog_name_owner)#blog_name_owner not connected to form on main.py or html yet
            db.session.add(new_blog)
            db.session.commit()     
           
            return render_template('singleBlogEntries.html', blog=new_blog)   

    return render_template('addBlogEntry.html', title_error=title_error, blog_error=blog_error)


@app.route('/singleBlogs')
def singleBlogs():
    
    blog_id = request.args.get("id")       
    blog = Blog.query.get(blog_id)
    return render_template('singleBlogEntries.html', blog=blog)

if __name__ == '__main__':
    app.run()

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            
    return render_template('login.html')

@app.route('/signUp')
def signUp():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            
            return "<h1>Duplicate User</h1>"

    return render_template('signup.html')

