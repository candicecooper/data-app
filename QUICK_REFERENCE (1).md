# 📋 QUICK REFERENCE CARD

## 🎭 DEMO VERSION

**File:** `app_DEMO.py`

### Run It:
```bash
streamlit run app_DEMO.py
```

### Login:
- **Email:** Any demo email (e.g., `admin@demo.edu.au`)
- **Password:** `demo`

### Demo Emails:
- admin@demo.edu.au
- sarah.johnson@demo.edu.au
- jessica.williams@demo.edu.au
- emily.brown@demo.edu.au

### What It Has:
- 9 mock students
- 7 mock staff
- 65+ mock incidents
- Full analytics

### Use For:
- Presentations
- Training
- Sharing publicly
- Portfolio

---

## 🔐 PRODUCTION VERSION

**File:** `app_PRODUCTION_WITH_PASSWORDS.py`

### Setup (One Time):
```bash
# 1. Run SQL
add_password_columns.sql (in Supabase)

# 2. Generate hash
python generate_password_hash.py

# 3. Set passwords (SQL)
UPDATE staff SET password_hash = '[hash]' WHERE ...

# 4. Run app
streamlit run app_PRODUCTION_WITH_PASSWORDS.py
```

### Login:
- **Email:** (your staff email)
- **Password:** `Welcome123!` (first time)
- **Will prompt:** Change password

### What It Has:
- Real database (Supabase)
- Password authentication
- Data persistence
- Full CRUD operations

### Use For:
- Actual school use
- Real student data
- Daily operations

---

## 🔧 QUICK FIXES

### Can't Add Staff/Students?
```sql
-- Disable RLS
ALTER TABLE staff DISABLE ROW LEVEL SECURITY;
ALTER TABLE students DISABLE ROW LEVEL SECURITY;
ALTER TABLE incidents DISABLE ROW LEVEL SECURITY;
```

### Reset Password?
```bash
# Generate new hash
python generate_password_hash.py

# Update in SQL
UPDATE staff 
SET password_hash = '[new_hash]', must_change_password = true
WHERE email = 'staff@email.com';
```

### Demo Not Working?
```bash
# Check requirements
pip install streamlit pandas plotly numpy

# Run again
streamlit run app_DEMO.py
```

---

## 📁 FILES CHECKLIST

### Demo:
- [ ] app_DEMO.py
- [ ] DEMO_README.md

### Production:
- [ ] app_PRODUCTION_WITH_PASSWORDS.py
- [ ] add_password_columns.sql
- [ ] generate_password_hash.py
- [ ] PRODUCTION_SETUP_GUIDE.md

### Docs:
- [ ] FINAL_DELIVERY_SUMMARY.md
- [ ] This quick reference!

---

## 🎯 REMEMBER

**Demo:** Password = "demo" for everyone  
**Production:** Default = "Welcome123!" (change required)

**Demo:** Data resets on refresh  
**Production:** Data persists in database

**Demo:** Safe to share  
**Production:** Keep secure (real data)

---

## 📞 EMERGENCY CONTACTS

**Database Issues:** Check Supabase console  
**Login Issues:** Verify staff email exists  
**Password Issues:** Use generate_password_hash.py  
**General Issues:** Check PRODUCTION_SETUP_GUIDE.md

---

**Print this and keep it handy!** 📌
