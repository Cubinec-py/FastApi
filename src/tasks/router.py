from fastapi import APIRouter, Depends
from starlette.background import BackgroundTasks

from auth.base_config import current_user
from tasks.tasks import send_mail
from auth.base_config import current_active_user


router = APIRouter(
    prefix='/api/tasks',
    dependencies=[Depends(current_active_user)],
    tags=['Tasks'],
)


@router.get("/dashboard")
def get_dashboard_report(background_tasks: BackgroundTasks, user=Depends(current_user)):
    # Simple complete - 1400ms
    # send_mail(user.username)

    # Using FastAPI BackgroundTasks in event loops - 500ms
    # background_tasks.add_task(send_mail, user.username)

    # Using Celery tasks - 600ms
    send_mail.delay(user.username)
    return {
        "status": 200,
        "data": "Письмо отправлено",
        "details": None
    }
