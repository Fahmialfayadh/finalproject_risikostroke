# Stroke Risk Assessment Project Documentation

## 1. Project Overview
**Stroke Risk Calculator** adalah sistem pakar berbasis web untuk estimasi risiko stroke dini. Proyek ini dikembangkan sebagai pemenuhan **Tugas Akhir Mata Kuliah Matematika Diskrit semester 1**.

### Latar Belakang & Tim
Aplikasi ini bertujuan menjembatani kesenjangan antara model statistik kompleks dan penggunaan klinis yang mudah dipahami.
**Tim Pengembang:**
1. Fahmi Alfayadh (5054251015)
2. Evina Fitriyani (5054251013)
3. Aziz Rahmad Arifin (5054251002)

---

## 2. Arsitektur Sistem (System Architecture)

### Technology Stack
*   **Backend Framework**: Python Flask 3.0.3 (Microframework dengan pola Blueprint)
*   **Database**: SQLite (Relational DB) dengan ORM SQLAlchemy 2.0
*   **Cryptography Engine**: PyCryptodome (AES, DES, RC4) & Werkzeug Security (scrypt)
*   **Template Engine**: Jinja2 (Server-side rendering)
*   **PDF Engine**: ReportLab (Programmatic PDF generation)

### Struktur Direktori
```text
/finalproject_risikostroke
├── app.py                  # Entry Point & Konfigurasi Flask
├── stroke_model.py         # Logika Model Inferensi (WOE & Regresi Logistik)
├── routes/                 # Modul Routing (Blueprint)
│   ├── public.py           # Endpoint Publik (/, /calculator, /predict, /download_pdf)
│   ├── auth.py             # Autentikasi Pengguna (/login, /register, /logout)
│   ├── user.py             # Riwayat Pasien Terdaftar (/user/history, /user/view)
│   └── admin.py            # Panel Pengelolaan Admin (/admin, /admin/view, /admin/delete)
├── models/                 # Database Schema (User, StrokeRecord)
│   ├── user.py             # Entitas Pengguna
│   └── strokerecord.py     # Entitas Rekam Medis Terenkripsi
├── db/                     # Inisialisasi Database Base
├── crypto/                 # Modul Kriptografi
│   ├── cipher/             # Primitif Algoritma (AES, DES, RC4, Base Crypto)
│   └── operations/         # Abstraksi Enkripsi, Dekripsi, dan Parsing Payload
├── utils.py                # Algoritma Rekursif (Merge Sort & Linear Search)
├── assets/messages/        # Lokalisasi Bahasa (ID/EN)
├── pdf_generator/          # Pembangkit Laporan PDF
└── templates/              # Antarmuka Pengguna (Jinja2 HTML)
```

---

## 3. Detail Implementasi Basis Data (`models/`)

Aplikasi menggunakan **SQLAlchemy 2.0** dengan sintaks deklaratif modern (`Mapped` dan `mapped_column`) untuk pemodelan data relasional pada SQLite.

### A. Schema: `User` (`users`)
Tabel untuk autentikasi dan otorisasi pengguna aplikasi.

| Field | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Primary Key, Auto-increment. |
| `username` | String(50) | Nama pengguna unik, Not Null. |
| `password` | String(255) | Hash kata sandi menggunakan algoritma `scrypt`. |

### B. Schema: `StrokeRecord` (`stroke_records`)
Tabel untuk menyimpan rekam medis hasil estimasi risiko dengan pengamanan data sensitif.

| Field | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Primary Key, Auto-increment. |
| `user_id` | Integer (FK) | Foreign Key merujuk ke `users.id` (Nullable untuk tamu). |
| `encrypted_payload` | **Text** | **Ciphertext Base64** dari data klinis pasien yang terenkripsi. |
| `risk_score` | Float | Hasil kalkulasi probabilitas model (0.0 - 1.0) dengan indeks. |
| `created_at` | DateTime | Waktu pencatatan data pasien. |

> **Technical Decision (Encrypted Payload Pattern)**: 
> Seluruh atribut klinis pasien (`name`, `age`, `glucose`, `smoking`, `hypertension`, `bmi`, dll.) diserialisasi ke dalam format JSON dan dienkripsi menjadi satu kesatuan string ciphertext yang disimpan di kolom `encrypted_payload`. 
> Kolom `risk_score` sengaja disimpan terpisah dengan `index=True` agar proses pengurutan (*sorting*) risiko stroke di tabel admin dan riwayat pengguna dapat dieksekusi langsung pada level kueri basis data tanpa beban komputasi dekripsi penuh di awal.

---

## 4. Modul Kriptografi & Keamanan Data (`crypto/`)

Untuk melindungi kerahasiaan data rekam medis saat berada di media penyimpanan (*Data at Rest*), sistem menyediakan modul kriptografi simetris berbasis Object-Oriented Programming (OOP) yang mendukung tiga algoritma berbeda.

### A. Algoritma Kriptografi yang Didukung

1. **AES (Advanced Encryption Standard)**
   - Ukuran blok: 128 bit (16 byte).
   - Mode operasi: **CBC (Cipher Block Chaining)**.
   - Padding: PKCS#7.
   - Vektor Inisialisasi: IV dinamis 16 byte acak (`os.urandom(16)`).
   - Format keluaran: `Base64(IV + Ciphertext)`.

2. **DES (Data Encryption Standard)**
   - Ukuran blok: 64 bit (8 byte).
   - Mode operasi: **CBC (Cipher Block Chaining)**.
   - Padding: PKCS#7.
   - Vektor Inisialisasi: IV dinamis 8 byte acak (`os.urandom(8)`).
   - Format keluaran: `Base64(IV + Ciphertext)`.

3. **RC4 (Rivest Cipher 4)**
   - Kategori: **Stream Cipher** (enkripsi berbasis byte kontinu).
   - Mode operasi: Tidak menggunakan mode operasi blok (bekerja via PRGA/KSA keystream XOR).
   - Padding & IV: Tanpa padding dan tanpa IV.
   - Format keluaran: `Base64(Ciphertext)`.

### B. Alur Enkripsi dan Dekripsi Data

```text
[Input Data Pasien]
        │
        ▼ (json.dumps)
[Plaintext JSON]
        │
        ▼ (Enkripsi Simetris: AES-CBC / DES-CBC / RC4)
[Raw Ciphertext Bytes]
        │
        ▼ (base64.b64encode)
[Base64 String Payload] ──> Disimpan ke stroke_records.encrypted_payload
```

Proses dekripsi membalikkan alur tersebut: mendekode Base64, mengekstrak IV (untuk AES/DES), mendekripsi ciphertext, dan mem-parsing kembali string JSON menjadi dictionary Python. Jika terjadi inkonsistensi kunci atau algoritma, sistem menerapkan penanganan eksepsi bertingkat (*graceful fallback*) agar sistem tidak mengalami *unhandled exception*.

### C. Keamanan Kredensial Pengguna
Kata sandi pengguna tidak disimpan dalam bentuk teks biasa maupun hash sederhana (MD5/SHA1). Sistem menggunakan implementasi fungsi derivasi kunci **`scrypt`** via `werkzeug.security` (`generate_password_hash` dan `check_password_hash`) yang memiliki ketahanan tinggi terhadap serangan *brute-force* berbasis GPU.

---

## 5. Algoritma & Logika Komputasi (`utils.py`)

Sebagai pemenuhan kompetensi Matematika Diskrit, sistem mengimplementasikan algoritma pengurutan dan pencarian secara manual tanpa bergantung pada fungsi bawaan Python `list.sort()`.

### A. Merge Sort Algorithm ($O(n \log n)$)
Digunakan pada tabel Admin dan Riwayat Pengguna untuk fitur **Sort by Risk Score** dan atribut lainnya.

**Implementasi Code:**
```python
# utils.py
def merge_sort(records, key, reverse=False):
    if len(records) <= 1: 
        return records  # Base Case
    
    mid = len(records) // 2
    left = merge_sort(records[:mid], key, reverse)   # Recursive Left
    right = merge_sort(records[mid:], key, reverse)  # Recursive Right
    
    return merge(left, right, key, reverse)          # Merge Step
```

**Logika `merge`:**
Fungsi `merge` menggunakan dua pointer (`i` dan `j`) untuk membandingkan elemen dari list kiri dan list kanan. Atribut dinamis diekstrak menggunakan `getattr(obj, key)` untuk memastikan algoritma dapat mengurutkan objek berdasarkan atribut numerik maupun teks secara fleksibel.

### B. Linear Search Algorithm ($O(n)$)
Digunakan untuk pencarian nama pasien pada data yang telah didekripsi di memori.
```python
# utils.py
def search(records, query, fields):
    query = query.lower()
    filtered = []
    for record in records:
        for field in fields:
            value = str(getattr(record, field, "") or "").lower()
            if query in value:
                filtered.append(record)
                break
    return filtered
```

---

## 6. Inti Model Prediksi (`stroke_model.py`)

Parameter model inferensi (koefisien regresi logistik dan tabel bobot WOE) dipisahkan secara modular ke dalam [`stroke_model.py`](file:///home/data/kuliah/rka/matdis/finalproject_risikostroke/finalproject_risikostroke/stroke_model.py) untuk memastikan independensi antara antarmuka web dan logika komputasi statistik.

### Konsep: Weight of Evidence (WOE)
Metode ini mentransformasi variabel kontinu dan kategorik menjadi nilai numerik standar yang mencerminkan bobot risiko statistik.

**Contoh Mapping Data:**
1.  Input Usia: `Age = 62`
2.  **Binning Function**:
    ```python
    def age_bin(a):
        if a < 40: return "0-40"
        if a < 55: return "40-55"
        if a < 70: return "55-70"
        return "70+"
    ```
3.  **Tabel WOE**:
    ```python
    woe_age = {"0-40": -2.608643, "40-55": -0.624399, "55-70": 0.569374, "70+": 1.452558}
    ```
    Kategori `"55-70"` memetakan nilai bobot `0.569374`.

### Rumus Matematika (Logistic Regression)
Probabilitas stroke $P(Y=1)$ dihitung menggunakan fungsi sigmoid:

$$ P(Y=1) = \frac{1}{1 + e^{-z}} $$

Dimana $z$ adalah kombinasi linear dari bias/intercept ($\beta_0$) dan perkalian koefisien fitur ($\beta_i$) dengan nilai bobot WOE ($X_{woe,i}$):

$$ z = \beta_0 + \sum_{i=1}^{n} (\beta_i \cdot X_{woe,i}) $$

**Implementasi Komputasi:**
```python
# stroke_model.py
z = intercept
contrib = {}
for k in coef:
    c = coef[k] * woe_values[k]
    contrib[k] = c
    z += c

prob = 1 / (1 + math.exp(-z))
```

### Ambang Batas Klasifikasi Risiko
Klasifikasi risiko stroke dibagi menjadi tiga kategori tingkat keparahan:
1.  **Low Risk**: Probabilitas $< 0.08$
2.  **Moderate Risk**: Probabilitas $0.08 \le P < 0.20$
3.  **High Risk**: Probabilitas $\ge 0.20$

---

## 7. Layanan Pendukung

### A. Lokalisasi Bahasa (I18N)
Kamus multi-bahasa (Indonesia dan Inggris) dikelola di [`assets/messages/messages.py`](file:///home/data/kuliah/rka/matdis/finalproject_risikostroke/finalproject_risikostroke/assets/messages/messages.py). Helper `t(key)` didaftarkan melalui `@app.context_processor` sehingga seluruh template HTML dapat merender teks antarmuka sesuai pilihan bahasa pengguna pada sesi aktif.

### B. Pembuatan Laporan PDF
Modul [`pdf_generator/`](file:///home/data/kuliah/rka/matdis/finalproject_risikostroke/finalproject_risikostroke/pdf_generator) menggunakan pustaka ReportLab untuk menghasilkan dokumen ringkasan hasil kalkulasi risiko secara instan tanpa menyimpan file statis di server (*in-memory streaming*).

---

## 8. Panduan Instalasi & Pengoperasian

1.  **Kloning Repositori**
    ```bash
    git clone https://github.com/Fahmialfayadh/finalproject_risikostroke.git
    cd finalproject_risikostroke
    ```

2.  **Pemasangan Dependensi**
    Disarankan menggunakan `uv` pada lingkungan Linux:
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```

3.  **Konfigurasi Lingkungan (`.env`)**
    Buat file `.env` pada direktori utama aplikasi:
    ```env
    ADMIN_USERNAME=sangadmin
    ENCRYPTION_METHOD=AES
    ENCRYPTION_KEY=1234567890123456
    ```

4.  **Menjalankan Aplikasi**
    ```bash
    python app.py
    ```
    Aplikasi dapat diakses melalui peramban web pada alamat `http://127.0.0.1:5000`.
