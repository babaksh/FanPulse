# Git & GitHub - مراحل قدم به قدم

## سوالات مهم:

### 1️⃣ اول commit کنم یا اول repository بسازم؟
**جواب: هر دو کار می‌کنه، ولی بهتره اول commit کنی!**

**ترتیب پیشنهادی:**
1. ✅ Commit local (روی کامپیوتر خودت)
2. ✅ ساخت repository در GitHub
3. ✅ اضافه کردن remote و push

**چرا؟** چون commit فقط روی کامپیوتر خودت هست و به GitHub ربطی نداره. بعداً که repository رو ساختی، push می‌کنی.

---

### 2️⃣ وقتی commit می‌کنم، به کدوم اکانت GitHub push میشه؟
**جواب: هیچ جا! Commit فقط local هست.**

**توضیح:**
- **Commit** = ذخیره تغییرات روی کامپیوتر خودت (local)
- **Push** = فرستادن commit ها به GitHub (remote)

**مراحل:**
```
Commit (local) → هنوز هیچ جا نرفته
     ↓
Add remote (مشخص کردن آدرس GitHub)
     ↓
Push → حالا میره به GitHub
```

---

## 📋 مراحل کامل (قدم به قدم):

### مرحله 1: تنظیم Git Config (فقط یک بار)
```bash
git config --global user.name "اسم تو"
git config --global user.email "ایمیل GitHub تو"
```

**مثال:**
```bash
git config --global user.name "Babak"
git config --global user.email "babak@example.com"
```

**چک کردن:**
```bash
git config --global user.name
git config --global user.email
```

---

### مرحله 2: Commit کردن (Local)
```bash
git commit -m "Initial commit: FanPulse - AI-powered World Cup analysis system"
```

**این کار:**
- ✅ فایل‌ها رو روی کامپیوتر خودت commit می‌کنه
- ❌ هیچ چیزی به GitHub نمیره
- ❌ نیازی به username/password نداره

---

### مرحله 3: ساخت Repository در GitHub

**گام‌ها:**
1. برو به [GitHub.com](https://github.com)
2. کلیک روی **"+"** (بالا سمت راست) → **"New repository"**
3. پر کردن فرم:
   - **Repository name**: `FanPulse`
   - **Description**: `AI-powered World Cup analysis system with VAR explanations`
   - **Visibility**: ✅ **Public** (برای IBM Challenge)
   - **Initialize**: ❌ بدون README, gitignore, license
4. کلیک **"Create repository"**

**نتیجه:** یه صفحه میاد که آدرس repository رو نشون میده:
```
https://github.com/YOUR_USERNAME/FanPulse.git
```

---

### مرحله 4: اضافه کردن Remote
```bash
git remote add origin https://github.com/YOUR_USERNAME/FanPulse.git
```

**جایگزین کن:** `YOUR_USERNAME` رو با username GitHub خودت

**این کار:** به Git میگه که repository GitHub کجاست

---

### مرحله 5: تغییر نام Branch به main
```bash
git branch -M main
```

**چرا؟** GitHub از `main` استفاده می‌کنه، نه `master`

---

### مرحله 6: Push کردن
```bash
git push -u origin main
```

**این کار:**
- ✅ تمام commit ها رو به GitHub میفرسته
- ✅ اینجا username/password یا token میخواد

**Authentication:**
- VS Code خودش از تو username/password میخواد
- یا از GitHub CLI استفاده کن: `gh auth login`
- یا Personal Access Token بساز

---

## 🔐 Authentication (احراز هویت)

### گزینه 1: VS Code (ساده‌ترین)
وقتی `git push` رو بزنی، VS Code خودش یه پنجره میاره که:
1. Sign in to GitHub
2. مرورگر باز میشه
3. Authorize VS Code
4. تمام!

### گزینه 2: Personal Access Token
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Scope: `repo` (full control)
4. Copy token
5. وقتی password میخواد، token رو paste کن

### گزینه 3: GitHub CLI
```bash
gh auth login
```

---

## ✅ چک کردن موفقیت

بعد از push، برو به:
```
https://github.com/YOUR_USERNAME/FanPulse
```

باید ببینی:
- ✅ تمام فایل‌ها
- ✅ README.md نمایش داده میشه
- ✅ تعداد commit ها

---

## 🚨 مشکلات رایج

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/FanPulse.git
```

### Error: "failed to push"
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Error: "Authentication failed"
- از Personal Access Token استفاده کن
- یا GitHub CLI: `gh auth login`

---

## 📝 خلاصه دستورات (به ترتیب)

```bash
# 1. تنظیم config (فقط یک بار)
git config --global user.name "Babak"
git config --global user.email "babak@example.com"

# 2. Commit (local)
git commit -m "Initial commit: FanPulse"

# 3. ساخت repository در GitHub (از مرورگر)

# 4. اضافه کردن remote
git remote add origin https://github.com/YOUR_USERNAME/FanPulse.git

# 5. تغییر branch به main
git branch -M main

# 6. Push
git push -u origin main
```

---

## 🎯 نکات مهم

1. **Commit ≠ Push**
   - Commit = local (روی کامپیوتر)
   - Push = remote (روی GitHub)

2. **Username در commit**
   - از `git config` استفاده می‌کنه
   - نه از GitHub account

3. **Authentication فقط برای Push**
   - Commit نیازی به authentication نداره
   - Push نیاز به GitHub login داره

4. **Repository باید Public باشه**
   - برای IBM Challenge submission
   - Private کار نمی‌کنه

---

## 📞 کمک بیشتر

اگر مشکلی پیش اومد:
1. Error message رو کپی کن
2. بهم بگو چه دستوری زدی
3. کمکت می‌کنم!