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
*   **Backend Framework**: Python Flask 3.0.3 (Microframework)
*   **Database**: SQLite (Relational DB) dengan ORM SQLAlchemy
*   **Template Engine**: Jinja2 (Server-side rendering)
*   **PDF Engine**: ReportLab (Programmatic PDF generation)

### Struktur Direktori
```text
/finalproject_risikostroke
├── app.py              # Controller & Model Logic Logic
├── models.py           # Database Schema
├── utils.py            # Algoritma (Sorting & Searching)
├── messages.py         # Localization (ID/EN)
├── pdf_generator.py    # Report Generation
└── templates/          # Views (HTML)
```

---

## 3. Detail Implementasi Database (`models.py`)

Aplikasi menggunakan **SQLAlchemy** sebagai ORM (Object Relational Mapper) untuk berinteraksi dengan database SQLite. Schema utama didefinisikan dalam class `StrokeInput`.

### Schema: `StrokeInput`
Tabel ini menyimpan riwayat input pengguna beserta hasil prediksinya.

| Field | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Primary Key, Auto-increment. |
| `name`, `age`, `gender` | String/Integer | Data demografis dasar. |
| `hypertension`, `heart_disease` | Integer (0/1) | Komorbiditas (biner). |
| `glucose`, `bmi` | Float | Data fisiologis kontinu. |
| `prediction` | Float | **Hasil kalkulasi model** (Probabilitas 0.0 - 1.0). |
| `bins` | **Text (JSON)** | Menyimpan kategori hasil binning (e.g. `["40-55", "Normal", ...]`) |
| `contrib` | **Text (JSON)** | Menyimpan nilai kontribusi per fitur untuk debugging/audit model. |

> **Technical Decision**: Field `bins` dan `contrib` disimpan sebagai **JSON String** (tipe `db.Text`) daripada tabel terpisah (relasi One-to-Many). Hal ini dipilih untuk performa (mengurangi JOIN query) karena data tersebut bersifat *read-only* setelah disimpan dan hanya digunakan untuk tampilan laporan.

---

## 4. Algoritma & Logika Komputasi (`utils.py`)

Sebagai proyek Matematika Diskrit, aplikasi ini mengimplementasikan algoritma dasar secara manual tanpa bergantung pada fungsi bawaan Python `list.sort()`.

### A. Merge Sort Algorithm ($O(n \log n)$)
Digunakan di panel Admin untuk fitur **Sort by Risk Score**. Algoritma ini dipilih karena stabilitasnya dan kompleksitas waktu rata-rata yang konsisten.

**Implementasi Code:**
```python
# utils.py
def merge_sort(records, key, reverse=False):
    if len(records) <= 1: return records  # Base Case
    
    mid = len(records) // 2
    left = merge_sort(records[:mid], key, reverse)   # Recursive Left
    right = merge_sort(records[mid:], key, reverse)  # Recursive Right
    
    return merge(left, right, key, reverse)          # Merge Step
```

**Logika `merge`:**
Fungsi `merge` menggunakan dua pointer (`i` dan `j`) untuk membandingkan elemen dari list kiri dan kanan.
*   Fitur unik: Menggunakan `getattr(obj, key)` untuk memungkinkan pengurutan dinamis berdasarkan atribut apapun (misal: urutkan by `age` atau by `prediction`).

### B. Linear Search Algorithm ($O(n)$)
Digunakan untuk fitur pencarian nama pasien.
```python
# utils.py
def search(records, query, fields):
    # ...
    for record in records:
        for field in fields:
            # Case-insensitive partial match
            if query in str(getattr(record, field)).lower():
                filtered.append(record)
                break
```
Algoritma ini melakukan iterasi sekuensial pada setiap record. Meskipun $O(n)$, ini cukup efisien untuk dataset ribuan baris yang digunakan dalam lingkup proyek ini.

---

## 5. Inti Model Prediksi (`app.py`)

Aplikasi ini **tidak memuat model machine learning eksternal** (.pkl/.h5) saat runtime. Sebaliknya, parameter model (koefisien dan bins) di-*hardcode* ke dalam aplikasi untuk kecepatan eksekusi ekstrem.

### Konsep: Weight of Evidence (WOE)
Metode ini mentransformasi variabel kontinu menjadi kategori diskrit yang memiliki bobot risiko tertentu. 

**Contoh Mapping Data:**
1.  User Input: `Age = 62`
2.  **Binning Function** (`app.py`):
    ```python
    if a < 70: return "55-70"
    ```
3.  **Dictionary Lookup**:
    ```python
    woe_age = {..., "55-70": 0.569374, ...}
    ```
    Nilai `0.569374` diambil sebagai input model.

### Rumus Matematika (Logistic Regression)
Probabilitas stroke $P$ dihitung menggunakan fungsi sigmoid standar:

$$ P(Y=1) = \frac{1}{1 + e^{-z}} $$

Dimana $z$ adalah kombinasi linear dari Koefisien ($\beta$) dan WOE ($X_{woe}$):

$$ z = \beta_0 + \sum_{i=1}^{n} (\beta_i \cdot X_{woe,i}) $$

**Implementasi Python (`calc` function):**
```python
# app.py
z = intercept
for k in coef:
    # Mengalikan Bobot Fitur (Coef) dengan Bobot Data (WOE)
    c = coef[k] * woe_values[k]
    z += c

prob = 1 / (1 + math.exp(-z))
```
Pendekatan manual ini memungkinkan transparansi penuh—kita tahu persis *berapa* kontribusi setiap faktor (misal: merokok menyumbang +0.5 ke skor z) yang kemudian ditampilkan di PDF report.

### Hybrid Thresholding
Klasifikasi risiko menggunakan dua titik potong (cut-off points):
1.  **Lower Bound (0.10)**: Diambil dari statistik klinis (populasi sehat).
2.  **Upper Bound (0.4545)**: Diambil dari Youden Index kurva ROC model.

---

## 6. Fitur Administratif & Keamanan

### Session Management
Login admin tidak menggunakan database user, melainkan *environment variable* tunggal untuk kesederhanaan deployment prototyping.
```python
# app.py
if pw == os.environ["ADMIN_PASSWORD"]:
    session["admin"] = True
```
Middleware check diterapkan pada setiap route admin (`/admin`, `/admin/delete`) untuk mencegah akses tanpa otorisasi.

### Localization
Fitur multi-bahasa menggunakan dictionary statis di `messages.py`. Helper function `t(key)` disuntikkan ke konteks template Jinja2 via `@app.context_processor`, memungkinkan pemanggilan `{{ t('home_title') }}` langsung di HTML.

---

## 7. Instruksi Instalasi

1.  **Clone Repository**
    ```bash
    git clone https://github.com/Fahmialfayadh/finalproject_risikostroke.git
    cd finalproject_risikostroke
    ```
2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Setup Environment**
    Buat file `.env` di root folder:
    ```env
    ADMIN_PASSWORD=admin123
    ```
4.  **Jalankan Server**
    ```bash
    python app.py
    ```
    Akses di `localhost:5000`.

---
