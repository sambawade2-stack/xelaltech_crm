# FinTrack CRM

CRM financier professionnel — Django + TailwindCSS + HTMX + Chart.js + PostgreSQL + Docker

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.12 + Django 4.2 |
| API REST | Django REST Framework + JWT |
| Base de données | PostgreSQL 16 |
| Cache & Async | Redis + Celery |
| Frontend | Django Templates + HTMX + TailwindCSS CDN |
| Charts | Chart.js 4 |
| Authentification | Django Allauth |
| Audit | django-simple-history + AuditLog custom |
| PDF | ReportLab |
| Excel | openpyxl |
| Serveur | Gunicorn + Nginx |
| Déploiement | Docker + Docker Compose |

## Lancement rapide (Docker)

```bash
# 1. Cloner et configurer
cp .env.example .env
# Editer .env avec vos valeurs

# 2. Démarrer tous les services
docker compose up -d

# 3. Les migrations + seeders s'exécutent automatiquement

# 4. Accéder
# App:   http://localhost (via Nginx)
# Dev:   http://localhost:8000 (direct Gunicorn)
# Admin: http://localhost:8000/admin/
```

## Lancement développement (sans Docker)

```bash
# Prérequis: PostgreSQL et Redis actifs

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Base de données PostgreSQL
createdb fintrack_db

# Migrations
python manage.py migrate

# Données de démo
python manage.py seed_data

# Serveur de développement
python manage.py runserver
```

## Comptes de démonstration

| Email | Mot de passe | Rôle |
|-------|-------------|------|
| admin@fintrack.com | admin123 | Administrateur |
| mamadou@fintrack.com | demo123 | Comptable |
| fatou@fintrack.com | demo123 | Manager |
| ibrahima@fintrack.com | demo123 | Auditeur |

## Structure du projet

```
crm_xelaltech/
├── config/                  # Configuration Django
│   └── settings/
│       ├── base.py          # Settings communs
│       ├── development.py   # Dev overrides
│       └── production.py    # Prod overrides
├── apps/
│   ├── users/               # Authentification + profils + rôles
│   ├── finance/             # Transactions + Factures + Budgets
│   ├── reports/             # Génération rapports PDF/Excel
│   ├── dashboard/           # Vue analytique principale
│   ├── documents/           # GED (gestion électronique documents)
│   ├── notifications/       # Système de notifications
│   ├── audit/               # Logs d'audit + traçabilité
│   └── api/                 # API REST (DRF)
├── templates/               # Templates HTML (TailwindCSS + HTMX)
├── static/                  # Assets statiques
├── docker/
│   ├── nginx/               # Config Nginx
│   └── postgres/            # Init SQL
├── scripts/
│   ├── deploy.sh            # Script déploiement production
│   └── dev.sh               # Script démarrage dev
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## API REST

```
GET  /api/v1/transactions/     Lister les transactions
POST /api/v1/transactions/     Créer une transaction
GET  /api/v1/transactions/{id}/ Détail
PUT  /api/v1/transactions/{id}/ Modifier
DEL  /api/v1/transactions/{id}/ Supprimer

GET  /api/v1/invoices/         Factures
GET  /api/v1/categories/       Catégories
GET  /api/v1/documents/        Documents
GET  /api/v1/notifications/    Notifications

GET  /api/v1/dashboard/stats/  Statistiques tableau de bord
POST /api/v1/auth/token/       Obtenir JWT token
```

## Modules

- **Dashboard**: KPIs revenus/dépenses, graphiques Chart.js 6 mois, répartition catégories, budgets temps réel
- **Transactions**: CRUD complet, filtres avancés, types multiples, pièces jointes, historique complet
- **Factures**: Génération avec items, téléchargement PDF ReportLab, suivi statuts
- **Budgets**: Suivi consommation, alertes automatiques par catégorie
- **Documents**: Upload PDF/images/contrats, organisation par type, tagging
- **Rapports**: Génération async (Celery), export PDF/Excel, rapports mensuels/annuels/cashflow
- **Audit**: Traçabilité complète (qui/quoi/quand/IP), journal immuable, filtres par action
- **Notifications**: Temps réel HTMX, alertes budgets, rappels factures en retard
- **API REST**: DRF + JWT, pagination, filtres, recherche

## Celery — Tâches planifiées

```python
# check_overdue_invoices  — quotidien
# send_budget_alerts      — quotidien
# generate_report_task    — à la demande (async)
```

## Rôles utilisateurs

| Rôle | Accès |
|------|-------|
| Admin | Accès total |
| Comptable | Finance + Documents |
| Manager | Dashboard + Rapports |
| Auditeur | Audit logs + lecture |
| Employé | Dashboard + ses transactions |

## Couleurs UI

- Sidebar: `#081C3A` (bleu nuit)
- Accent: `#2563EB` (bleu électrique)
- Revenus: Vert `#22C55E`
- Dépenses: Rouge `#EF4444`
- Alertes: Orange `#F97316`
