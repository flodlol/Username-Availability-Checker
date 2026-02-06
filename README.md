# Handle Scout 🔎

Check if a username is available across multiple platforms — instantly!

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)

## ✨ Features

- Check username availability on 10+ platforms at once
- Simple web interface — no coding required
- Fast parallel checking
- Suggestions for alternative usernames

## 🚀 Quick Start (No Coding Required!)

### Step 1: Download

Click the green **Code** button above, then **Download ZIP**. Extract it anywhere.

### Step 2: Install Python

If you don't have Python installed:
- **Mac**: Open Terminal and run `brew install python3`
- **Windows**: Download from [python.org](https://python.org/downloads) (check "Add to PATH"!)
- **Linux**: Run `sudo apt install python3 python3-pip`

### Step 3: Run

- **Mac/Linux**: Double-click `run.sh` or open Terminal and run `./run.sh`
- **Windows**: Double-click `run.bat`

### Step 4: Open

Go to **http://localhost:8000** in your browser. Done! 🎉

---

## 🛠️ For Developers

```bash
git clone https://github.com/flodlol/Username-Availability-Checker.git
cd Username-Availability-Checker
pip install -r requirements.txt
python app.py
```

## 📡 Supported Platforms

| Platform | Status |
|----------|--------|
| GitHub | ✅ Reliable |
| Reddit | ✅ Reliable |
| GitLab | ✅ Reliable |
| Bitbucket | ✅ Reliable |
| Dev.to | ✅ Reliable |
| CodePen | ✅ Reliable |
| Dribbble | ✅ Reliable |
| Behance | ✅ Reliable |
| X (Twitter) | ⚠️ Manual check needed |
| TikTok | ⚠️ Manual check needed |

## 🤝 Contributing

**Want to add a new platform?** It's super easy!

1. Fork this repo
2. Edit `platforms.py` and add one line:
   ```python
   {"name": "Instagram", "url": "https://instagram.com/{username}"},
   ```
3. Create a Pull Request

That's it! We'd love your contributions. 💜

### Ideas for contributions:
- Add more platforms (Instagram, Snapchat, LinkedIn, etc.)
- Improve the UI
- Add dark/light mode toggle
- Translations

---

## 📖 API

```
GET /api/check?username=yourname
```

Returns JSON with availability status for each platform.

## 📄 License

MIT — do whatever you want with it!

---

Made with ❤️ by [Jonas](https://github.com/flodlol)

Checklist:

- Choose a profile URL template
- Decide which status codes indicate availability
- Add any special headers
- Keep logic simple and explainable

## Contributing

Pull requests are welcome. Please:

- Keep checks best-effort and lightweight
- Avoid API keys or heavy scraping
- Add clear reasons for `unknown` results

## License

MIT
