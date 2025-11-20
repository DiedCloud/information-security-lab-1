from fastapi import APIRouter

cleaner_router = APIRouter(prefix="/cleaner", tags=["Процесс удаления старых публикаций"])

@cleaner_router.get("/")
def get_status():
    pass

@cleaner_router.post("/")
def start_cleaner():
    pass

@cleaner_router.delete("/")
def stop_cleaner():
    pass
