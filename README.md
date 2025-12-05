# 🏥 Aplikasi Prediksi Risiko Stroke

Aplikasi web berbasis Flask untuk memprediksi risiko stroke menggunakan Machine Learning.

---

## 📋 Daftar Isi

- [Instalasi](#instalasi)
- [Cara Menjalankan](#cara-menjalankan)
- [Struktur Project](#struktur-project)
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Developer](#developer)

---

## 🚀 Instalasi

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Fahmialfayadh/finalproject_risikostroke.git
cd finalproject_risikostroke
```

### 2️⃣ Buka Project di VSCode

**Jika perintah `code` sudah terpasang di PATH:**

```bash
code .
```

**Jika belum bisa:**

1. Buka VSCode
2. Tekan `Ctrl + Shift + P` (Windows/Linux) atau `Cmd + Shift + P` (Mac)
3. Pilih: `Shell Command: Install 'code' command in PATH`
4. Tekan Enter
5. Ulangi perintah:

```bash
code .
```

### 3️⃣ Install Dependencies

**Cara cepat:**

```bash
pip install -r requirements.txt
```

**Kalau error atau tidak bisa install, gunakan virtual environment:**

```bash
# Buat virtual environment
python3 -m venv venv

# Aktivasi virtual environment
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Cara Menjalankan

### Via VSCode

1. Buka file `app.py`
2. Klik tombol **Run** di pojok kanan atas

### Via Terminal

```bash
python app.py
```

Aplikasi akan berjalan di: `http://127.0.0.1:5000/`

---

## 📂 Struktur Project

```
finalproject_risikostroke/
│
├── app.py                  # File utama aplikasi Flask
├── requirements.txt        # Daftar dependencies
├── README.md              # Dokumentasi project
├── models/                # Folder model ML
├── static/                # Folder CSS, JS, images
└── templates/             # Folder HTML templates
```

---

## 🛠️ Teknologi yang Digunakan

- **Python** - Bahasa pemrograman utama
- **Flask** - Web framework
- **Scikit-learn** - Machine learning library
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **HTML/CSS/JavaScript** - Frontend

---
