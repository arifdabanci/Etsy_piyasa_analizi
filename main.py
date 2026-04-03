name: Etsy Daily Report Bot

on:
  schedule:
    # UTC 06:00, Türkiye saatiyle 09:00 eder.
    - cron: '0 6 * * *'
  workflow_dispatch: # Manuel çalıştırmak istersen

jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3 # v3 kullanmak her zaman daha kararlıdır

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      # STRATEJİK HAMLE: Kendi izole sanal ortamımızı (venv) kuruyoruz
      - name: Install dependencies in Virtual Environment
        run: |
          python -m venv venv
          source venv/bin/activate
          python -m pip install --upgrade pip
          pip install requests beautifulsoup4 google-genai

      # Botu bu izole ortamın içinde çalıştırıyoruz
      - name: Run Python script
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          EMAIL_ADDRESS: ${{ secrets.EMAIL_ADDRESS }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          RECEIVER_EMAIL: ${{ secrets.RECEIVER_EMAIL }}
        run: |
          source venv/bin/activate
          python main.py
