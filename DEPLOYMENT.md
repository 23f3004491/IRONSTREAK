# 🚀 IronStreak Deployment Guide (FREE Hosting)

## Overview
- **Frontend**: Vercel (free forever)
- **Backend**: Render (free tier)
- **Database**: Render PostgreSQL (free tier)

---

## Step 1: Push to GitHub

First, create a GitHub repository and push your code:

```bash
cd c:\Users\gangw\Downloads\Projects\IRONSTREAK
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ironstreak.git
git push -u origin main
```

---

## Step 2: Deploy Backend on Render

1. Go to [render.com](https://render.com) and sign up (free)

2. Click **New +** → **Web Service**

3. Connect your GitHub repo

4. Configure:
   - **Name**: `ironstreak-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. Add Environment Variables:
   | Key | Value |
   |-----|-------|
   | `JWT_SECRET` | (click "Generate" for random value) |
   | `USER1_EMAIL` | `Tarungangwar@gmail.com` |
   | `USER1_PASSWORD` | `your-secure-password` |
   | `USER2_EMAIL` | `brother@example.com` |
   | `USER2_PASSWORD` | `another-secure-password` |
   | `FRONTEND_ORIGIN` | (add after Vercel deployment) |

6. Click **Create Web Service**

7. **Add PostgreSQL Database**:
   - Go to **New +** → **PostgreSQL**
   - Name: `ironstreak-db`
   - Plan: **Free**
   - Click **Create Database**
   - Copy the **Internal Database URL**
   - Go back to your web service → Environment → Add:
     - `DATABASE_URL` = (paste the Internal Database URL)

8. Note your backend URL: `https://ironstreak-api.onrender.com`

---

## Step 3: Deploy Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and sign up (free)

2. Click **Add New** → **Project**

3. Import your GitHub repo

4. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js (auto-detected)

5. Add Environment Variable:
   | Key | Value |
   |-----|-------|
   | `NEXT_PUBLIC_BACKEND_URL` | `https://ironstreak-api.onrender.com` |

6. Click **Deploy**

7. Note your frontend URL: `https://ironstreak.vercel.app`

---

## Step 4: Update CORS on Render

Go back to Render → Your Web Service → Environment:

Add/Update:
- `FRONTEND_ORIGIN` = `https://ironstreak.vercel.app`

Click **Save Changes** (service will redeploy)

---

## 🎉 Done!

Your app is now live at: `https://ironstreak.vercel.app`

### Login Credentials:
- Email: `Tarungangwar@gmail.com`
- Password: (whatever you set in `USER1_PASSWORD`)

---

## ⚠️ Important Notes

### Render Free Tier Limitations:
- Service sleeps after 15 mins of inactivity
- First request after sleep takes ~30 seconds (cold start)
- 750 hours/month free (enough for personal use)

### To Keep Backend Awake (Optional):
Use a free cron service like [cron-job.org](https://cron-job.org) to ping your backend every 14 minutes.

### Database:
- Render free PostgreSQL: 1GB storage, 90-day expiry (recreate if needed)
- For permanent free DB, consider [Supabase](https://supabase.com) or [Neon](https://neon.tech)

---

## Troubleshooting

**Login fails?**
- Check if backend is awake (visit `https://your-backend.onrender.com/docs`)
- Verify environment variables on Render

**CORS errors?**
- Make sure `FRONTEND_ORIGIN` matches your Vercel URL exactly

**Database connection fails?**
- Ensure `DATABASE_URL` is set correctly
- Check Render logs for errors
