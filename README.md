
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


   python manage.py runserver
   ```
 Open `http://127.0.0.1:8000/`. Admin site: `http://127.0.0.1:8000/admin/`.

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


<img width="1917" height="863" alt="Screenshot 2026-11-12 015404" src="https://github.com/user-attachments/assets/d3bd1639-c87b-4e2c-a3bd-03a6eb69dcaa" />
<img width="1910" height="864" alt="Screenshot 2026-11-12 015342" src="https://github.com/user-attachments/assets/511b83dc-7a4c-4b6a-ad6f-587735a9c4b1" />
<img width="1917" height="858" alt="Screenshot 2026-11-12 015325" src="https://github.com/user-attachments/assets/1ba95d74-b72e-4824-b7fd-ebdfce70b94f" />
<img width="1915" height="862" alt="Screenshot 2026-11-12 015307" src="https://github.com/user-attachments/assets/90ab4423-69ae-41c5-bb78-405bb3a8a5d6" />
<img width="1919" height="854" alt="Screenshot 2026-11-12 015241" src="https://github.com/user-attachments/assets/b4ca036f-c71a-4ca3-aaa3-2452196a039d" />
<img width="1916" height="858" alt="Screenshot 2026-11-12 015231" src="https://github.com/user-attachments/assets/a645c245-6ddc-4d6a-9200-644aeaaad364" />

