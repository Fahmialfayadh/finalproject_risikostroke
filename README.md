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

## 🚀 Cara Install dan Jalankan Aplikasi

### **LANGKAH 1: Download Project**

Buka **Command Prompt** atau **Terminal**, lalu ketik:

```bash
git clone https://github.com/Fahmialfayadh/finalproject_risikostroke.git
cd finalproject_risikostroke
```

**Penjelasan:**
- Perintah pertama = download project dari GitHub
- Perintah kedua = masuk ke folder project

---

### **LANGKAH 2: Buka Project di VSCode**

#### **Cara 1 (Langsung buka):**

Kalau sudah di dalam folder project, ketik:

```bash
code .
```

#### **Cara 2 (Manual):**

1. Buka aplikasi **VSCode**
2. Klik **File** → **Open Folder**
3. Pilih folder `finalproject_risikostroke`
4. Klik **Select Folder**

---

### **LANGKAH 3: Install Python Libraries**

Di dalam VSCode, buka **Terminal** (Menu: Terminal → New Terminal), lalu ketik:

```bash
pip install -r requirements.txt
```

**Kalau muncul error "pip not found" atau gagal install:**

```bash
python -m pip install -r requirements.txt
```

**Kalau masih error, pakai virtual environment:**

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

### **LANGKAH 4: Jalankan Aplikasi**

#### **Cara 1 (Pakai Terminal di VSCode):**

Ketik perintah ini di Terminal:

```bash
python app.py
```

Tunggu sampai muncul tulisan seperti ini:

```
* Running on http://127.0.0.1:5000
```

Lalu buka browser dan ketik: **http://127.0.0.1:5000**

#### **Cara 2 (Pakai Tombol Run di VSCode):**

1. Buka file **app.py**
2. Klik tombol **▶ Run** di pojok kanan atas
3. Tunggu sampai aplikasi jalan
4. Buka browser: **http://127.0.0.1:5000**

---

### **LANGKAH 5: Stop Aplikasi**

Untuk stop aplikasi, tekan **Ctrl + C** di Terminal

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

## 👨‍💻 Developer

**Final Project – Rekayasa Kecerdasan Artifisial**

Dikembangkan oleh:
- **Fahmialfayadh**
- **Team**

---

## 📝 Lisensi

Project ini dibuat untuk keperluan akademik Final Project mata kuliah Rekayasa Kecerdasan Artifisial.

---

## 📞 Kontak

Jika ada pertanyaan atau masalah, silakan hubungi developer melalui:
- GitHub: [@Fahmialfayadh](https://github.com/Fahmialfayadh)

---

**© 2024 - Aplikasi Prediksi Risiko Stroke**
