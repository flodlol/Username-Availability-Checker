# Add platforms here
# url: use {username} as placeholder
# unreliable: True for JS-heavy sites that need manual check

PLATFORMS = [
    {"name": "GitHub", "url": "https://github.com/{username}"},
    {"name": "Reddit", "url": "https://www.reddit.com/user/{username}/about.json"},
    {"name": "X", "url": "https://x.com/{username}", "unreliable": True},
    {"name": "TikTok", "url": "https://www.tiktok.com/@{username}", "unreliable": True},
    {"name": "GitLab", "url": "https://gitlab.com/{username}"},
    {"name": "Bitbucket", "url": "https://bitbucket.org/{username}"},
    {"name": "Dev.to", "url": "https://dev.to/{username}"},
    {"name": "CodePen", "url": "https://codepen.io/{username}"},
    {"name": "Dribbble", "url": "https://dribbble.com/{username}"},
    {"name": "Behance", "url": "https://www.behance.net/{username}"},
    {"name": "Hugging Face", "url": "https://huggingface.co/{username}"},
    {"name": "Figma", "url": "https://www.figma.com/@{username}", "unreliable": True},
]