from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import random
import html  # For decoding HTML entities

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# ----------------- Users -----------------
users = {}

# ----------------- Categories -----------------
CATEGORIES = {
    9: "General Knowledge",
    10: "Entertainment: Books",
    11: "Entertainment: Film",
    12: "Entertainment: Music",
    17: "Science & Nature",
    18: "Computers",
    19: "Mathematics",
    21: "Sports",
    23: "History",
    27: "Animals"
}

# ----------------- Routes -----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists.')
        else:
            users[username] = password
            flash('Signup successful. Please login.')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        category_id = request.form.get('category')
        amount = int(request.form.get('amount', 5))
        try:
            response = requests.get(
                "https://opentdb.com/api.php",
                params={
                    "amount": amount,
                    "type": "multiple",
                    "category": category_id
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json().get('results', [])
            if not data:
                flash('No questions found for this category.')
                return redirect(url_for('index'))

            # Prepare questions with shuffled options and decode HTML entities
            question_bank = []
            for q in data:
                options = q['incorrect_answers'] + [q['correct_answer']]
                random.shuffle(options)
                labels = ['A', 'B', 'C', 'D']
                option_pairs = [(label, html.unescape(opt)) for label, opt in zip(labels, options)]

                question_bank.append({
                    'text': html.unescape(q['question']),
                    'answer': html.unescape(q['correct_answer']),
                    'option_pairs': option_pairs
                })

            session['questions'] = question_bank
            session['index'] = 0
            session['score'] = 0

            return redirect(url_for('quiz'))

        except requests.exceptions.RequestException:
            flash('Network error. Try again later.')
            return redirect(url_for('index'))

    return render_template('index.html', categories=CATEGORIES)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user' not in session:
        return redirect(url_for('login'))

    questions = session.get('questions', [])
    index = session.get('index', 0)
    score = session.get('score', 0)

    if index >= len(questions):
        return redirect(url_for('result'))

    current_question = questions[index]
    option_pairs = current_question['option_pairs']

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        if user_answer == current_question['answer']:
            session['score'] += 1
        session['index'] += 1
        return redirect(url_for('quiz'))

    return render_template('quiz.html', question=current_question['text'], option_pairs=option_pairs, score=score)

@app.route('/result')
def result():
    if 'user' not in session:
        return redirect(url_for('login'))

    score = session.get('score', 0)
    total = len(session.get('questions', []))
    return render_template('result.html', score=score, total=total)

if __name__ == '__main__':
    app.run(debug=True)
