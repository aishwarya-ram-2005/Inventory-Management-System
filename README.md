# SmartStock – Smart Inventory Management System

A Django + MySQL inventory management application with an analytics dashboard, product catalogue, stock movement tracking, low-stock alerts, supplier directory, batch/expiry tracking, search/filtering, and CSV/PDF reports.

## Main features
1. Dashboard: product count, low/out-of-stock counts, inventory valuation, category chart, recent stock movements, expiry watch.
2. Product management: create, edit, search, filter, stock status, product image URL.
3. Stock management: stock-in and stock-out, transaction history, validation against negative stock.
4. Low-stock alerts: generated when a product reaches its reorder level.
5. Supplier management: supplier contact directory.
6. Search/filter: name/SKU, category and stock status.
7. Reports: inventory valuation plus CSV and PDF exports.
8. Batch/expiry tracking: batch codes, manufacture and expiry dates, 30-day warning.

## Requirements
- Python 3.11 or 3.12 recommended
- MySQL Server 8.0 or 8.4
- MySQL Workbench (optional, for database management)
- VS Code (optional)

## Windows setup
1. Extract the ZIP.
2. Open Command Prompt in the folder containing `manage.py`.
3. Create and activate a virtual environment:
   ```cmd
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   ```
   If Python 3.12 is not installed, use `py -m venv .venv`.
4. Install packages:
   ```cmd
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. In MySQL Workbench, run:
   ```sql
   CREATE DATABASE smartstock_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
6. Copy `.env.example` to `.env`. On Windows Command Prompt:
   ```cmd
   copy .env.example .env
   ```
   Edit `.env` and enter the MySQL password. Do not upload `.env` to GitHub.
7. Create database tables:
   ```cmd
   python manage.py makemigrations inventory
   python manage.py migrate
   ```
8. Create an administrator:
   ```cmd
   python manage.py createsuperuser
   ```
9. Start the server:
   ```cmd
   python manage.py runserver
   ```
10. Open `http://127.0.0.1:8000/`. Admin site: `http://127.0.0.1:8000/admin/`.

## First-use checklist
- Sign in using the superuser account.
- Add categories first.
- Add suppliers.
- Add products. The opening quantity is recorded as an opening stock transaction.
- Use Stock movements to record later stock-in and stock-out.
- Add batches to track expiry dates.
- Review Alerts and Reports.

## Testing checklist
1. Login is required to view the application.
2. Add a category and supplier.
3. Add a product with quantity 10 and reorder level 5.
4. Record Stock Out quantity 6. Product quantity should become 4 and a low-stock alert should appear.
5. Try Stock Out quantity 99. The form should reject it and leave quantity unchanged.
6. Record Stock In quantity 10. Product quantity should become 14 and the low-stock alert should be resolved.
7. Add a batch with an expiry date within 30 days. It should appear in the dashboard expiry watch.
8. Search products by SKU and filter by category/status.
9. Download the CSV and PDF reports.

## Notes
- The app uses Django's built-in authentication. Create staff users through Django Admin if needed.
- This is a local development starter. Before public deployment, set `DEBUG=False`, use a strong unique `SECRET_KEY`, configure secure HTTPS cookies, restrict `ALLOWED_HOSTS`, configure static/media hosting, backups, and database permissions.
- Product images are optional external image URLs; no image upload is required.
- For production, use role-based permission checks tailored to your organization and add automated tests/monitoring.
