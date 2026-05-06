import logging
import os
import signal

from app.tasks.queue_worker import run_queue_worker


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

is_running = True


def stop_worker(signum: int, _frame: object) -> None:
    global is_running
    logging.info("Worker received stop signal: %s", signum)
    is_running = False


def main() -> None:
    logging.info("Worker service started")
    logging.info("Redis URL configured: %s", os.getenv("REDIS_URL", "not set"))
    logging.info("Database URL configured: %s", os.getenv("DATABASE_URL", "not set"))

    signal.signal(signal.SIGINT, stop_worker)
    signal.signal(signal.SIGTERM, stop_worker)

    run_queue_worker(lambda: is_running)

    logging.info("Worker service stopped")


if __name__ == "__main__":
    main()
