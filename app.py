from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user 
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tubes'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful! Welcome, {}!'.format(username), 'success')  # Success message
            return redirect(url_for('index'))  # Redirect to the students page
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')  # Logout message
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}! This is your dashboard.'

@app.route('/students', methods=['GET'])
@login_required
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

@app.route('/')
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
@login_required
def add_student():
    # name = request.form['name']
    # age = request.form['age']
    # grade = request.form['grade']
    

    # connection = sqlite3.connect('instance/students.db')
    # cursor = connection.cursor()

    # # RAW Query
    # # db.session.execute(
    # #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    # #     {'name': name, 'age': age, 'grade': grade}
    # # )
    # # db.session.commit()
    # query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    # cursor.execute(query)
    # connection.commit()
    # connection.close()
    # return redirect(url_for('index'))
    if current_user.username != "akuhakam":
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('index'))

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    new_student = Student(name=name, age=age, grade=grade)
    db.session.add(new_student)
    db.session.commit()
    flash('Student added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<string:id>') 
def delete_student(id):
    if current_user.username != "akuhakam":
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('index'))
    # RAW Query
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return redirect(url_for('index'))

    # student = Student.query.get(id)
    # db.session.delete(student)
    # db.session.commit()
    # flash('Student deleted successfully!', 'success')
    # return redirect(url_for('students'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):

    if current_user.username != "akuhakam":
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        # RAW Query
        db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)
    

    # if request.method == 'POST':
    #     name = request.form['name']
    #     age = request.form['age']
    #     grade = request.form['grade']
        
    #     # student = Student.query.get(id)
    #     student.name = name
    #     student.age = age
    #     student.grade = grade
    #     db.session.commit()
    #     flash('Student updated successfully!', 'success')
    #     return redirect(url_for('students'))
    # else:
    #     # student = Student.query.get(id)
    #     student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
    #     return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

