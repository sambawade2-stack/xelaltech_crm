import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Attend que la base de données soit disponible'

    def handle(self, *args, **options):
        self.stdout.write('[wait_for_db] Attente de la base de données...')
        db_conn = None
        attempts = 0
        while not db_conn:
            try:
                db_conn = connections['default']
                db_conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS('[wait_for_db] Base de données disponible.'))
            except OperationalError:
                attempts += 1
                if attempts >= 30:
                    self.stdout.write(self.style.ERROR('[wait_for_db] Impossible de joindre la DB après 30 tentatives.'))
                    raise
                self.stdout.write(f'[wait_for_db] Tentative {attempts}/30 — nouvelle tentative dans 2s...')
                time.sleep(2)
