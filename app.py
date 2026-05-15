import time, io, csv, random, json 
from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), default='student')
class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), default="General")
    password = db.Column(db.String(50), default="1234")
    questions = db.relationship('Question', backref='exam', lazy=True)
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
    text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

class ExamResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    exam_title = db.Column(db.String(200), nullable=False, default="General") 
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.String(100), nullable=False)
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', password='21058452', role='admin')
        db.session.add(admin_user)
        db.session.commit()

@app.route('/')
def index():
    return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username')
        pword = request.form.get('password')
        user = User.query.filter_by(username=uname, password=pword).first()
        if user:
            session['user'] = user.username
            session['role'] = user.role
            return redirect(url_for('admin_panel' if user.role == 'admin' else 'dashboard'))
        return "<h1>incorrect password and username!</h1><a href='/login'>exit</a>"
    return render_template('login.html')
@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    all_exams = Exam.query.all()
    return render_template('dashboard.html', user=session['user'], exams=all_exams)
@app.route('/admin')
def admin_panel():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    return render_template('admin.html', 
                           results=ExamResult.query.all(), 
                           questions=Question.query.all(), 
                           all_users=User.query.all(),
                           exams=Exam.query.all())
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    current_user = session['user']
    user_results = ExamResult.query.filter_by(username=current_user).order_by(ExamResult.id.desc()).all()
    
    return render_template('profile.html', user=current_user, results=user_results)

@app.route('/add_exam', methods=['POST'])
def add_exam():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    new_exam = Exam(
        title=request.form.get('title'),
        category=request.form.get('category'),
        password=request.form.get('password')
    )
    db.session.add(new_exam)
    db.session.commit()
    return redirect(url_for('admin_panel'))
@app.route('/add_question', methods=['POST'])
def add_question():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    new_q = Question(
        exam_id=request.form.get('exam_id'),
        text=request.form.get('text'),
        option_a=request.form.get('a'),
        option_b=request.form.get('b'),
        option_c=request.form.get('c'),
        option_d=request.form.get('d'),
        correct_answer=request.form.get('correct')
    )
    db.session.add(new_q)
    db.session.commit()
    return redirect(url_for('admin_panel'))
@app.route('/course/<int:exam_id>')
def course_detail(exam_id):
    if 'user' not in session: return redirect(url_for('login'))
    exam = Exam.query.get_or_404(exam_id)
    return render_template('course.html',user=session['user'], exam=exam)
@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    exam_id = request.form.get('exam_id')
    exam = Exam.query.get(exam_id)
    input_pass = request.form.get('quiz_password')

    if exam and input_pass == exam.password:
        session['current_exam_id'] = exam_id
        session['answers'] = {}
        session['start_time'] = time.time()
        
       
        questions = Question.query.filter_by(exam_id=exam_id).all()
        if not questions:
            return "<h1>this question has not been prepared for this exam!</h1><a href='/dashboard'>back</a>"
        q_ids = [q.id for q in questions]
        random.shuffle(q_ids) 
        session['shuffled_q_ids'] = q_ids
        
        return redirect(url_for('quiz', q_id=q_ids[0]))
    
    return "<h1>incorrect exam password!</h1><a href='/dashboard'>back</a>"

@app.route('/quiz/<int:q_id>', methods=['GET', 'POST'])
def quiz(q_id):
    if 'user' not in session: return redirect(url_for('login'))
    
    question = Question.query.get_or_404(q_id)
    shuffled_ids = session.get('shuffled_q_ids', [])
    answers = session.get('answers', {}) 
    
    if request.method == 'POST':
        ans = request.form.get('answer')
        answers[str(q_id)] = ans
        session['answers'] = answers
        
        try:
            current_index = shuffled_ids.index(q_id)
            next_index = current_index + 1
            if next_index < len(shuffled_ids):
                next_q_id = shuffled_ids[next_index]
                return redirect(url_for('quiz', q_id=next_q_id))
            else:
                return redirect(url_for('summary'))
        except ValueError:
            return redirect(url_for('summary'))
    
    time_left = max(0, int(600 - (time.time() - session.get('start_time', time.time()))))
    
    answered_ids = list(answers.keys()) 
    
    return render_template('quiz.html', 
                           question=question, 
                           shuffled_ids=shuffled_ids, 
                           time_left=time_left, 
                           answered_ids=answered_ids) 
@app.route('/summary')
def summary():
    exam_id = session.get('current_exam_id')
    all_qs = Question.query.filter_by(exam_id=exam_id).all()
    answered_ids = [int(k) for k in session.get('answers', {}).keys()]
    return render_template('summary.html', all_questions=all_qs, answered_ids=answered_ids)
@app.route('/add_student', methods=['POST'])
def add_student():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    uname = request.form.get('username')
    pword = request.form.get('password')
    if not User.query.filter_by(username=uname).first():
        db.session.add(User(username=uname, password=pword, role='student'))
        db.session.commit()
    return redirect(url_for('admin_panel'))
@app.route('/export_results')
def export_results():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student', 'Score', 'Total', 'Date'])
    for res in ExamResult.query.all():
        writer.writerow([res.username, res.score, res.total, res.date_taken])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=results.csv"})


@app.route('/finish_quiz', methods=['POST'])
def finish_quiz():
    exam_id = session.get('current_exam_id')
    exam = Exam.query.get(exam_id)
    answers = session.get('answers', {})
    
    flagged_data = request.form.get('flagged_list', '[]')
    try:
        flagged_ids = json.loads(flagged_data) 
    except:
        flagged_ids = []
    
    score = 0
    questions = Question.query.filter_by(exam_id=exam_id).all()
    
    for q in questions:
        if q.id in flagged_ids:
            continue 
            
        
        if answers.get(str(q.id)) == q.correct_answer:
            score += 1
   
    new_result = ExamResult(
        username=session['user'], 
        exam_title=exam.title, 
        score=score, 
        total=len(questions), 
        date_taken=time.strftime("%Y-%m-%d %H:%M")
    )
    db.session.add(new_result)
    db.session.commit()
    return render_template('result.html', score=score, total=len(questions))

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    exam_id = request.form.get('exam_id')
    file = request.files['file']
    
    if not file or not file.filename.endswith('.csv'):
        return "<h1>please select CSV file</h1>"

   
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)
    
    next(csv_input) 

    for row in csv_input:
        if len(row) < 6: continue 
        
        new_q = Question(
            exam_id=exam_id,
            text=row[0],
            option_a=row[1],
            option_b=row[2],
            option_c=row[3],
            option_d=row[4],
            correct_answer=row[5].lower() 
        )
        db.session.add(new_q)
    
    db.session.commit()
    return redirect(url_for('admin_panel'))
if __name__ == '__main__':
    app.run(debug=True)    