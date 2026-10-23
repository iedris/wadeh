# Wadeh

A Python 3.10+ command-line tool that explains official documents using Groq.
Document text is sent to Groq for processing.

## Setup

Run `python -m pip install -r requirements.txt`.
If you do not already have a `.env`, copy `.env.example` to `.env`.
Set `GROQ_API_KEY` in your environment or `.env` beside the script.
Optionally set `GROQ_MODEL` to a model available to your account.
Existing environment variables take precedence over `.env`.

## Usage

### Web interface

Install the dependencies above, then run:

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser. Paste text or select a UTF-8 `.txt`
file, then click **Explain my document**. The page shows loading feedback,
results, and errors. Documents are limited to 50,000 characters and requests
to 1 MB. Uploaded files are processed in memory, not saved to disk. Your API key
stays in Python and is never included in the page. This server is for local use.

### Command line

```powershell
python analyzer.py
python analyzer.py --file document.txt
python analyzer.py --file document.txt --model your_model_id
Get-Content -Raw -Encoding UTF8 document.txt | python analyzer.py
```

For interactive input, paste your text, then submit two consecutive empty lines
to finish. Single blank lines between paragraphs are preserved.
File input supports UTF-8 text files with or without a BOM. PDF and Word
extraction are not included. Results go to standard output; progress and errors
go to standard error. Failure exits with status 1, cancellation with status 130.

Answers are generated from supplied text and are not independently verified.

## Free hosting on Render

`render.yaml` defines a free Python web service using Gunicorn. Connect the
project's Git repository to a Render Blueprint, then enter `GROQ_API_KEY` as a
secret when prompted. Never commit `.env` or paste its contents into chat.
If needed, set `GROQ_MODEL` in the Render environment settings.

Render assigns the public `onrender.com` address after creation; the exact
address depends on availability. The included configuration requests the Free
plan. Free services sleep after inactivity and have usage limits.

## Checks

Run `python -m unittest discover -s tests -v`.
