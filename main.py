from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))

    def __init__(self, title, body):
        self.title = title
        self.body = body
    
#    def __repr__(self):
#        return '<Blog %r>' % self.title % self.body



@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'POST':
        title = request.form['blog-title']
        body = request.form['blog-body']
        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()


    if request.method == "GET":
        if not request.args:
            posts = Blog.query.all()
            return render_template('blogs.html',title="Blog Posts", posts=posts)
        if request.args:
            blog_id = request.args.get('id')
            posts = Blog.query.filter_by(id=blog_id).all()
            return render_template('blog_post.html',title="Blog Entry", posts=posts)
            


    

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['blog-title']
        body = request.form['blog-body']
        if len(title)==0:
            title_error="Please fill in the title"
            return render_template("newpost.html", title_error=title_error)
        if len(body)==0:
            body_error="Please fill in the blog text"
            return render_template("newpost.html", body_error=body_error)
        else:
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            return redirect("/blog")

    posts = Blog.query.all()
    return render_template('newpost.html',title="Add a Blog Post", 
        posts=posts)




if __name__ == '__main__':
    app.run()