from flask import Flask, render_template, request, redirect, session, flash, \
    url_for, jsonify
from functools import wraps
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask-app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


# Login
@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    status = True
    if request.method == 'POST':
        username= request.form["username"]
        password = request.form["password"]
        cur = mysql.connection.cursor()
        cur.execute("select * from users where USERNAME=%s and PASSWORD=%s",(username, password))
        data = cur.fetchone()
        if data:
            session['logged_in'] = True
            session['name'] = data["NAME"]
            flash('Login Successfully', 'success')
            return redirect('home')
        else:
            flash('Invalid Login. Try Again', 'danger')
    return render_template("login.html")


# check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login', 'danger')
            return redirect(url_for('login'))

    return wrap


# Registration
@app.route('/reg', methods=['POST', 'GET'])
def reg():
    status = False
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        username = request.form["username"]
        password = request.form["password"]
        cur = mysql.connection.cursor()
        cur.execute("insert into users(NAME,EMAIL,MOBILE,USERNAME,PASSWORD)"
                    "values(%s,%s,%s,%s,%s)",
                    (name, email,mobile,username, password))
        mysql.connection.commit()
        cur.close()
        flash('Registration Successfully. Login Here...', 'success')
        return redirect('login')
    return render_template("reg.html", status=status)


# Home page
@app.route("/home")
@is_logged_in
def home():
    return render_template('home.html')


# logout
@app.route("/logout")
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# create post
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    status = False
    if request.method == 'POST':
        title = request.form["title"]
        description = request.form["description"]
        tags = request.form["tags"]
        date = request.form["date"]
        cur = mysql.connection.cursor()
        cur.execute("insert into posts(TITLE,DESCRIPTION,TAGS,DATE)"
                    "values(%s,%s,%s,%s)",
                    (title, description,tags,date))
        mysql.connection.commit()
        cur.close()
        flash('Post Created Successfully.', 'success')
        return redirect(url_for("posts", title=title))

    return render_template("blog.html", status=status)


@app.route('/posts', methods=['POST', 'GET'])
def posts():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM posts")
    
    return render_template("postlist.html")




if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
