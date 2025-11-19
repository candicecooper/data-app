# Production Version Setup Guide - Password Authentication

## 🎯 Overview

This guide will help you add password authentication to your production Behaviour Support app.

---

## 📦 What's Included

1. **app_PRODUCTION_WITH_PASSWORDS.py** - Production app with password system
2. **add_password_columns.sql** - SQL to add password fields
3. **generate_password_hash.py** - Script to generate password hashes
4. This guide!

---

## 🚀 Step-by-Step Setup

### Step 1: Add Password Columns to Database

Run this SQL in Supabase SQL Editor:

```sql
-- Add password columns
ALTER TABLE staff ADD COLUMN IF NOT EXISTS password_hash TEXT;
ALTER TABLE staff ADD COLUMN IF NOT EXISTS password_set_date TIMESTAMP;
ALTER TABLE staff ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN DEFAULT true;
ALTER TABLE staff ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;
```

### Step 2: Generate Default Password Hash

Run the password generator:

```bash
python generate_password_hash.py
```

This will output a hash for the default password "Welcome123!"

Copy the hash it gives you.

### Step 3: Set Default Password for All Staff

Run this SQL (replace `YOUR_HASH_HERE` with the hash from Step 2):

```sql
-- Set default password for all existing staff
UPDATE staff 
SET 
    password_hash = 'YOUR_HASH_HERE',
    must_change_password = true
WHERE password_hash IS NULL AND archived = false;
```

### Step 4: Deploy the New App

1. Download `app_PRODUCTION_WITH_PASSWORDS.py`
2. Rename it to `app.py`
3. Replace your current app.py
4. Restart Streamlit

```bash
streamlit run app.py
```

### Step 5: Test Login

1. Go to the app
2. You should see a login page with Email AND Password fields
3. Try logging in:
   - Email: (any staff email)
   - Password: `Welcome123!`
4. You'll be prompted to change your password!

---

## 🔐 How Password System Works

### First Login:
1. Staff enters email + default password ("Welcome123!")
2. System checks password hash
3. If `must_change_password` is true, redirects to change password page
4. Staff must set a new password
5. After changing password, they can access the system

### Subsequent Logins:
1. Staff enters email + their password
2. System verifies password hash
3. Login successful - access granted!

### Password Security:
- ✅ Passwords are hashed with SHA-256
- ✅ Each hash includes a random salt
- ✅ Passwords never stored in plain text
- ✅ Salted hashes prevent rainbow table attacks

---

## 🔧 Managing Passwords

### Reset a Staff Member's Password

If a staff member forgets their password, you (as admin) can reset it:

```sql
-- Generate a new hash using generate_password_hash.py
-- Then update the staff member:
UPDATE staff 
SET 
    password_hash = 'NEW_HASH_HERE',
    must_change_password = true
WHERE email = 'staff.email@schools.sa.edu.au';
```

### Add Password for New Staff

When you add a new staff member through the app, they won't have a password yet.

Option 1: Set default password via SQL (as above)

Option 2: Let them login without password once (if password_hash is NULL), then force password change

---

## 📋 Password Requirements

Current implementation allows any password. You can add requirements by modifying the `render_change_password_page()` function:

```python
# Add these checks in the change password function:
if len(new_password) < 8:
    st.error("Password must be at least 8 characters")
    return

if not any(c.isupper() for c in new_password):
    st.error("Password must contain at least one uppercase letter")
    return

if not any(c.isdigit() for c in new_password):
    st.error("Password must contain at least one number")
    return
```

---

## ⚠️ Important Security Notes

### For Production Use:

1. **Change Default Password:** Don't use "Welcome123!" - use something unique
2. **SSL/HTTPS:** Always use HTTPS in production
3. **Supabase RLS:** Keep row-level security enabled
4. **Regular Updates:** Have staff change passwords regularly
5. **Strong Passwords:** Enforce password complexity requirements

### Current Limitations:

- No "forgot password" email flow (admin must reset)
- No password expiration
- No account lockout after failed attempts
- No two-factor authentication

These can be added if needed!

---

## 🎭 Comparison: Demo vs Production

| Feature | Demo Version | Production Version |
|---------|--------------|-------------------|
| Login | Email only (password = "demo") | Email + Password |
| Password | Same for everyone | Individual passwords |
| Security | Minimal | Password hashing, salting |
| Password Change | Not needed | First login required |
| Password Reset | N/A | Admin can reset |

---

## 🐛 Troubleshooting

### "Invalid email or password"
- Check email is correct
- Check password is exactly "Welcome123!" (case-sensitive) for default
- Verify staff member exists and is not archived

### "Please change your password"
- This is expected on first login
- Set a new password (different from "Welcome123!")
- New password will be saved

### Password won't save
- Check database columns were added correctly
- Check Supabase RLS allows updates
- Check console/terminal for errors

### Staff can't login after changing password
- Password may not have saved
- Check `password_hash` column in database
- Try resetting password via SQL

---

## 📧 Support

If you need help:
1. Check the troubleshooting section above
2. Verify database columns exist
3. Check Streamlit console for errors
4. Verify RLS policies allow operations

---

## ✅ Checklist

Before going live with passwords:

- [ ] Added password columns to database
- [ ] Generated password hash
- [ ] Set default password for all staff
- [ ] Deployed new app version
- [ ] Tested login with default password
- [ ] Tested password change
- [ ] Tested login with new password
- [ ] Informed staff about password system
- [ ] Documented how to reset passwords
- [ ] Enabled HTTPS (if not already)

---

**You're all set! Your app now has secure password authentication!** 🎉
