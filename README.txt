==============================
 MV ROYAL SPICE — TRACKER
==============================

RENDER DEPLOYMENT (one-time setup):
-------------------------------------
1. Upload this folder to a GitHub repo
2. Go to https://render.com → New → Web Service
3. Connect your GitHub repo
4. Render auto-reads render.yaml — just click "Create Web Service"
5. Set these Environment Variables in Render dashboard:
     STAFF_PASSWORD   → your staff login password  (default: mvrs143)
     ADMIN_PASSWORD   → your admin login password  (default: mvrs12345)
     SECRET_KEY       → click "Generate" in Render
6. Done! Live at: https://mvrs-tracker.onrender.com


LOCAL SETUP (optional):
--------------------------
1. Install Python 3.10+
2. pip install -r requirements.txt
3. python manage.py migrate
4. python manage.py runserver
5. Open: http://127.0.0.1:8000
   Admin login: admin / mvrs12345
   Staff login: mvrs143


PAGES:
------
  /                  Dashboard    — Cash earnings, Swiggy/Zomato, expenses, net profit
  /vendors/          Vendors      — All vendors; click to enter daily purchases
  /attendance/       Attendance   — Admin: full staff salary, attendance, edit roles
  /staff-attendance/ Staff Page   — Staff: mark own attendance (Full Day/Half Day/Absent)
  /reports/          Reports      — View any date, full breakdown
  /export-csv/       CSV Export   — Download daily report


FIXED STAFF (pre-loaded):
--------------------------
  Lokesh 1100 | Siphou 600 | Khaleem 1200 | Sibou 333 | Siva 899
  Banty 733 | Khislam 633 | Khana 300 | Toofan 640 | Rakesh 799
  Fillu 400 | Anusha 300 | Priya 333 | Mori Aunty Morning 800
  Evening Aunty Morning 800 | Security 370


ATTENDANCE FEATURES:
---------------------
  Admin Page  → Full Day / Half Day / Absent per staff + edit role/salary + add/remove staff
  Staff Page  → Each staff taps their own card: Full Day / Half Day / Absent
  Half Day    → Automatically pays 50% of fixed salary
  Absent      → Pays ₹0


NOTES:
------
• Swiggy/Zomato recorded separately — NOT added to cash earnings total
• Yesterday's net profit auto carries forward each new day
• Staff self-attendance shows "✓ self-marked" badge on admin page
• Free Render plan sleeps after 15 min of inactivity (upgrade to Starter $7/mo to avoid)
