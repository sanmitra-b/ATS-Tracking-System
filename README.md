# ATS Resume Expert (Streamlit)

## Run locally
1. Create `.env` in project root:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start app:
   ```bash
   streamlit run app.py
   ```

## Push to GitHub
From project root:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## Deploy on Streamlit Community Cloud
1. Go to https://share.streamlit.io
2. Click **New app**
3. Select your GitHub repo and branch `main`
4. Set main file path: `app.py`
5. In app settings, add secret:
   ```toml
   GOOGLE_API_KEY="your_api_key_here"
   ```
6. Click **Deploy**

## Notes
- Do **not** commit `.env` or `.streamlit/secrets.toml`.
- If scanned PDF parsing fails in cloud, it may be due to missing Poppler required by `pdf2image`.
