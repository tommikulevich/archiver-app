# 🗂️ Archiver with Encryption

> ☣ **Warning:** This project was created during my studies for educational purposes only. It may contain non-optimal solutions.

### 📑 About

The program allows user to select multiple files or folders for **archiving** or **unpacking**. When *creating archives*, users can choose **the archive format** (`.zip`, `.7z`, `.tar`), set **the compression level** (`fast`, `normal`, `maximum`), **encrypt the archive** using AES-256, and decide **the archive's name and save location**. It also provides **options to delete source files** after archiving or unpacking. During *unpacking* process, users can specify **the destination for unpacked files** and provide **a password for decryption**. User interface includes **a progress bar** showing the current operation status and **a status label** updating the process results.

> The application is written in **Python 3.10.12**, using Qt (PyQt5) and GTK3 (PyGObject), in Visual Studio Code 1.89.1. Make sure you have installed [GTK3](https://pygobject.gnome.org/getting_started.html) on your system, if you want to run GTK implementation.

### 🌟 Functionality

#### Main window
| Qt | GTK |
| :------: | :--------: |
|<img src="data/_readme-img/1-main-qt.png?raw=true 'Qt: Main window'">|<img src="data/_readme-img/1-main-gtk.png?raw=true 'GTK: Main window'">|

#### Archive window 
| Qt | GTK |
| :------: | :--------: |
|<img src="data/_readme-img/2-archive-qt.png?raw=true 'Qt: Archive window'">|<img src="data/_readme-img/2-archive-gtk.png?raw=true 'GTK: Archive window'">|

#### Unarchive window
| Qt | GTK |
| :------: | :--------: |
|<img src="data/_readme-img/3-unarchive-qt.png?raw=true 'Qt: Unarchive window'">|<img src="data/_readme-img/3-unarchive-gtk.png?raw=true 'GTK: Unarchive window'">|
