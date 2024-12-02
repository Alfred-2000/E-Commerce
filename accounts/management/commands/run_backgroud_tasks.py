import subprocess
import logging
from django.core.management import BaseCommand
from e_commerce.constants import LOG_LINES
from e_commerce.settings import CELERY_DEFAULT_WORKER, CELERY_DEFAULT_QUEUE


class Command(BaseCommand):
    help = "This is django command line script to run celery worker"

    def handle(self, *args, **options):
        logging.info("STARTING_CELERY_WORKER" + LOG_LINES)
        try:
            logfile = "/tmp/debug.log"
            cmd = f"celery -A e_commerce worker -Q {CELERY_DEFAULT_QUEUE} -l INFO --concurrency={CELERY_DEFAULT_WORKER} --prefetch-multiplier=1 -O fair -f {logfile}"
            subprocess.call([cmd], shell=True)
        except Exception as error:
            logging.info(
                "Exception occured while starting celery"
                + LOG_LINES
                + "{}".format(error)
            )
