from app import create_app, scheduler
from app.services.scheduler import init_scheduler

app = create_app()

if __name__ == '__main__':
    init_scheduler(scheduler)
    scheduler.start()
    app.run(host='0.0.0.0', port=8000, debug=True)
