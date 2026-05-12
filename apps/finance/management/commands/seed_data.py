import random
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed demo data for FinTrack CRM'

    def handle(self, *args, **options):
        self.stdout.write('Seeding FinTrack CRM demo data...')

        from apps.users.models import User
        from apps.finance.models import Category, Transaction, Invoice, InvoiceItem, Budget
        from apps.notifications.models import Notification

        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@fintrack.com',
                'first_name': 'Admin',
                'last_name': 'FinTrack',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'  Created admin: admin@fintrack.com / admin123')

        # Create demo users
        demo_users = [
            ('mamadou.diop', 'mamadou@fintrack.com', 'Mamadou', 'Diop', User.Role.ACCOUNTANT),
            ('fatou.fall', 'fatou@fintrack.com', 'Fatou', 'Fall', User.Role.MANAGER),
            ('ibrahima.ba', 'ibrahima@fintrack.com', 'Ibrahima', 'Ba', User.Role.AUDITOR),
        ]
        users = [admin]
        for uname, email, first, last, role in demo_users:
            u, c = User.objects.get_or_create(username=uname, defaults={
                'email': email, 'first_name': first, 'last_name': last, 'role': role
            })
            if c:
                u.set_password('demo123')
                u.save()
            users.append(u)

        # Categories
        categories_data = [
            ('Salaires', 'income', 'users', '#22C55E'),
            ('Ventes produits', 'income', 'shopping-cart', '#16A34A'),
            ('Loyer', 'expense', 'home', '#EF4444'),
            ('Fournitures', 'expense', 'box', '#F97316'),
            ('Transport', 'expense', 'car', '#F59E0B'),
            ('Marketing', 'expense', 'bullhorn', '#8B5CF6'),
            ('Utilities', 'expense', 'bolt', '#06B6D4'),
            ('Investissement', 'investment', 'chart-line', '#2563EB'),
        ]
        categories = {}
        for name, ctype, icon, color in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={'category_type': ctype, 'icon': icon, 'color': color, 'created_by': admin}
            )
            categories[name] = cat

        # Transactions
        transaction_templates = [
            ('Salaire employés', 'salary', 'Salaires', (800000, 1500000)),
            ('Vente contrat client A', 'income', 'Ventes produits', (200000, 800000)),
            ('Loyer bureau', 'expense', 'Loyer', (150000, 300000)),
            ('Achat fournitures bureau', 'expense', 'Fournitures', (20000, 80000)),
            ('Carburant véhicule', 'expense', 'Transport', (30000, 100000)),
            ('Campagne publicité', 'expense', 'Marketing', (50000, 200000)),
            ('Facture électricité', 'expense', 'Utilities', (15000, 50000)),
            ('Investissement équipement', 'investment', 'Investissement', (300000, 1000000)),
        ]

        txn_count = 0
        for i in range(60):
            title, ttype, cat_name, (min_amt, max_amt) = random.choice(transaction_templates)
            amount = Decimal(random.randint(min_amt, max_amt))
            txn_date = date.today() - timedelta(days=random.randint(0, 180))
            Transaction.objects.get_or_create(
                title=f"{title} #{i+1}",
                defaults={
                    'amount': amount,
                    'transaction_type': ttype,
                    'category': categories.get(cat_name),
                    'date': txn_date,
                    'status': random.choice(['completed', 'completed', 'completed', 'pending']),
                    'created_by': random.choice(users[:2]),
                }
            )
            txn_count += 1

        # Invoices
        clients = ['SONATEL SA', 'Orange Money', 'Wave SN', 'DHL Sénégal', 'Total Energie']
        for i in range(8):
            inv = Invoice(
                client_name=random.choice(clients),
                client_email=f"client{i}@example.com",
                issue_date=date.today() - timedelta(days=random.randint(5, 60)),
                due_date=date.today() + timedelta(days=random.randint(-10, 30)),
                status=random.choice(['pending', 'paid', 'overdue', 'draft']),
                created_by=admin,
            )
            inv.save()
            subtotal = Decimal(0)
            for j in range(random.randint(1, 3)):
                qty = Decimal(random.randint(1, 10))
                price = Decimal(random.randint(10000, 100000))
                InvoiceItem.objects.create(
                    invoice=inv,
                    description=f"Service professionnel {j+1}",
                    quantity=qty,
                    unit_price=price,
                    total=qty * price,
                )
                subtotal += qty * price
            inv.subtotal = subtotal
            inv.tax_rate = Decimal('18')
            inv.save()

        # Budgets
        budget_data = [
            ('Budget Marketing Q2', 'Marketing', 500000),
            ('Budget Transport Mensuel', 'Transport', 200000),
            ('Budget Fournitures', 'Fournitures', 150000),
        ]
        first_day = date.today().replace(day=1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        for name, cat_name, amount in budget_data:
            Budget.objects.get_or_create(
                name=name,
                defaults={
                    'category': categories.get(cat_name),
                    'amount': Decimal(amount),
                    'period_start': first_day,
                    'period_end': last_day,
                    'created_by': admin,
                }
            )

        # Notifications
        Notification.objects.get_or_create(
            user=admin,
            title="Bienvenue sur FinTrack CRM !",
            defaults={
                'message': "Votre environnement de démonstration est prêt. Les données sont pré-chargées.",
                'notification_type': 'success',
            }
        )

        self.stdout.write(self.style.SUCCESS(
            f'\nDonnées de démo créées:\n'
            f'  - {len(users)} utilisateurs\n'
            f'  - {len(categories)} catégories\n'
            f'  - {txn_count} transactions\n'
            f'  - 8 factures\n'
            f'  - 3 budgets\n\n'
            f'Connexion admin: admin@fintrack.com / admin123'
        ))
