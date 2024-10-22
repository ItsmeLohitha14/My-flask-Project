from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates")
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'lohi@14'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'todo_app'

mysql = MySQL(app)

todos = [{"todo": "Sample Todo", "done": False}]

@app.route("/")
def index():
    if 'username' in session:
        return render_template("index.html", todos=todos, username=session['username'])
    return redirect(url_for('login'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cursor.close()
        session['success'] = "Registration successful! You can now log in."
        return redirect(url_for('login'))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    user_not_found = False  # Variable to indicate user not found
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[2], password):
            session['username'] = user[1]
            return redirect(url_for('index'))
        else:
            user_not_found = True  # Set to True if user not found

    # Check if there is a success message from registration
    success_message = None
    if 'success' in session:
        success_message = session['success']
        session.pop('success')  # Clear the message after displaying it

    return render_template("login.html", user_not_found=user_not_found, success_message=success_message)



@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/add", methods=["POST"])
def add():
    if 'username' in session:
        todo = request.form['todo']
        todos.append({"todo": todo, "done": False})
        return redirect(url_for("index"))
    return redirect(url_for('login'))

@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):
    if 'username' in session:
        todo = todos[index]
        if request.method == "POST":
            todo['todo'] = request.form['todo']
            return redirect(url_for("index"))
        else:
            return render_template("edit.html", todo=todo, index=index)
    return redirect(url_for('login'))

@app.route("/check/<int:index>", methods=["POST"])
def check(index):
    if 'username' in session:
        todos[index]['done'] = not todos[index]['done']
        return redirect(url_for("index"))
    return redirect(url_for('login'))

@app.route("/delete/<int:index>", methods=["POST"])
def delete(index):
    if 'username' in session:
        del todos[index]
        return redirect(url_for("index"))
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
