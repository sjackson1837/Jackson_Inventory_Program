from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os


#Create a Flask Instance
app = Flask(__name__)
ckeditor = CKEditor(app)

#export FLASK_APP = hello.py

#Add Database
###OLD SQLITE DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'

#NEW SQL DB
###app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ert33MNB@localhost/our_users'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vbmlkcjlnjxrdn:132102329d056425c4979290ad0b6ebab7074441ae8d9118b9f94cf40ee39811@ec2-34-202-127-5.compute-1.amazonaws.com:5432/d81j22oj9kp485'

#Secret Key
app.config['SECRET_KEY'] = "MY SUPER SECRET KEY NO ONE KNOWS"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#initialize the database
db = SQLAlchemy(app)

migrate = Migrate(app, db)
#app.app_context().push()

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

#Pass Stuff to Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

#Create Search Function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        #Get data from submitted form
        post.searched = form.searched.data
        # Query the Database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", form=form, searched=post.searched, posts = posts)


#Create Login Page
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successfull!!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!!!")
        else:
            flash("That User Doesn't Exist!  Try Again...")
    return render_template('login.html', form=form)

#Create Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!  Thanks For Stopping By...")
    return redirect(url_for('login'))


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:    
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            # Return a message
            flash("Blog Post Was Deleted!")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
        except:
            # Return error message
            flash("Whoops! There was a problem deleting the post!")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
            flash("You Aren't Authorized to Delete That Post!!")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)

@app.route('/posts')
@login_required
def posts():
    # Grab all of the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
@login_required
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        #post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been updated!")
        return redirect(url_for('post', id=post.id))
    
    if current_user.id == post.poster_id:
        form.title.data = post.title
        #form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You Aren't Authorized To Edit This Post")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)
    

# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content = form.content.data, poster_id = poster, slug = form.slug.data)
        # Clear the form
        form.title.data = ''
        form.content.data = ''
        #form.author.data = ''
        form.slug.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return Message
        flash("Blog Post Submitted Successfully!")

    # Redirect to the webpage
    return render_template("add_post.html", form=form)

# Json thing
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "John": "Pepperoni", 
        "Mary": "Cheese", 
        "Tim": "Mushroom"}
    return favorite_pizza
    #return {"Date": date.today()}

# #Create Model
class users(db.Model, UserMixin):
     id = db.Column(db.Integer, primary_key = True)
     username = db.Column(db.String(20), nullable=False, unique=True)
     name = db.Column(db.String(200), nullable=False)
     email = db.Column(db.String(120), nullable=False, unique=True)
     favorite_color = db.Column(db.String(120))
     about_author = db.Column(db.Text(), nullable=True)
     date_added = db.Column(db.DateTime, default=datetime.utcnow)
     profile_pic = db.Column(db.String(), nullable=True)
     #Do some password stuff!!!
     password_hash = db.Column(db.String(128))
     #User Can Have Many Posts
     posts = db.relationship('Posts', backref='poster')
    
     
     @property
     def password(self):
         raise AttributeError('password is not a readable attribute!!')
     
     @password.setter
     def password(self, password):
         self.password_hash = generate_password_hash(password)

     def verify_password(self, password):
         return check_password_hash(self.password_hash, password)
     
     #     #Create a string
     def __repr__(self):
         return '<Name %r>' % self.name


# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    #Foreign Key to Link Users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!")  
        our_users = users.query.order_by(users.date_added)
        return render_template("add_user.html", form = form, name=name, our_users = our_users)
    except:
        flash("Whoops!  There was a problem deleting user....try again")
        return render_template("add_user.html", form = form, name=name, our_users = our_users)



#update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", form=form, name_to_update = name_to_update)
        except:
            flash("Error!  Looks like there was a problem")
            return render_template("update.html", form=form, name_to_update = name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update = name_to_update, id = id)

#Create dashboard Page
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        name_to_update.profile_pic = request.files['profile_pic']
        # Grab Image Name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        # Set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        # Save that image
        saver = request.files['profile_pic']
        
        # Change it to a string to save to db
        name_to_update.profile_pic = pic_name
        try:
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER']), pic_name)
            flash("User Updated Successfully!")
            return render_template("dashboard.html", form=form, name_to_update = name_to_update)
        except:
            flash("Error!  Looks like there was a problem")
            return render_template("dashboard.html", form=form, name_to_update = name_to_update)
    else:
        return render_template("dashboard.html", form=form, name_to_update = name_to_update, id = id)
    return render_template('dashboard.html')

#def index():
#    return "<h1>Hello World!</h1>"

@app.route('/user_add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = users(username = form.username.data, name=form.name.data, email = form.email.data, favorite_color = form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.email.favorite_color = ''
        form.password_hash = ''
        flash("User Added!")

    our_users = users.query.order_by(users.date_added)
    return render_template("add_user.html", form = form, name=name, our_users = our_users)

#Create a route decorator
@app.route('/')
def index():
    first_name = "John"
    favorite_pizza = ['Pepperoni', 'Cheese', 'Mushrooms', 41]
    return render_template("index.html", first_name=first_name, favorite_pizza=favorite_pizza)

@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 15:
        return render_template("admin.html")
    else:
        flash("Sorry, you must be the admin to access the Admin Page!!!")
        return redirect(url_for('dashboard'))

# localhost:5000/user/John
@app.route('/user/<name>')

def user(name):
    return render_template("user.html", user_name=name)

#Create custom error pages

#invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

#Create password Test page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    #Validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        #Clear the form        
        form.email.data = ''
        form.password_hash.data = ''

        # Lookup User by 
        pw_to_check = users.query.filter_by(email=email).first()

        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)


        #flash("Form Submitted Successfully!")

    return render_template("test_pw.html", email = email, password = password, pw_to_check = pw_to_check, passed = passed, form=form)


#Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    #Validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!")

    return render_template("name.html", name = name, form = form)

if __name__ == "__main__":
# #    db.create_all()
    app.run(debug=True)
