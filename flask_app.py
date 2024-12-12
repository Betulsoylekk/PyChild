from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'ItisReallySecret'

db = SQLAlchemy(app)

@app.before_request
def assign_user_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())  


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    session_id = db.Column(db.String(36), nullable=False)  # Store session ID for tracking scores

    def __repr__(self):
        return f'<Score {self.score}>'


def create_tables():
    with app.app_context():  
        db.create_all()


@app.route('/')
def index():
    user_id = session['user_id']
    
    # Query the highest score for the current session
    highest_score = (
        db.session.query(db.func.max(Score.score))
        .filter_by(session_id=user_id)
        .scalar() or 0
    )
    
    return render_template('index.html', highest_score=highest_score)


@app.route('/submit_answers', methods=['POST'])
def submit_test():
    correct_answers = {
        "q1": "b",
        "q2": "a",
        "q3": "c",
        "q4": "b",
        "q5": "a",
    }

    user_answers = request.form.to_dict()
    total_score = 0

    for question_id, correct_answer in correct_answers.items():
        user_answer = user_answers.get(question_id, None)
        if user_answer == correct_answer:
            total_score += 20  # Each correct answer gives 20 points

    session_id = session['user_id']
    new_score = Score(score=total_score, session_id=session_id)
    db.session.add(new_score)
    db.session.commit()

    return render_template('results.html', total_score=total_score)



if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
