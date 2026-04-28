import time
import logging
from django.core.management.base import BaseCommand


log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Continuously process outbox events every second"

    def handle(self, *args, **options):
        from src.interface.container import Container

        use_case = Container.process_outbox_use_case()

        while True:
            try:
                use_case()
            except Exception as e:
                log.error("Outbox processing error: %s", e)
            time.sleep(1)
