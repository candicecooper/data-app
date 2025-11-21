# 🔐 LOGIN CREDENTIALS - Quick Reference

## 📧 Demo Staff Accounts

### Staff Member Logins:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name              Email                          Password
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Emily Jones       emily.jones@example.com        demo123
Daniel Lee        daniel.lee@example.com         demo123
Sarah Chen        sarah.chen@example.com         demo123
Admin User        admin.user@example.com         admin123
Michael Torres    michael.torres@example.com     demo123
Jessica Williams  jessica.williams@example.com   demo123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🔑 Universal Demo Password

**Password:** `demo`

Works with ANY staff email for quick testing!

**Example:**
- Email: `emily.jones@example.com`
- Password: `demo`
- ✅ Login successful!

---

## 🎭 Quick Copy-Paste

### Test Account 1 (JP Program):
```
email: emily.jones@example.com
password: demo123
```

### Test Account 2 (PY Program):
```
email: daniel.lee@example.com
password: demo123
```

### Test Account 3 (SY Program):
```
email: sarah.chen@example.com
password: demo123
```

### Admin Account:
```
email: admin.user@example.com
password: admin123
```

---

## 📝 Adding Your Own Staff

Edit the `MOCK_STAFF` list in `app.py` (around line 195):

```python
MOCK_STAFF = [
    {
        "id": "s7",
        "name": "Your Name",
        "role": "JP",  # JP, PY, SY, or ADM
        "email": "your.email@example.com",
        "password": "yourpassword"
    },
    # ... existing staff
]
```

---

## 🚀 Quick Start

### 1. Run the app:
```bash
streamlit run app.py
```

### 2. Login screen appears

### 3. Enter credentials:
- **Email:** `emily.jones@example.com`
- **Password:** `demo123`

### 4. Click "Login"

### 5. You're in! 🎉

---

## 🔒 Security Notes

### For Demo/Testing:
- Use the provided demo accounts
- Universal "demo" password for quick access
- No real security needed

### For Production:
- Change all passwords
- Use strong passwords
- Remove universal demo password
- Consider real authentication system

---

## ⚠️ Common Issues

### "Invalid email or password"
- ✅ Check spelling
- ✅ Check caps lock
- ✅ Try "demo" as password
- ✅ Use exact email from list

### Password field empty?
- Make sure to click in the password field
- Type password (will show as ****)
- Press Enter or click Login button

---

## 💡 Pro Tip

For fastest testing, use:
- **Email:** Any staff email
- **Password:** `demo`

This works every time! 🚀

---

## 📋 Checklist

Setup:
- [ ] App installed and running
- [ ] Login page visible
- [ ] Password field showing

Testing:
- [ ] Email works
- [ ] Password works
- [ ] Can log in
- [ ] Can access features

---

## 🎓 For Training

When showing the app to new staff:

1. Show login screen
2. Demonstrate with Emily Jones account
3. Show password requirement
4. Explain role-based access (JP/PY/SY/ADM)
5. Give them the credentials card

---

**Keep this card handy for quick reference! 📌**
