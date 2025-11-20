from apscheduler.schedulers.base import STATE_RUNNING
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import APIRouter, HTTPException

from src.background_tasks.sheduled_cleaner import scheduler, JOB_ID, make_job_func
from src.controller.schemas.schemas import CleanerStatus, StartParams

cleaner_router = APIRouter(prefix="/cleaner", tags=["Процесс удаления старых публикаций"])

@cleaner_router.get("/", response_model=CleanerStatus)
def get_status():
    """
    Возвращает статус планировщика и информацию о задаче.
    """
    job = scheduler.get_job(JOB_ID)
    next_run = None
    trigger = None
    if job:
        # next_run_time — datetime или None
        nrt = job.next_run_time
        next_run = nrt.isoformat() if nrt else None
        trigger = str(job.trigger)
    return {
        "message": "Cleaner info",
        "scheduler_running": scheduler.state == STATE_RUNNING,
        "job_scheduled": job is not None,
        "next_run_time": next_run,
        "trigger": trigger,
        "job_id": JOB_ID,
    }

@cleaner_router.post("/", response_model=CleanerStatus)
def start_cleaner(params: StartParams):
    """
    Запускает планировщик (если ещё не запущен) и ставит задачу.
    Если задача уже есть — заменит её.
    """
    # выбираем триггер
    if params.interval_seconds:
        trigger = IntervalTrigger(seconds=params.interval_seconds, timezone="UTC")
    else:
        trigger = CronTrigger.from_crontab(params.cron, timezone="UTC")

    # старт планировщика, если он ещё не запущен
    if scheduler.state != STATE_RUNNING:
        scheduler.start()

    # добавляем/заменяем задачу
    scheduler.add_job(
        make_job_func(),
        trigger=trigger,
        id=JOB_ID,
        replace_existing=True,
        coalesce=True,  # если выполнения накопятся — объединять
        max_instances=1,
    )

    response = get_status()
    response["message"] = "Cleaner scheduled"
    return response


@cleaner_router.delete("/", response_model=CleanerStatus)
def stop_cleaner():
    """
    Останавливает задачу (удаляет её).
    """
    job = scheduler.get_job(JOB_ID)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    scheduler.remove_job(JOB_ID)

    response = get_status()
    response["message"] = "Cleaner job removed"
    return response
