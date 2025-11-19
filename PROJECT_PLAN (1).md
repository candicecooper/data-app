# Project Plan: Demo Version + Production Fixes

## 🎯 Goals

### 1. Demo Version (Synthetic Data)
Create a standalone demo app with:
- ✅ 9 mock students (3 per program: JP, PY, SY)
- ✅ 6 mock staff members (2 per program)
- ✅ 50+ mock incident reports
- ✅ Realistic names, dates, behaviors
- ✅ Enough data for meaningful analytics
- ✅ NO database connection (pure mock data)
- ✅ Can be shared publicly without exposing real data

### 2. Production Version Fixes
Fix the current production app:
- ✅ Fix staff/student insertion issue
- ✅ Add password authentication
- ✅ Keep all existing Supabase integration
- ✅ Maintain all current functionality

---

## 📦 Deliverables

### Demo Version Files:
1. **app_DEMO.py** - Standalone demo with mock data
2. **DEMO_README.md** - Instructions for running demo
3. **demo_data.json** - Mock data file (optional, embedded in app)

### Production Version Files:
1. **app_PRODUCTION_WITH_PASSWORDS.py** - Fixed production app
2. **add_password_column.sql** - SQL to add password fields
3. **PRODUCTION_UPDATE_GUIDE.md** - How to implement passwords

---

## 🎭 Demo Version Specifications

### Mock Students (9 total):

**JP Program (3 students):**
- Emma Thompson, Grade R, EDID: JP001
- Oliver Martinez, Grade Y1, EDID: JP002
- Sophia Wilson, Grade Y2, EDID: JP003

**PY Program (3 students):**
- Liam Chen, Grade Y3, EDID: PY001
- Ava Rodriguez, Grade Y4, EDID: PY002
- Noah Brown, Grade Y6, EDID: PY003

**SY Program (3 students):**
- Isabella Garcia, Grade Y7, EDID: SY001
- Ethan Davis, Grade Y9, EDID: SY002
- Mia Anderson, Grade Y11, EDID: SY003

### Mock Staff (6 total):
- Sarah Johnson (JP Teacher)
- Michael Lee (JP Support)
- Jessica Williams (PY Teacher)
- David Martinez (PY Support)
- Emily Brown (SY Teacher)
- James Wilson (SY Support)

### Mock Incidents (50+):
- Distribution across all students
- Various behavior types: Refusal, Elopement, Aggression, etc.
- Different severity levels
- Different times of day
- Different locations
- Realistic interventions and outcomes
- Date range: Last 3 months

---

## 🔐 Production Password System

### Password Features:
1. **Hashed passwords** (bcrypt)
2. **Login with email + password**
3. **Password reset capability** (admin only)
4. **Default password** for new staff
5. **Force password change** on first login (optional)

### Database Changes:
```sql
-- Add password fields to staff table
ALTER TABLE staff ADD COLUMN password_hash TEXT;
ALTER TABLE staff ADD COLUMN password_changed_at TIMESTAMP;
ALTER TABLE staff ADD COLUMN force_password_change BOOLEAN DEFAULT false;
```

### Login Flow:
1. Enter email
2. Enter password
3. Verify password hash matches
4. If first login, force password change
5. Login successful

---

## 🚀 Implementation Priority

### Phase 1: Fix Current Production Issue (Immediate)
- Debug why Ben can't be added
- Fix the database insertion
- Test staff addition works

### Phase 2: Create Demo Version (2-3 hours)
- Generate all mock data
- Replace database calls with mock data
- Test all features work with mock data
- Package for distribution

### Phase 3: Add Password System (2-3 hours)
- Add password fields to database
- Update login page
- Add password hashing
- Add password reset functionality
- Test thoroughly

---

## 📝 Next Steps

1. **First:** Let's fix the current Ben Sutton issue
   - Run the SQL check to see if he exists
   - Check the actual error in terminal
   - Fix the root cause

2. **Second:** Create demo version
   - I'll generate all mock data
   - Create standalone app
   - Test analytics work

3. **Third:** Add passwords
   - Update database schema
   - Implement authentication
   - Test login flow

---

## ⏱️ Estimated Timeline

- Fix current issue: **30 minutes**
- Create demo version: **2-3 hours**
- Add password system: **2-3 hours**
- Testing & documentation: **1 hour**

**Total: ~6-7 hours of work**

---

## 🤔 Questions Before Starting

1. **For demo:** Do you want specific behavior patterns (e.g., one student with escalating incidents)?
2. **For passwords:** Do you want password complexity requirements?
3. **For passwords:** Should there be a "forgot password" email flow or admin-reset only?

Let me know and I'll start building! 🚀
