import time
import logging
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Attend que la base de données soit disponible'

    def handle(self, *args, **options):
        self.stdout.write('[wait_for_db] Attente de la base de données...')
        for attempt in range(1, 31):
            try:
                conn = connections['default']
                conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS('[wait_for_db] Base de données disponible.'))
                return
            except OperationalError as e:
                self.stdout.write(f'[wait_for_db] Tentative {attempt}/30 — {e} — retry dans 2s...')
                logger.warning('wait_for_db attempt %d/30: %s', attempt, e)
                time.sleep(2)
            except Exception as e:
                # Erreur de config (mauvais DATABASE_URL, driver manquant…)
                self.stdout.write(self.style.ERROR(f'[wait_for_db] Erreur de configuration : {e}'))
                logger.error('wait_for_db config error: %s', e)
                raise

        raise SystemExit('[wait_for_db] Base de données inaccessible après 30 tentatives.')
