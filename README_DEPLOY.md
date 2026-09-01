# 🚀 Galactic Voyager — Deployment Guide

## Option A: 🌐 Play in Browser (Public Link via itch.io)

This is the **easiest way** to get a public link so anyone can play without installing anything.

### Step 1 — Install Pygbag
```bash
pip install pygbag
```

### Step 2 — Build the Web Version
```bash
# Run from your project root (c:\Shooter_Game)
python -m pygbag --build main.py
```
This generates a `build/web/` folder with `index.html`.

### Step 3 — Test Locally
```bash
python -m pygbag main.py
# Opens at: http://localhost:8000
```

### Step 4 — Upload to itch.io
1. Go to [https://itch.io](https://itch.io) → Create account → New Project
2. Set **Kind of project** = HTML
3. Zip the `build/web/` folder → Upload the zip
4. Check **"This file will be played in the browser"**
5. Set viewport size: **480 × 800**
6. Click **Save & view page** → copy the public URL ✅

> **Result**: Anyone in the world can open that link and play your game in their browser — no download!

---

## Option B: 📱 Android APK

Buildozer requires a **Linux environment** (WSL or Ubuntu).

### Step 1 — Enable WSL (Windows)
```powershell
# In PowerShell as Administrator:
wsl --install
# Restart PC, then open Ubuntu from Start Menu
```

### Step 2 — Install Buildozer in WSL
```bash
sudo apt update && sudo apt install -y \
    python3-pip git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config zlib1g-dev \
    libncurses5-dev libncursesw5-dev libtinfo5 cmake

pip install buildozer cython
```

### Step 3 — Copy Project to WSL
```bash
cp -r /mnt/c/Shooter_Game ~/Shooter_Game
cd ~/Shooter_Game
```

### Step 4 — Build Debug APK
```bash
buildozer android debug
```
> First build downloads Android SDK/NDK (~2GB), takes 15–30 min.

### Step 5 — Get Your APK
The APK will be at:
```
~/Shooter_Game/bin/galacticvoyager-1.0-debug.apk
```

### Step 6 — Install on Phone
1. Enable **Developer Options** on your Android phone
2. Enable **USB Debugging**
3. Connect via USB → run:
```bash
adb install bin/galacticvoyager-1.0-debug.apk
```

Or copy the APK to your phone and open it directly (allow "Install from unknown sources").

---

## Option C: 🎮 GitHub Pages (Free Public Hosting)

After running `pygbag --build main.py`:

1. Push the `build/web/` folder to a GitHub repo
2. Go to repo **Settings → Pages**
3. Set source = `main` branch, `/docs` folder (or use a `gh-pages` branch)
4. Your game is live at: `https://yourusername.github.io/repo-name/` ✅

---

## Quick Commands Summary

| Action | Command |
|--------|---------|
| Run game (desktop) | `python main.py` |
| Test in browser | `python -m pygbag main.py` |
| Build web bundle | `python -m pygbag --build main.py` |
| Build Android APK | `buildozer android debug` (WSL/Linux) |
| Install APK | `adb install bin/*.apk` |
