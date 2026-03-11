from concurrent.futures import ThreadPoolExecutor
from app.canvas.retry import canvas_retry

MAX_CONCURRENT_QUIZ_REQUESTS = 5


def fetch_quiz_questions_batch(quizzes):
    """
    Fetch quiz questions in controlled parallel batches.
    Prevents API burst spikes.
    """

    results = {}

    def fetch(quiz):
        try:
            questions = list(
                canvas_retry(
                    quiz.get_questions(per_page=100)
                )
            )
            return quiz.id, questions
        except Exception:
            return quiz.id, []

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_QUIZ_REQUESTS) as pool:
        futures = [pool.submit(fetch, q) for q in quizzes]

        for future in futures:
            quiz_id, questions = future.result()
            results[quiz_id] = questions

    return results