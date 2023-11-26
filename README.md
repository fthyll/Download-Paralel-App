Tentu, mari kita bahas programnya dalam Bahasa Indonesia dengan lebih rinci:

```python
import streamlit as st
import requests
import io
import os
from tqdm import tqdm
from urllib.parse import urlparse
import threading
```
Blok ini mengimpor library dan modul yang diperlukan. `streamlit` digunakan untuk membuat aplikasi web, `requests` untuk membuat permintaan HTTP, `io` untuk menangani aliran byte, `os` untuk berinteraksi dengan sistem operasi, `tqdm` untuk menampilkan batang kemajuan, dan `threading` untuk mengelola beberapa thread.

```python
def download_chunk(url, start_byte, end_byte, buffer):
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    response = requests.get(url, headers=headers, stream=True)
    buffer.write(response.content)
```
Blok ini mendefinisikan fungsi `download_chunk` yang mengunduh sebagian dari file yang ditentukan oleh argumen `url`, dimulai dari `start_byte` hingga `end_byte`. Konten yang diunduh ditulis ke `buffer` yang diberikan. Fungsi ini menggunakan header 'Range' dalam permintaan HTTP untuk mengunduh rentang byte tertentu.

```python
def download_with_progress(url, num_threads=4):
    response = requests.head(url)
    total_size = int(response.headers.get('content-length', 0))

    chunk_size = total_size // num_threads
    ranges = [(i * chunk_size, (i + 1) * chunk_size - 1) for i in range(num_threads - 1)]
    ranges.append(((num_threads - 1) * chunk_size, total_size - 1))

    content_buffers = [io.BytesIO() for _ in range(num_threads)]
```
Blok ini mendefinisikan fungsi `download_with_progress` yang memecah unduhan file menjadi beberapa bagian menggunakan beberapa thread. Ini mengambil ukuran total file, menghitung ukuran blok, dan membuat daftar rentang byte untuk setiap thread. `io.BytesIO()` digunakan untuk membuat buffer untuk setiap thread untuk menyimpan konten yang diunduh.

```python
    with st.progress(0) as progress_bar:
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=download_chunk, args=(url, ranges[i][0], ranges[i][1], content_buffers[i]))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        final_content = b"".join(buffer.getvalue() for buffer in content_buffers)
        st.progress(100)
```
Blok ini menyiapkan batang kemajuan menggunakan Streamlit (`st.progress(0)`) dan memulai beberapa thread untuk mengunduh blok yang berbeda secara bersamaan. Kemudian menunggu semua thread selesai (`thread.join()`) dan menggabungkan konten yang diunduh dari setiap buffer menjadi `final_content`. Terakhir, memperbarui batang kemajuan menjadi 100%.


```python
    return final_content, response.headers.get('Content-Type')
```
Blok ini mengembalikan konten yang diunduh akhir dan header 'Content-Type' dari tanggapan HTTP.

```python
def show_sidebar():
    # ... (Isi sidebar)
```
Blok ini mendefinisikan fungsi `show_sidebar` yang menyiapkan konten informasi dan panduan pengguna untuk sidebar dalam aplikasi Streamlit.

```python
def main():
    st.title("✨ Download Parallel ✨")

    show_sidebar()

    num_urls = st.number_input("🔽 Masukkan jumlah URL yang ingin diunduh 🔽", min_value=1, step=1, value=1)
    num_threads = st.number_input("🧬 Masukkan jumlah threads yang ingin digunakan 🧬", min_value=1, step=1, value=4)

    urls = []
    for i in range(num_urls):
        url = st.text_input(f"Masukkan URL ke-{i + 1}:")
        urls.append(url)
```
Blok ini mendefinisikan fungsi utama `main` untuk menyiapkan antarmuka aplikasi Streamlit. Ini mengambil masukan pengguna untuk jumlah URL dan thread, dan mengumpulkan URL dalam sebuah list.

```python
    if st.button("Mulai Unduh 🚀"):
        st.write("Proses unduh dimulai...")
        result_holder = {}
        for url in urls:
            content, content_type = download_with_progress(url, num_threads)
            save_file(url, content, content_type)

        st.write("Proses unduh selesai! 🎉")
```
Blok ini memeriksa apakah tombol "Mulai Unduh" diklik. Jika diklik, ini memulai proses unduh untuk setiap URL menggunakan jumlah thread yang ditentukan dan menyimpan file yang diunduh.

```python
def save_file(url, content, content_type):
    # ... (Fungsi untuk menyimpan file yang diunduh)
```
Blok ini mendefinisikan fungsi `save_file` yang menyimpan konten yang diunduh ke file. Ini menentukan ekstensi file berdasarkan header 'Content-Type', membuat direktori untuk file hasil, dan menyimpan file dengan nama yang sesuai.

```python
if __name__ == "__main__":
    main()
```
Blok ini memastikan bahwa fungsi `main()` dipanggil saat skrip dijalankan sebagai modul utama.

Secara keseluruhan, program ini merupakan aplikasi Streamlit untuk mengunduh file secara paralel menggunakan beberapa thread. Ini menyediakan antarmuka pengguna sederhana untuk memasukkan URL dan mengonfigurasi jumlah thread, dan menggunakan jumlah thread yang ditentukan untuk mengunduh sebagian file secara bersamaan. Konten yang diunduh kemudian disimpan ke file.

Untuk membuat user manual yang menjelaskan cara menggunakan `main.py`, Anda bisa membuat sebuah dokumen teks atau Markdown yang berisi langkah-langkah dan petunjuk penggunaan aplikasi. Berikut adalah contoh user manual:

---

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
git clone [URL repositori]
cd [nama folder]
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
3. Masukkan URL yang ingin diunduh pada kolom URL sesuai dengan jumlah yang dimasukkan pada langkah 1.

## Langkah 5: Mulai Unduh

Klik tombol "Mulai Unduh 🚀" untuk memulai proses unduh. Proses unduh akan ditampilkan dalam batang kemajuan. Tunggu hingga proses selesai.

## Langkah 6: Selesai

Setelah proses unduh selesai, file-file hasil unduhan akan disimpan dalam folder "result_file". Anda dapat menemukan file-file tersebut dengan ekstensi yang sesuai dengan tipe kontennya.

---

Gantilah `[URL repositori]` dan `[nama folder]` dengan URL repositori yang benar dan nama folder tempat Anda meng-clone repositori tersebut. Semoga ini membantu pengguna memahami cara menggunakan aplikasi Download Parallel ini.