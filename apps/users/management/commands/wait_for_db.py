import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Attend que la base de données soit disponible'

    def handle(self, *args, **options):
        self.stdout.write('[wait_for_db] Attente de la base de données...')
        attempts = 0
        while True:
            try:
                conn = connections['default']
                conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS('[wait_for_db] Base de données disponible.'))
                break
            except Exception as e:
                attempts += 1
                if attempts >= 30:
                    self.stdout.write(self.style.ERROR(f'[wait_for_db] Echec après 30 tentatives: {e}'))
                    raise
                self.stdout.write(f'[wait_for_db] Tentative {attempts}/30 — {e} — nouvelle tentative dans 2s...')
                time.sleep(2)
