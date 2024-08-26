from src.config import init_app, celery

app = init_app()
cel = celery

if __name__ == "__main__": 
    app.run(port=6000)