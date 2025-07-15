# 📌 spam.io — Telegram Spam Channel & Group Cleaner

**spam.io** is a simple Python script that automatically scans your Telegram account for spam **groups** and **channels**, detects them based on keywords, and safely leaves them in batches — so your Telegram stays clean and clutter-free.

---

## ✨ Features

✅ Automatically detect spam **groups** and **channels**  
✅ Uses a customizable spam keyword list  
✅ Supports a safe list (never leave important groups by accident)  
✅ Runs in safe batches to avoid API limits  
✅ Keeps a log of all actions (`spam_cleaner.log`)  
✅ Unicode-safe for all languages & emojis  
✅ Works on Windows, Linux, Mac

---

## 📂 Requirements

- Python **3.8+**
- [Telethon](https://docs.telethon.dev)

---

## 📦 Installation

- pip install telethon

---

## 📲 Create a Telegram API ID & hash:

- Get yours at my.telegram.org
- Replace api_id and api_hash in spamio.py with your own.

---

## 😶‍🌫️ Optional:

- Add trusted group/channel names to safe_list.txt (one per line)

---

## 🚀 Usage:

- python spamio.py

---

