# 0 to 21.1 km: Half Marathon Plan (Streamlit)

A 29-week beginner-to-half-marathon training tracker with a month calendar,
weekly list, progress bar, and a printable PDF (one month per A4 page).

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Host on Streamlit Community Cloud (free)
1. Push this folder to a GitHub repository.
2. Go to https://share.streamlit.io, click **Create app**, pick the repo, and set the main file to `app.py`.
3. Deploy.

## About saved progress
Ticks and the start date are saved to `progress.json` next to `app.py`.
- On your own computer or server, this persists normally.
- On Streamlit Community Cloud the disk resets when the app restarts or sleeps,
  so use **Download backup** in the sidebar now and then, and **Restore from backup** if needed.
- The app has one shared progress file, so it's meant for one person. Anyone with the link
  would see and change the same ticks.

## Files
- `app.py` - the Streamlit app
- `plan.py` - the training plan data and date helpers
- `pdf_export.py` - printable PDF generator
