# Quick Fixes Needed

## 🎨 Issue 1: Text Visibility (FIXED)

I've updated the CSS to aggressively force text colors:
- **White text** on dark backgrounds (main page)
- **Dark text** on white backgrounds (forms, tables, cards)

**Download:** app_fixed_visibility.py
**Action:** Replace your current app.py with this file and restart your Streamlit app

---

## 📊 Issue 2: Can't Add Students (NEEDS FIX)

Your students table is missing the `program` column that the app expects.

### Fix in Supabase:

1. Go to Supabase → SQL Editor
2. Run this SQL:

```sql
-- Add missing program column
ALTER TABLE students ADD COLUMN IF NOT EXISTS program TEXT;

-- Verify it worked
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'students'
ORDER BY ordinal_position;
```

3. After running, you should see `program` in the list of columns

---

## ✅ After Fixing Both Issues:

1. **Replace app.py** with the new file
2. **Run the SQL** to add program column
3. **Restart your Streamlit app**
4. **Login with:** candice.cooper330@schools.sa.edu.au
5. **Try adding a student again**

---

## 🚀 Testing Your Fixed App:

### Test 1: Visibility
- Can you read all text on the page?
- Are forms readable?
- Are buttons visible?

### Test 2: Add a Student
- Go to Admin Portal → Student Management
- Fill in:
  - First Name: Test
  - Last Name: Student  
  - Date of Birth: 01/01/2015
  - Program: JP (or PY or SY)
  - Grade: (choose based on program)
  - EDID: TEST001
- Click "Add Student"
- Should show success message!

### Test 3: Add Staff
- Go to Admin Portal → Staff Management
- Fill in:
  - First Name: Jane
  - Last Name: Doe
  - Email: jane.doe@schools.sa.edu.au
  - Role: JP
- Click "Add Staff"
- Jane should now be able to login!

---

## 📧 Your Current Login Emails:

You can login with any of these:
- admin@test.com
- admin@example.com
- testadmin@example.com
- annette.balestrin13@schools.sa.edu.au
- candice.cooper330@schools.sa.edu.au
- naomi.schlein14@schools.sa.edu.au
- caitie.hook19@schools.sa.edu.au

---

## 🔧 If Students Still Won't Add:

Check the Streamlit error message and share it with me. It might show:
- Database error
- Validation error
- Missing field error

I can then help debug further!
