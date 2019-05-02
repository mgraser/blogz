from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '18ysk37'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(24))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username=username
        self.password=password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
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
            return redirect('/newpost')
        if not user:
            user_error = "This username does not exist"
            return render_template("login.html", user_error=user_error)
        if user.password != password:
            user_pwd_error= "password incorrect"
            return render_template("login.html", user_pwd_error=user_pwd_error)
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if not username.isalnum() or len(username)<3 or len(username)>20:
            nameerror = "Please enter a valid username"
            return render_template("signup.html", nameerror=nameerror)
        if not password.isalnum() or len(password)<3 or len(password)>20:
            passworderror = "Please enter a valid password"
            return render_template("signup.html", username=username, pwderror=passworderror)
        if password != verify:
            verify_pwd_error = "Those passwords don't match"
            return render_template("signup.html", username=username, verify_pwd_error=verify_pwd_error)
     

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            nameerror = "Username exists"
            return render_template("signup.html", nameerror=nameerror)

        

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'POST':
        title = request.form['blog-title']
        body = request.form['blog-body']
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        blog_id = Blog.query.get(id)


    if request.method == "GET":
        if not request.args:
            posts = Blog.query.all()
            return render_template('blogs.html',title="Blog Posts", posts=posts)
        if request.args.get('user'):
            user = request.args.get('user')
            user_posts = Blog.query.filter_by(owner_id=user).all()
            return render_template('singleUser.html', user_posts=user_posts)

        else:
            blog_id = request.args.get('id')
            posts = Blog.query.filter_by(id=blog_id).first()
            return render_template('blog_post.html',title="Blog Entry", post=posts)
            


    

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['blog-title']
        body = request.form['blog-body']
        owner = User.query.filter_by(username=session['username']).first()

        if len(body)==0 and len(title)==0:
            title_error="Please fill in the title"
            body_error="Please fill in the blog text"
            return render_template("newpost.html", title_error=title_error, body_error=body_error)
        if len(title)==0:
            title_error="Please fill in the title"
            return render_template("newpost.html", title_error=title_error)
        if len(body)==0:
            body_error="Please fill in the blog text"
            return render_template("newpost.html", body_error=body_error)
        
        else:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            #new_blog = Blog.query.filter_by(id=new_post.id).first()
            return render_template('blog_post.html', post=new_post)
    else:
        #posts = Blog.query.all()
        return render_template('newpost.html',title="Add a Blog Post")

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)



if __name__ == '__main__':
    app.run()