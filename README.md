# User Manual - Aplikasi Download Parallel

Selamat datang di Aplikasi Download Parallel! Aplikasi ini memungkinkan Anda mengunduh file secara paralel menggunakan beberapa thread sekaligus. Berikut adalah langkah-langkah untuk menggunakan aplikasi ini:

## Persyaratan

Sebelum memulai, pastikan Anda memiliki Python terinstal di sistem Anda. Anda juga perlu menginstal beberapa pustaka yang dibutuhkan dengan menjalankan perintah berikut:

```bash
pip install streamlit requests tqdm
```

## Langkah 1: Clone Repositori

Clone repositori ini ke komputer Anda menggunakan perintah Git berikut:

```bash
git clone [URL https://github.com/fthyll/Download-Paralel-App]
cd [nama Download Paralel App]
```

## Langkah 2: Install Dependensi

Pastikan dependensi yang diperlukan telah diinstal dengan menjalankan perintah berikut:

```bash
pip install -r requirements.txt
```

## Langkah 3: Jalankan Aplikasi

Jalankan aplikasi dengan perintah:

```bash
streamlit run main.py
```

## Langkah 4: Pengaturan

1. Masukkan jumlah URL yang ingin diunduh.
2. Masukkan jumlah thread yang ingin digunakan.
3. Masukkan URL yang ingin diunduh pada kolom URL sesuai dengan jumlah yang dimasukkan pada langkah 1

## Langkah 5: Mulai Unduh

Klik tombol "Mulai Unduh 🚀" untuk memulai proses unduh. Proses unduh akan ditampilkan dalam batang kemajuan. Tunggu hingga proses selesai.

## Langkah 6: Selesai

Setelah proses unduh selesai, file-file hasil unduhan akan disimpan dalam folder "result_file". Anda dapat menemukan file-file tersebut dengan ekstensi yang sesuai dengan tipe kontennya.
