from app.tasks.scan_tasks import scan_course_task

def queue_course_scan(course_id):

    scan_course_task.delay(course_id)