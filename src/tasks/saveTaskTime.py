from ..config import celery, db
from ..models.testModel import TestModel
import time
from celery import Celery
from celery.contrib.abortable import AbortableTask
# from celery import current_task


# @celery.task(bind=True,autoretry_for=(Exception,), max_retries=10, default_retry_delay=10)
@celery.task(bind=True)
def saveTaskLongTime(self: AbortableTask, text: str):
    print(555555555555555555555555555555555555555555555)
    time.sleep(2)
    if self.is_aborted():
        return
    raise Exception("Error")
    new_test_model= TestModel(text_test=text)
    db.session.add(new_test_model)
    db.session.commit()
    return new_test_model.to_dict()



    
    