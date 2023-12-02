### Import Module

```python
import streamlit as st
import requests
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import time
from multiprocessing import cpu_count
```

1. `import streamlit as st`: Ini mengimpor modul Streamlit yang digunakan untuk membuat antarmuka pengguna web dengan mudah.

2. `import requests`: Digunakan untuk membuat permintaan HTTP ke server, misalnya untuk mengunduh data dari internet.

3. `import os`: Modul ini menyediakan antarmuka dengan sistem operasi, dan sering digunakan untuk manipulasi file dan direktori.

4. `from urllib.parse import urlparse`: Digunakan untuk mem-parsing URL, membantu dalam ekstraksi informasi dari URL seperti domain, path, dan lainnya.

5. `from concurrent.futures import ThreadPoolExecutor, as_completed`: Membawa modul yang mendukung eksekusi paralel menggunakan pool utas (threads) untuk meningkatkan kinerja.

6. `import io`: Modul input/output standar Python, sering digunakan untuk bekerja dengan data biner menggunakan `BytesIO` atau data teks menggunakan `StringIO`.

7. `import time`: Modul ini memberikan fungsi-fungsi waktu, yang dapat digunakan untuk mengukur berapa lama suatu operasi memakan waktu.

8. `from multiprocessing import cpu_count`: Digunakan untuk mendapatkan jumlah core CPU yang tersedia pada sistem.

### Fungsi `download_chunk`

Fungsi `download_chunk` ini sepertinya merupakan bagian dari suatu kode yang bertujuan untuk mengunduh data dari suatu URL secara terpisah (dalam bentuk chunk atau bagian-bagian) dengan menggunakan HTTP Range Requests. Mari kita bahas satu per satu:

```python
def download_chunk(url, start_byte, end_byte, buffer, total_size, progress_list):
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    response = requests.get(url, headers=headers, stream=True)
```

1. `def download_chunk(url, start_byte, end_byte, buffer, total_size, progress_list):`: Ini adalah deklarasi fungsi dengan nama `download_chunk` yang menerima beberapa parameter: `url` (URL sumber data), `start_byte` (byte awal dari chunk), `end_byte` (byte akhir dari chunk), `buffer` (objek buffer untuk menulis data), `total_size` (ukuran total file yang akan diunduh), dan `progress_list` (daftar untuk menyimpan kemajuan unduhan).

2. `headers = {'Range': f'bytes={start_byte}-{end_byte}'}:`: Membuat header HTTP dengan menggunakan Range Request, yang memungkinkan kita untuk meminta server hanya mengirimkan bagian tertentu dari file (dalam hal ini, byte dari `start_byte` hingga `end_byte`).

3. `response = requests.get(url, headers=headers, stream=True)`: Menggunakan modul `requests` untuk mengirim permintaan HTTP GET ke URL dengan menggunakan header yang telah dibuat. Argumen `stream=True` digunakan agar data diunduh dalam bentuk streaming.

```python
    chunk_size = end_byte - start_byte + 1
    buffer.write(response.content)
```

4. `chunk_size = end_byte - start_byte + 1`: Menghitung ukuran chunk yang diunduh dengan mengurangkan byte awal dari byte akhir dan menambahkan 1. Ini memberikan panjang sebenarnya dari data yang diunduh.

5. `buffer.write(response.content)`: Menulis data yang diunduh ke dalam objek buffer (`buffer`). `response.content` berisi data yang diambil dari server sebagai respons terhadap permintaan HTTP.

```python
    progress = (start_byte + chunk_size) / total_size
    progress_list.append(progress)
```

6. `progress = (start_byte + chunk_size) / total_size`: Menghitung persentase kemajuan unduhan dan menyimpannya dalam variabel `progress`. Persentase ini dihitung dengan membagi jumlah byte yang sudah diunduh (`start_byte + chunk_size`) dengan ukuran total file.

7. `progress_list.append(progress)`: Menambahkan nilai kemajuan (`progress`) ke dalam daftar kemajuan (`progress_list`). Ini dapat digunakan untuk memantau kemajuan unduhan secara keseluruhan.

### 3 Fungsi `download_with_progress`
Fungsi `download_with_progress` ini sepertinya merupakan implementasi dari unduhan paralel dengan menggunakan beberapa thread untuk meningkatkan kecepatan unduhan. Mari kita jelaskan baris per baris:

```python
def download_with_progress(url, num_threads=None, max_threads=8):
    if num_threads is None:
        num_threads = min(cpu_count(), max_threads)  # Use min to limit the threads to max_threads
```

1. Menentukan jumlah thread yang akan digunakan. Jika `num_threads` tidak diberikan (None), maka akan digunakan jumlah thread yang sama dengan jumlah core CPU, dengan batasan maksimum `max_threads`.

```python
    if num_threads > max_threads:
        st.warning(f"Number of threads ({num_threads}) exceeds the maximum allowed (8). Using 8 threads instead.")
        num_threads = max_threads
```

2. Memeriksa apakah jumlah thread yang diminta (`num_threads`) melebihi batas maksimum (`max_threads`). Jika iya, akan memberikan peringatan dan menggunakan jumlah thread maksimum yang diizinkan (8).

```python
    response = requests.head(url)
    total_size = int(response.headers.get('content-length', 0))
```

3. Mengirim permintaan `HEAD` ke server untuk mendapatkan informasi header, terutama ukuran total file yang akan diunduh.

```python
    chunk_size = total_size // num_threads
    ranges = [(i * chunk_size, (i + 1) * chunk_size - 1) for i in range(num_threads - 1)]
    ranges.append(((num_threads - 1) * chunk_size, total_size - 1))
```

4. Menghitung ukuran setiap chunk berdasarkan jumlah thread yang dipilih (`num_threads`). Kemudian, menghasilkan daftar `ranges` yang menentukan rentang byte untuk setiap chunk.

```python
    content_buffers = [io.BytesIO() for _ in range(num_threads)]
```

5. Membuat objek buffer (`BytesIO`) sebanyak jumlah thread yang dipilih.

```python
    progress_list = []
```

6. Membuat daftar kosong untuk menyimpan kemajuan unduhan.

```python
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []

        for i in range(num_threads):
            future = executor.submit(download_chunk, url, ranges[i][0], ranges[i][1], content_buffers[i], total_size, progress_list)
            futures.append(future)

        for future in as_completed(futures):
            future.result()
```

7. Menggunakan `ThreadPoolExecutor` untuk menjalankan fungsi `download_chunk` pada setiap thread. Setiap thread akan mendownload bagian file yang berbeda dan menyimpannya di objek buffer yang sesuai.

```python
    final_content = b"".join(buffer.getvalue() for buffer in content_buffers)

    return final_content, response.headers.get('Content-Type'), progress_list
```

8. Menggabungkan semua bagian yang diunduh dari setiap thread menjadi satu konten (`final_content`). Selanjutnya, mengembalikan konten, tipe konten (Content-Type), dan daftar kemajuan unduhan.

### 4 Fungsi `save_file`
Fungsi `save_file` ini bertujuan untuk menyimpan konten yang diunduh dari suatu URL ke dalam sebuah file di direktori target. Berikut adalah penjelasan baris per baris:

```python
def save_file(url, content, content_type, target_directory):
    if content_type:
        extension = content_type.split('/')[-1]
    else:
        extension = 'unknown'
```

1. Mengekstrak ekstensi file dari tipe konten (`content_type`). Jika tipe konten tidak ada (`content_type` adalah `None`), maka ekstensinya diatur sebagai 'unknown'.

```python
    os.makedirs(target_directory, exist_ok=True)
```

2. Membuat direktori target jika belum ada. Argumen `exist_ok=True` memastikan bahwa tidak akan ada kesalahan jika direktori tersebut sudah ada.

```python
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
```

3. Mengurai URL menggunakan `urlparse` dan mendapatkan nama file dari path URL menggunakan `os.path.basename`.

```python
    filename = filename.replace('%20', ' ')
```

4. Mengganti karakter '%20' (yang mewakili spasi dalam URL yang di-kode) dengan spasi.

```python
    if '.' in filename:
        parts = filename.split('.')
        filename = '.'.join(parts[:-1])
```

5. Memeriksa apakah ada ekstensi file dalam nama file. Jika ada, menghapus ekstensinya sehingga dapat diganti dengan ekstensi yang diperoleh sebelumnya dari tipe konten.

```python
    with open(os.path.join(target_directory, f"{filename}.{extension}"), "wb") as f:
        f.write(content)
```

6. Membuka file untuk ditulis di direktori target dengan nama yang telah dibuat dan ekstensi yang sudah diambil. Menulis konten yang diunduh ke dalam file tersebut dalam mode binary (`"wb"`).

### 5 Fungsi `show_sidebar`
Fungsi `show_sidebar` ini sepertinya bertujuan untuk menampilkan informasi dan panduan pengguna di sidebar antarmuka pengguna web Streamlit. Berikut adalah penjelasan setiap bagian:

```python
def show_sidebar():
    st.sidebar.title("📚 About this project 📚")
    st.sidebar.write("Project ini ditujukan untuk memenuhi tugas besar mata kuliah Sistem Paralel Dan Terdistribusi.")
    st.sidebar.write("Pada project ini Anda dapat melakukan unduh file dengan menggunakan beberapa thread sekaligus.")
```

1. Menampilkan judul dan deskripsi proyek di sidebar. Memberikan informasi umum tentang tujuan proyek dan fungsionalitasnya.

```python
    st.sidebar.subheader("User Manual 📖")
    st.sidebar.write("1. Masukkan URL yang ingin diunduh pada kolom URL")
    st.sidebar.write("2. Masukkan jumlah thread yang ingin digunakan pada kolom Thread")
    st.sidebar.write("3. Klik tombol Mulai Unduh untuk memulai proses unduh")
```

2. Menampilkan subjudul dan panduan pengguna di sidebar. Memberikan langkah-langkah yang harus diikuti oleh pengguna untuk menggunakan aplikasi.

```python
    st.sidebar.subheader("Author 📝")
    st.sidebar.markdown("**Karina Khairunnisa Putri (1301213106)**")
    st.sidebar.write("Diandra Lintang Hanintya (1301213072)")
    st.sidebar.write("Naufal Hilmi Majid (1301213430)")
    st.sidebar.write("Muhammad Fatih Yumna Lajuwirdi Lirrahman (1301213389)")
    st.sidebar.write("Benito Raymond (1301213345)")
```

3. Menampilkan informasi tentang penulis atau tim pengembang proyek di sidebar.

```python
    st.sidebar.subheader("Find us at 🔎")
    st.sidebar.button("Github", key="github")
```

4. Menampilkan subjudul dan tombol di sidebar. Tombol ini mungkin berfungsi sebagai tautan ke halaman GitHub proyek.

### 6 Fungsi `main`

Fungsi `main` ini adalah fungsi utama dari program yang menggunakan Streamlit untuk membuat antarmuka pengguna web. Berikut adalah penjelasan setiap bagian:

```python
def main():
    st.title("✨ MultiFetch Download Manager ✨")
```

1. Menampilkan judul pada antarmuka pengguna menggunakan `st.title`.

```python
    show_sidebar()
```

2. Menampilkan sidebar menggunakan fungsi `show_sidebar` yang telah dijelaskan sebelumnya.

```python
    num_urls = st.number_input("🔗 Masukkan jumlah URL yang ingin diunduh 🔗", min_value=1, step=1, value=1)
    num_threads = st.number_input("🧬 Masukkan jumlah threads yang ingin digunakan 🧬", min_value=1, step=1, value=4)

    target_directory = st.text_input("📂 Pilih direktori penyimpanan file (e.g., result_files):", "result_files")
```

3. Menggunakan elemen-elemen antarmuka pengguna Streamlit (`st.number_input` dan `st.text_input`) untuk mengumpulkan input dari pengguna seperti jumlah URL yang ingin diunduh, jumlah thread yang ingin digunakan, dan direktori penyimpanan file.

```python
    urls = []
    for i in range(num_urls):
        url = st.text_input(f"Masukkan URL ke-{i + 1}:")
        urls.append(url)
```

4. Menggunakan loop untuk mengumpulkan URL yang ingin diunduh dari pengguna.

```python
    if st.button("Mulai Unduh 🚀"):
        st.write("Proses unduh dimulai...")

        start_time = time.time()

        all_content = []
        all_content_types = []
        all_progress_lists = []

        for url in urls:
            content, content_type, progress_list = download_with_progress(url, num_threads)
            all_content.append(content)
            all_content_types.append(content_type)
            all_progress_lists.append(progress_list)

        for i, url in enumerate(urls):
            content = all_content[i]
            content_type = all_content_types[i]
            progress_list = all_progress_lists[i]
            save_file(url, content, content_type, target_directory)

            for progress in progress_list:
                st.progress(progress)

        end_time = time.time()
        elapsed_time = end_time - start_time

        st.success(f"Proses unduh selesai! 🎉 Waktu yang diperlukan: {elapsed_time:.2f} detik ⌛️")
        st.write(f"File-file disimpan di: {os.path.abspath(target_directory)}")
```

5. Mengeksekusi unduhan dan penyimpanan file menggunakan fungsi `download_with_progress` dan `save_file`. Menampilkan kemajuan unduhan menggunakan elemen antarmuka `st.progress`. Memberikan informasi ke pengguna setelah selesai, termasuk waktu yang diperlukan dan direktori penyimpanan file.

### 7 Bagian `if __name__ == "__main__":`

Bagian `if __name__ == "__main__":` merupakan bagian terakhir dari skrip Python yang umumnya digunakan untuk mengeksekusi fungsi `main()` ketika skrip dijalankan secara langsung. 

```python
if __name__ == "__main__":
    main()
```

Penjelasannya:

1. `__name__` adalah sebuah variabel khusus dalam Python yang memuat string yang menunjukkan nama dari module atau script saat ini.

2. Pernyataan `if __name__ == "__main__":` berarti kode di dalam blok ini hanya akan dieksekusi jika skrip dijalankan langsung (bukan di-import sebagai modul oleh skrip lain).

3. Ketika skrip dijalankan, `__name__` akan menjadi string `"__main__"` sehingga blok ini akan dieksekusi.

4. Dalam konteks ini, fungsi `main()` akan dijalankan ketika skrip dijalankan secara langsung, sehingga aplikasi akan memulai eksekusi dari fungsi `main()`.