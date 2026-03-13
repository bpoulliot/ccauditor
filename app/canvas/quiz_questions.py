from app.canvas.api import canvas_retry
from app.canvas.rate_limiter import canvas_rate_limiter
from collections import defaultdict

MAX_CONCURRENT_QUIZ_REQUESTS = 5


def fetch_quiz_questions_batch(quizzes):
    quiz_questions = defaultdict(list)
    for quiz in quizzes:
        try:
            canvas_rate_limiter.acquire()
            questions = list(
                canvas_retry(
                    lambda: quiz.get_questions(per_page=100)
                )
            )
            quiz_questions[quiz.id] = questions
        except Exception as e:
            print(f"Quiz question fetch error ({quiz.id}): {e}")

    return quiz_questions