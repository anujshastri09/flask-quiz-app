import html


class QuizBrain:
    def __init__(self, questions):
        self.question_number = 0
        self.score = 0
        self.questions = questions


    def has_questions(self):
        return self.question_number < len(self.questions)


    def next_question(self):
        q = self.questions[self.question_number]
        self.question_number += 1
        return html.unescape(q.text)


    def check_answer(self, user_answer):
        correct = self.questions[self.question_number - 1].answer
        if user_answer.lower() == correct.lower():
           self.score += 1
        return True
        return False