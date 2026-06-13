# Back It Up!

This script scans common Windows folders, picks up files that actually matter, and organizes them into a single backup folder on Desktop. Code is intentionally excluded since it should already be on GitHub.

---

## What it does

It scans these folders on Windows machine.

- Desktop
- Documents
- Downloads
- Pictures
- Videos
- Music

Files are sorted into categories and placed inside a folder called `Linux_Migration_Backup` on Desktop.

---

## Folder structure after running

```
Linux_Migration_Backup/
    Images/
    PDFs/
    Documents/
    Text_Files/
    Videos/
    Audio/
    Fonts/
    Database/
    Archives/
    Others/
    PRIVATE/
        .ssh/
        env_files/
        shell_configs/
        VSCode_User/
        Browser_Bookmarks/
        gnupg/
        .gitconfig
```

---

## What goes where

**Images** -> jpg, jpeg, png, gif, bmp, webp, svg, ico, tiff, heic, raw.

**PDFs** -> all pdf files. These are moved, not copied, so they will no longer exist in their original location after the script runs.

**Documents** -> doc, docx, ppt, pptx, xls, xlsx, csv, rtf, odt and similar office files.

**Text Files** -> txt, md, rst.

**Videos** -> mp4, mkv, avi, mov, wmv, flv, webm.

**Audio** -> mp3, wav, flac, aac, ogg, m4a.

**Fonts** -> ttf, otf, woff, woff2.

**Database** -> db, sqlite, sqlite3.

**Archives** -> zip, rar, 7z, tar, gz.

**Others** -> anything that does not match a known category but is not a code file.

**PRIVATE** -> sensitive files handled separately. See section below.

---

## What goes into PRIVATE

The script automatically picks up the following.

**.ssh folder** -> SSH keys. These are critical if you connect to GitHub, remote servers, or anything over SSH. After copying them to Linux, run these two commands or SSH will refuse to use them.

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
```

Replace `id_rsa` with actual key filename if it is different, for example `id_ed25519`.

**.gitconfig** -> Git name, email, and settings.

**env files** -> any `.env` file found during scanning is copied here with its parent folder name added to the filename, so you know which project it belongs to. For example, a `.env` inside a folder called `myapp` becomes `myapp__.env` inside `PRIVATE/env_files/`.

**shell configs** -> .bashrc, .zshrc, .bash_profile, .profile, .bash_aliases, .zprofile. These are not very useful on Windows but if you had WSL set up, configs are here.

**VSCode settings** -> settings.json, keybindings.json, and snippets folder.

**Browser bookmarks** -> bookmarks from Chrome and Edge are saved as JSON files. To use them on Linux, open browser and use the import bookmarks option, pointing it to this file.

**GPG keys** -> if you use GPG for signing commits or encrypting files, keys are backed up here.

---

## What is skipped

Code files are skipped completely and not placed anywhere, not even in Others. This includes py, java, cpp, js, ts, html, css, json, yml, sh, bat, exe, dll and similar.

Build folders like `node_modules`, `dist`, `build`, `target`, `.git`, `venv`, `__pycache__`, `.next`, `.idea` are skipped entirely during scanning.

Files larger than 500 MB are skipped.

---

## For files greater than 500 MB
To know what large files are going to be skipped, run the script with `--scan-large` argument. It will print all files above the size limit and generate a report on Desktop.

## How to run it

Make sure Python is installed, then open a terminal in the folder where the script is saved and run.

```bash
python backup_script.py
```

The script will print what it is doing as it goes. At the end it shows a summary of how many files were copied, moved, skipped, and if there were any errors.

---

## Before you run it, check these manually

The script cannot catch everything. Go through these yourself before migrating.

- Any project folders that have local changes not pushed to GitHub yet. Run `git status` inside each one to confirm.
- Downloads folder. License keys, activation codes, or purchased software installers are often sitting there.
- Saved passwords in Chrome or Edge. Export them from Settings before switching.
- Postman or Insomnia collections if you use those for API testing. Export them manually from inside the app.
- DBeaver or TablePlus connection configs if you work with databases.

---

## After copying

The PRIVATE folder contains sensitive files. Keep it off cloud storage or delete it once you have set things up on new machine. Do not leave SSH keys or env files sitting in an unprotected location.
