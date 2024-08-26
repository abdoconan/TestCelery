# Celery Documentation

Celery is a powerful distributed task queue that allows you to run tasks asynchronously in the background. It is commonly used for handling long-running or background tasks in web applications. Celery consists of two main components:

1. **Queue (Broker)**: The queue, also known as the broker, is where tasks are stored before being processed. Popular choices for brokers include Redis, RabbitMQ, or a persistent database managed through SQLAlchemy.

2. **Backend (Result Store)**: The backend is responsible for storing the results of executed tasks. This can be any database supported by SQLAlchemy, providing flexibility in how you manage task results.

## Celery Architecture with Web Server

Celery is often integrated with web servers to manage and execute time-consuming tasks asynchronously, ensuring the main application remains responsive. Below is a high-level architecture diagram illustrating how Celery works in conjunction with a web server.

![Celery Architecture with Web Server](https://miro.medium.com/v2/resize:fit:720/format:webp/1*YfgI1IhMdA42uq0EHVggcw.png)

## Key Features of Celery

- **Asynchronous Task Execution**: Celery enables tasks to run asynchronously in the background, allowing your application to handle more requests simultaneously and improving overall performance.

- **Function-Based Tasks**: Tasks in Celery are defined as functions, making it easy to trigger them by simply calling the corresponding function. This design offers great flexibility in integrating Celery into different parts of your application.

- **Scalability**: Celery is highly scalable, capable of managing a large number of tasks across multiple worker nodes, making it suitable for both small and large-scale applications.

- **Multiple Broker and Backend Support**: Celery supports a variety of message brokers (e.g., Redis, RabbitMQ) and result backends (e.g., SQLAlchemy, Redis), allowing you to choose the technologies that best meet your application's requirements.

# Code Implementation

## Adding Celery to Flask

To integrate Celery with a Flask application, initialize Celery in the Flask configuration file as follows:
```python 
from celery.contrib.abortable import AbortableTask

## code here 
app: Flask = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.getenv("CELERY_BROKER_URL")
app.config['CELERY_RESULT_BACKEND'] = os.getenv("CELERY_RESULT_BACKEND")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("POSTGRES_URL")
celery: Celery = Celery(
    app.import_name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND']
)
celery.conf.update(app.config)

# Tie Flask application context to Celery tasks
# class ContextTask(celery.Task):
class ContextTask(AbortableTask):
    def __call__(self, *args: tuple, **kwargs: dict) -> any:
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask
celery.conf.update(
    task_track_started=True,  # Track when tasks start
    result_extended=True,  # Store additional task information
)
celery.conf.update(app.config)
```

- Import necessary modules: `Celery`, `AbortableTask`, `Flask`, and `os`.
- Create a Flask app instance and configure it with `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, and `SQLALCHEMY_DATABASE_URI`.
- Initialize Celery with the Flask app's name, broker, and backend configurations.
- Tie the Flask application context to Celery tasks by subclassing `AbortableTask` and overriding the `__call__` method to ensure the task runs within the Flask app context.
- Update Celery configuration with options like `task_track_started` and `result_extended` to enhance task tracking and result storage.

### Notes:

- For `CELERY_BROKER_URL`, add the appropriate protocol before the URL: `sqla+` for databases and `amqp` for RabbitMQ.
- For `CELERY_RESULT_BACKEND`, add `db+` before the PostgreSQL URL or any other database.

## Creating a Task

To create a task in Celery, define a function decorated with `@celery_app.task`. This function will contain the logic you want to execute asynchronously.

```python 
from config import celery_app

@celery_app.task
def saveTaskLongTime(text: str):
    ## task heres
```

## Triggering the Task

To activate the task, use `apply_async` with the function, passing any required arguments via the `args` parameter. You can monitor the task's ID and state to track its progress.

```python 
from celery.contrib.abortable import AbortableAsyncResult

task = saveTaskLongTime.apply_async(args=[text])
```

### Notes:

- Use `task.id` and `task.state` to retrieve the task ID and status, respectively.
- `args=[array]` passes the array of parameters to the function. If there are no parameters, omit this argument.

## Retrieving the Task

To retrieve a task from anywhere in your code, use `AsyncResult` with the task's ID.
```python 
from celery.result import AsyncResult

task: AsyncResult = AsyncResult(task_id)
```


## Re-executing the Task

To restart or re-execute the same task with the same parameters, retrieve the task using `AsyncResult`, and then apply the task again using `apply_async` with the original arguments and keyword arguments.

```python
from celery.result import AsyncResult
from celery.contrib.abortable import AbortableAsyncResult

task = AsyncResult(task_id)
new_task = saveTaskLongTime.apply_async(args=task.args, kwargs=task.kwargs)
```

## Aborting the task
To abort task which alread started or retried, doing this require two step process:
1) The code that change status into aborted is as following: 
```python 
from celery.contrib.abortable import AbortableAsyncResult
task = AbortableAsyncResult(task_id)
task.abort()
```
this is change task to be aborted and prevent it from retiring. however that will not stop the task that currently running. 
2-  To so the task that currently running inside the task it self you have to impelement that step that stop the task as following:
```python 
from celery.contrib.abortable import AbortableTask
@celery.task(bind=True)
def saveTaskLongTime(self: AbortableTask, text: str):
    if self.is_aborted():
        return

```

# Running Celery wroker

```bash
    celery -A app.celery  worker --loglevel=info --pool=threads --queues=queue_name --detach --concurrency=10 
```

### NOTATION
1) celery -A app.celery  worker is the only required part of the line. 
2) `--loglevel=<log level>`, `-l <log level>` is used to set the log lever of celery.
3) `--pool=<value>`, `-P <value>` is used to set how many thread celery will use for the jobs. `solo` for single thread and `threads` for many thread as many task started. while using `--concurrency=10` is used to limit the number of threads to certian number. 
4) `--queues=queue_name`  is optional part to name the queue of the celery otherwise the queue will be named celery
5) `--detach` is used to run the celery in the background without terminal needed to be open. 

# additional options to add to celery task. 

## retiring when exception 
```python 
from config import celery_app

@celery_app.task(autoretry_for=(Exception,))
def saveTaskLongTime(text: str):
    ## task heres
```
## specify max number of retires
```python 
from config import celery_app

@celery_app.task(max_retries=10)
def saveTaskLongTime(text: str):
    ## task heres
```

## added delay between each retriy 
```python 
from config import celery_app

@celery_app.task(default_retry_delay=10)
def saveTaskLongTime(text: str):
    ## task heres
```
