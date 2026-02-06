# Username Availability Checker

Check if a username is available across multiple platforms at once.

---

## Installation

### Windows

1. Install [Python](https://www.python.org/downloads/) (check "Add to PATH" during installation)

2. Install required libraries:
   ```
   pip install -r requirements.txt
   ```

### Mac

1. Install Python:
   ```
   brew install python3
   ```

2. Install required libraries:
   ```
   pip3 install -r requirements.txt
   ```

---

## Running the App

### Windows
Double-click `run.bat` or run:
```
python app.py
```

### Mac
Double-click `run.sh` or run:
```
python3 app.py
```

Then open http://localhost:8000 in your browser.

---

## Supported Platforms

- GitHub
- Reddit
- GitLab
- Bitbucket
- Dev.to
- CodePen
- Dribbble
- Behance
- X (Twitter) - manual check needed
- TikTok - manual check needed

---

## Adding a New Platform

Edit `platforms.py` and add a new line:

```python
{"name": "Instagram", "url": "https://instagram.com/{username}"},
```

For sites that require JavaScript (can't be checked automatically), add:

```python
{"name": "Snapchat", "url": "https://snapchat.com/add/{username}", "unreliable": True},
```

---

## API

```
GET /api/check?username=yourname
```

Returns JSON with availability status for each platform.

---

## Contributing

Pull requests are welcome. Please:

- Keep checks best-effort and lightweight
- Avoid API keys or heavy scraping
- Add clear reasons for `unknown` results

