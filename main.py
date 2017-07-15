from flask import Flask, request, redirect, render_template, session, flash
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
        
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/blog')
        else:
            flash('User password incorrect, or user does not exist', 'error')

            
    return render_template('login.html')

@app.route('/signUp', methods=['POST', 'GET'])
def signUp():

    username_error = ''
    password_error = ''
    verify_error = ''    

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #if len(username) == 0 or len(username) < 3:
            #username_error = 'Invalid Username'

        #if len(password) == 0 or len(password) < 3:
            #password_error = 'Invalid Password'

        #if str(verify) != str(password):
            #verify_error = 'Passwords do not match.'
        
        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
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


@app.route('/', methods=['POST','GET'])
def index():

    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    #change the get arguments below to fit with the user class, and replace users=users with the blog=blog value, which you'll change   
    #user_Id = request.args.get("id") #gets the id from the url, which has the key val pair id and the number. when the url is input, you are routed to singleblogs
    #user = User.query.get(user_Id) #calls the query method on User to get the user associated with that id

    blogs = Blog.query.filter_by(submitted=False).all()
    user = User.query.all()
    return render_template('mainBlogPage.html',title="Build a Blog", blogs=blogs, user=user) # passes user as a param making it available to the html file

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
    
    blogs = Blog.query.filter_by(submitted=False,owner=owner).all()
    return render_template('addBlogEntry.html', title_error=title_error, blog_error=blog_error, owner=owner, blogs=blogs)


@app.route('/singleBlogs')
def singleBlogs():
    
    blog_id = request.args.get("id")       
    blog = Blog.query.get(blog_id)
    return render_template('singleBlogEntries.html', blog=blog)


if __name__ == '__main__':
    app.run()

