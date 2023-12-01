```python
    import streamlit as st
    import requests
    import os
    from urllib.parse import urlparse
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import io
    import time
```

1. `import streamlit as st`: Mengimpor modul Streamlit dan memberikan alias `st` untuk mempermudah penggunaan. Streamlit digunakan untuk membuat aplikasi web dengan antarmuka pengguna (UI) sederhana.

2. `import requests`: Mengimpor modul `requests`, yang digunakan untuk melakukan permintaan HTTP, seperti mengunduh file dari internet.

3. `import os`: Mengimpor modul `os` yang menyediakan fungsi-fungsi untuk berinteraksi dengan sistem operasi, seperti membuat direktori dan mengelola file.

4. `from urllib.parse import urlparse`: Mengimpor fungsi `urlparse` dari modul `urllib.parse`. Fungsi ini berguna untuk memecah URL menjadi komponen-komponennya, seperti skema, netloc, path, dll.

5. `from concurrent.futures import ThreadPoolExecutor, as_completed`: Mengimpor kelas `ThreadPoolExecutor` dan fungsi `as_completed` dari modul `concurrent.futures`. Ini digunakan untuk melakukan eksekusi fungsi dalam beberapa thread secara paralel.

6. `import io`: Mengimpor modul `io`, yang menyediakan alat-alat untuk bekerja dengan input/output stream, seperti `io.BytesIO` yang digunakan di dalam program ini.

7. `import time`: Mengimpor modul `time` yang menyediakan fungsi-fungsi terkait waktu, seperti mengukur durasi eksekusi.

Dengan mengimpor modul-modul ini, program dapat menggunakan fungsi dan kelas yang didefinisikan di dalamnya untuk membuat aplikasi unduhan dengan antarmuka pengguna menggunakan Streamlit, melakukan permintaan HTTP, berinteraksi dengan sistem operasi, dan menjalankan tugas-tugas secara paralel dengan bantuan thread.

Fungsi `download_chunk` ini bertanggung jawab untuk mengunduh bagian tertentu dari suatu file secara paralel dalam bentuk chunk. Mari kita bahas setiap baris kode dalam fungsi ini:


```python
def download_chunk(url, start_byte, end_byte, buffer, total_size, progress_list):
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    response = requests.get(url, headers=headers, stream=True)
```

1. **`headers = {'Range': f'bytes={start_byte}-{end_byte}'}:`**: Membuat header HTTP dengan menggunakan teknik "Range Requests". Header ini memberitahu server untuk hanya mengirimkan bagian tertentu dari file yang diminta, yaitu dari `start_byte` hingga `end_byte`.

2. **`response = requests.get(url, headers=headers, stream=True)`:** Melakukan permintaan HTTP GET ke URL dengan header yang telah dibuat sebelumnya. `stream=True` digunakan untuk memastikan bahwa respons diterima dalam bentuk streaming, yang berguna untuk menghemat penggunaan memori.

```python
    chunk_size = end_byte - start_byte + 1
    buffer.write(response.content)
```

3. **`chunk_size = end_byte - start_byte + 1`:** Menghitung ukuran chunk (bagian) yang diunduh. Ini digunakan untuk mengupdate kemajuan unduhan.

4. **`buffer.write(response.content)`:** Menuliskan konten dari respons HTTP ke dalam buffer. Buffer di sini adalah objek `io.BytesIO`, yang digunakan untuk menyimpan sementara data yang diunduh.

```python
    progress = (start_byte + chunk_size) / total_size
    progress_list.append(progress)
```

5. **`progress = (start_byte + chunk_size) / total_size`:** Menghitung persentase kemajuan unduhan dan menyimpannya dalam variabel `progress`.

6. **`progress_list.append(progress)`:** Menambahkan nilai kemajuan (progress) ke dalam daftar `progress_list`. Ini akan digunakan nanti untuk memantau kemajuan total unduhan.

Dengan demikian, fungsi ini dapat dijalankan secara paralel oleh beberapa thread untuk mengunduh bagian-bagian tertentu dari file, dan melacak kemajuan unduhan masing-masing bagian melalui daftar kemajuan (progress_list).

Fungsi `download_with_progress` ini adalah fungsi tingkat lebih tinggi yang mengatur proses unduhan dengan memanfaatkan `download_chunk` untuk mendownload bagian-bagian tertentu dari file secara paralel. Mari kita bahas setiap bagian dari fungsi ini:

```python
def download_with_progress(url, num_threads=4):
    response = requests.head(url)
    total_size = int(response.headers.get('content-length', 0))
```

1. **`response = requests.head(url)`:** Melakukan permintaan HTTP HEAD ke URL untuk mendapatkan informasi tentang file, terutama panjang total konten (content-length) tanpa mengunduh seluruh kontennya. Informasi ini akan digunakan untuk menghitung ukuran chunk dan membagi tugas unduhan.

2. **`total_size = int(response.headers.get('content-length', 0))`:** Mengambil panjang total konten dari header respons dan mengonversinya menjadi bilangan bulat. Jika header tidak memiliki informasi tentang panjang konten, maka dianggap 0.

```python
    chunk_size = total_size // num_threads
    ranges = [(i * chunk_size, (i + 1) * chunk_size - 1) for i in range(num_threads - 1)]
    ranges.append(((num_threads - 1) * chunk_size, total_size - 1))
```

3. **`chunk_size = total_size // num_threads`:** Menghitung ukuran chunk (bagian) yang akan diunduh oleh setiap thread.

4. **`ranges = [(i * chunk_size, (i + 1) * chunk_size - 1) for i in range(num_threads - 1)]`:** Membuat daftar rentang (range) yang akan diunduh oleh setiap thread. Ini membagi rentang total menjadi bagian-bagian yang akan diunduh oleh masing-masing thread.

5. **`ranges.append(((num_threads - 1) * chunk_size, total_size - 1))`:** Menambahkan rentang terakhir untuk memastikan bahwa tidak ada bagian yang terlewat.

```python
    content_buffers = [io.BytesIO() for _ in range(num_threads)]
    progress_list = []
```

6. **`content_buffers = [io.BytesIO() for _ in range(num_threads)]`:** Membuat daftar objek `io.BytesIO` sebagai buffer untuk setiap thread. Setiap buffer akan digunakan untuk menyimpan sementara konten yang diunduh.

7. **`progress_list = []`:** Membuat daftar kosong untuk menyimpan kemajuan (progress) unduhan.

```python
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []

        for i in range(num_threads):
            future = executor.submit(download_chunk, url, ranges[i][0], ranges[i][1], content_buffers[i], total_size, progress_list)
            futures.append(future)

        for future in as_completed(futures):
            future.result()
```

8. **`with ThreadPoolExecutor(max_workers=num_threads) as executor:`:** Membuka blok konteks menggunakan `ThreadPoolExecutor` dengan jumlah thread sesuai dengan parameter `num_threads`. Ini memungkinkan eksekusi fungsi dalam beberapa thread secara paralel.

9. **`for i in range(num_threads):`:** Membuat dan menyerahkan tugas unduhan ke masing-masing thread menggunakan metode `executor.submit`. Setiap thread akan menjalankan fungsi `download_chunk` untuk mengunduh bagian tertentu.

10. **`for future in as_completed(futures):`:** Menunggu hingga semua thread selesai dijalankan menggunakan `as_completed`. Ini memastikan bahwa proses unduhan tidak dilanjutkan hingga semua thread selesai.

```python
    final_content = b"".join(buffer.getvalue() for buffer in content_buffers)
    return final_content, response.headers.get('Content-Type'), progress_list
```

11. **`final_content = b"".join(buffer.getvalue() for buffer in content_buffers)`:** Menggabungkan semua bagian yang telah diunduh dari setiap thread menjadi satu konten utuh menggunakan `b"".join()`.

12. **`return final_content, response.headers.get('Content-Type'), progress_list`:** Mengembalikan hasil unduhan, tipe konten, dan daftar kemajuan (progress) kepada pemanggil fungsi.

Dengan demikian, fungsi ini memanfaatkan beberapa thread untuk mengunduh bagian-bagian tertentu dari file secara paralel, mengelola buffer untuk menyimpan sementara konten yang diunduh, dan melacak kemajuan unduhan masing-masing bagian.

Fungsi `save_file` ini bertanggung jawab untuk menyimpan konten yang telah diunduh ke dalam file di sistem penyimpanan lokal. Berikut adalah penjelasan rinci dari setiap baris kode:

```python
def save_file(url, content, content_type, target_directory):
    if content_type:
        extension = content_type.split('/')[-1]
    else:
        extension = 'unknown'
```

1. **`if content_type:`:** Memeriksa apakah `content_type` ada. Jika iya, itu berarti server memberikan informasi tentang tipe konten file yang diunduh. Jika tidak, maka dianggap sebagai tipe konten yang tidak diketahui (`'unknown'`).

2. **`extension = content_type.split('/')[-1]`:** Jika `content_type` ada, ekstrak ekstensi file dari tipe konten tersebut. Misalnya, jika tipe konten adalah `"image/jpeg"`, maka `extension` akan menjadi `"jpeg"`.

```python
    os.makedirs(target_directory, exist_ok=True)

    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
```

3. **`os.makedirs(target_directory, exist_ok=True)`:** Membuat direktori target (tempat penyimpanan file) jika belum ada. Jika sudah ada, parameter `exist_ok=True` memastikan bahwa tidak akan ada kesalahan jika direktori sudah ada sebelumnya.

4. **`parsed_url = urlparse(url)`:** Mem-parsing URL untuk mendapatkan informasi seperti skema, netloc, dan path.

5. **`filename = os.path.basename(parsed_url.path)`:** Mengambil nama file dari path yang didapat dari URL.

```python
    filename = filename.replace('%20', ' ')

    if '.' in filename:
        parts = filename.split('.')
        filename = '.'.join(parts[:-1])
```

6. **`filename = filename.replace('%20', ' ')`:** Mengganti karakter `%20` (yang biasanya merupakan representasi dari spasi dalam URL) dengan spasi dalam nama file.

7. **`if '.' in filename:`:** Memeriksa apakah nama file mengandung ekstensi.

8. **`parts = filename.split('.')`:** Memisahkan nama file menjadi bagian-bagian berdasarkan tanda titik (dot).

9. **`filename = '.'.join(parts[:-1])`:** Mengambil semua bagian kecuali yang terakhir, sehingga mendapatkan nama file tanpa ekstensi.

```python
    with open(os.path.join(target_directory, f"{filename}.{extension}"), "wb") as f:
        f.write(content)
```

10. **`with open(os.path.join(target_directory, f"{filename}.{extension}"), "wb") as f:`:** Membuka file untuk ditulis dalam mode biner (`"wb"`).

11. **`f.write(content)`:** Menulis konten (data yang diunduh) ke dalam file yang baru dibuat.

Dengan demikian, fungsi ini membuat direktori target (jika belum ada), mengambil informasi dari URL untuk menentukan nama file, mengelola ekstensi file, dan menyimpan konten ke dalam file di direktori target.

Fungsi `show_sidebar` ini digunakan untuk menampilkan informasi tentang proyek pada bagian samping (sidebar) saat menggunakan Streamlit. Berikut adalah penjelasan baris per baris:

```python
def show_sidebar():
    st.sidebar.title("📚 About this project 📚")
```

1. **`st.sidebar.title("📚 About this project 📚")`:** Menampilkan judul di bagian samping (sidebar) dengan emoji dan teks "About this project".

```python
    st.sidebar.write("Project ini ditujukan untuk memenuhi tugas besar mata kuliah Sistem Paralel Dan Terdistribusi.")
    st.sidebar.write("Pada project ini Anda dapat melakukan unduh file dengan menggunakan beberapa thread sekaligus.")
```

2. **`st.sidebar.write("Project ini ditujukan untuk memenuhi tugas besar mata kuliah Sistem Paralel Dan Terdistribusi.")`:** Menampilkan teks informasi bahwa proyek ini dibuat untuk memenuhi tugas besar pada mata kuliah Sistem Paralel Dan Terdistribusi.

3. **`st.sidebar.write("Pada project ini Anda dapat melakukan unduh file dengan menggunakan beberapa thread sekaligus.")`:** Menyampaikan informasi kepada pengguna bahwa proyek ini memungkinkan mereka untuk mengunduh file dengan menggunakan beberapa thread secara paralel.

```python
    st.sidebar.subheader("User Manual 📖")
    st.sidebar.write("1. Masukkan URL yang ingin diunduh pada kolom URL")
    st.sidebar.write("2. Masukkan jumlah thread yang ingin digunakan pada kolom Thread")
    st.sidebar.write("3. Klik tombol Mulai Unduh untuk memulai proses unduh")
```

4. **`st.sidebar.subheader("User Manual 📖")`:** Menampilkan subjudul "User Manual" dengan emoji buku.

5. **`st.sidebar.write("1. Masukkan URL yang ingin diunduh pada kolom URL")`:** Menyampaikan langkah pertama dalam penggunaan proyek, yaitu memasukkan URL yang ingin diunduh.

6. **`st.sidebar.write("2. Masukkan jumlah thread yang ingin digunakan pada kolom Thread")`:** Menyampaikan langkah kedua, yaitu memasukkan jumlah thread yang ingin digunakan.

7. **`st.sidebar.write("3. Klik tombol Mulai Unduh untuk memulai proses unduh")`:** Menyampaikan langkah ketiga, yaitu mengklik tombol "Mulai Unduh" untuk memulai proses pengunduhan.

```python
    st.sidebar.subheader("Author 📝")
    st.sidebar.markdown("**Karina Khairunnisa Putri (1301213106)**")
    st.sidebar.write("Diandra Lintang Hanintya (1301213072)")
    st.sidebar.write("Naufal Hilmi Majid (1301213430)")
    st.sidebar.write("Muhammad Fatih Yumna Lajuwirdi Lirrahman (1301213389)")
    st.sidebar.write("Benito Raymond (1301213345)")
```

8. **`st.sidebar.subheader("Author 📝")`:** Menampilkan subjudul "Author" dengan emoji pena.

9. **`st.sidebar.markdown("**Karina Khairunnisa Putri (1301213106)**")`:** Menampilkan nama dan NIM masing-masing anggota tim sebagai penulis proyek menggunakan format Markdown untuk mempercantik tampilan.

```python
    st.sidebar.subheader("Find us at 🔎")
    st.sidebar.button("Github", key="github")
```

10. **`st.sidebar.subheader("Find us at 🔎")`:** Menampilkan subjudul "Find us at" dengan emoji kaca pembesar.

11. **`st.sidebar.button("Github", key="github")`:** Menampilkan tombol yang mengarahkan pengguna ke halaman Github proyek. Parameter `key="github"` dapat digunakan sebagai referensi khusus jika dibutuhkan.

Dengan demikian, fungsi `show_sidebar` ini dirancang untuk memberikan informasi tentang proyek, petunjuk penggunaan, dan mengarahkan pengguna ke sumber daya tambahan, seperti profil Github.

Fungsi `main` merupakan inti dari program dan berfungsi untuk menampilkan antarmuka pengguna menggunakan Streamlit, mengumpulkan input dari pengguna, dan mengelola proses pengunduhan file. Mari kita jelaskan setiap bagian dari fungsi ini:

```python
def main():
    st.title("✨ MultiFetch Download Manager ✨")
```

1. **`st.title("✨ MultiFetch Download Manager ✨")`:** Menampilkan judul pada antarmuka pengguna dengan menggunakan emoji untuk memberikan elemen dekoratif dan menarik perhatian pengguna.

```python
    show_sidebar()
```

2. **`show_sidebar()`:** Memanggil fungsi `show_sidebar()` yang telah dijelaskan sebelumnya untuk menampilkan informasi proyek dan panduan pengguna di bagian samping (sidebar).

```python
    num_urls = st.number_input("🔗 Masukkan jumlah URL yang ingin diunduh 🔗", min_value=1, step=1, value=1)
    num_threads = st.number_input("🧬 Masukkan jumlah threads yang ingin digunakan 🧬", min_value=1, step=1, value=4)
```

3. **`num_urls = st.number_input("🔗 Masukkan jumlah URL yang ingin diunduh 🔗", min_value=1, step=1, value=1)`:** Menampilkan input jumlah URL yang ingin diunduh dalam bentuk bilangan yang dapat dimasukkan oleh pengguna. `min_value=1` memastikan bahwa pengguna harus memasukkan setidaknya satu URL.

4. **`num_threads = st.number_input("🧬 Masukkan jumlah threads yang ingin digunakan 🧬", min_value=1, step=1, value=4)`:** Menampilkan input jumlah thread yang ingin digunakan dalam proses pengunduhan. Nilai default diatur sebagai 4.

```python
    target_directory = st.text_input("📂 Pilih direktori penyimpanan file (e.g., result_files):", "result_files")
```

5. **`target_directory = st.text_input("📂 Pilih direktori penyimpanan file (e.g., result_files):", "result_files")`:** Menampilkan input teks untuk memasukkan direktori tempat file akan disimpan. Nilai default diatur sebagai "result_files".

```python
    urls = []
    for i in range(num_urls):
        url = st.text_input(f"Masukkan URL ke-{i + 1}:")
        urls.append(url)
```

6. **Loop untuk Mengumpulkan URL:**
   - Membuat sebuah list kosong (`urls`) untuk menyimpan URL yang dimasukkan oleh pengguna.
   - Menggunakan loop `for` untuk mengiterasi sebanyak `num_urls`.
   - Menampilkan input teks untuk memasukkan URL ke-n menggunakan `st.text_input`.
   - Menambahkan URL ke list `urls`.

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

        target_directory = "result_files"

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

7. **Memulai Proses Unduhan:**
   - **`if st.button("Mulai Unduh 🚀"):`:** Menjalankan blok kode ini jika tombol "Mulai Unduh" diklik.
   - **`st.write("Proses unduh dimulai...")`:** Menampilkan pesan bahwa proses unduhan dimulai.

   - **`for url in urls:`:** Loop melalui setiap URL yang dimasukkan oleh pengguna.
      - **`content, content_type, progress_list = download_with_progress(url, num_threads)`:** Memanggil fungsi `download_with_progress` untuk mengunduh file dari URL yang diberikan dengan memanfaatkan beberapa thread.

      - **`all_content.append(content)`, `all_content_types.append(content_type)`, `all_progress_lists.append(progress_list)`:** Menyimpan hasil unduhan, tipe konten, dan daftar kemajuan (progress) ke dalam list yang sesuai.

   - **`target_directory = "result_files"`:** Menetapkan ulang direktori target. Ini bisa diubah menjadi nilai lain jika diperlukan.

   - **Loop untuk Menyimpan File dan Menampilkan Kemajuan:**
      - **`for i, url in enumerate(urls):`:** Loop melalui setiap URL dan indeksnya menggunakan fungsi `enumerate`.
         - **`content = all_content[i]`, `content_type = all_content_types[i]`, `progress_list = all_progress_lists[i]`:** Mengambil hasil unduhan, tipe konten, dan daftar kemajuan (progress) yang sesuai dengan URL saat ini.

         - **`save_file(url, content, content_type, target_directory)`:** Memanggil fungsi `save_file` untuk menyimpan file dengan menggunakan hasil unduhan, tipe konten, dan direktori target.

         - **`for progress in progress_list:`:** Loop melalui daftar kemajuan (progress) untuk menampilkan kemajuan pengunduhan menggunakan `st.progress(progress)`.

   - **Menghitung dan Menampilkan Waktu yang Diperlukan:**
      - **`end_time = time.time()`, `elapsed_time = end_time - start_time`:** Menghitung waktu yang diperlukan untuk menyelesaikan seluruh proses unduhan.
      - **`st.success(f"Proses unduh selesai! 🎉 Waktu yang diperlukan: {elapsed_time:.2f} detik ⌛️")`:** Menampilkan pesan sukses yang mencakup waktu yang diperlukan.
      - **`st.write(f"File-file disimpan di: {os.path.abspath(target_directory)}")`:** Menampilkan lokasi absolut dari direktori tempat file-file disimpan.

Dengan demikian, fungsi `main` ini bertanggung jawab untuk menampilkan antarmuka pengguna, mengumpulkan input pengguna, menjalankan proses unduhan dengan menggunakan beberapa thread, menyimpan file

Bagian `if __name__ == "__main__":` digunakan untuk mengeksekusi fungsi `main()` ketika skrip ini dijalankan sebagai program utama. Ini adalah pola umum dalam Python yang memeriksa apakah skrip dijalankan langsung atau diimpor sebagai modul ke dalam skrip lain. Jika skrip dijalankan langsung, maka blok kode di dalam `if __name__ == "__main__":` akan dieksekusi.

Dalam konteks ini:

```python
if __name__ == "__main__":
    main()
```

Artinya:

- `__name__` adalah sebuah variabel spesial di Python yang berisi nama dari modul atau skrip yang sedang dieksekusi.
- `__main__` adalah string yang diberikan ke variabel `__name__` ketika skrip dijalankan langsung.
- Dengan menggunakan `if __name__ == "__main__":`, kita memastikan bahwa `main()` hanya dijalankan jika skrip ini dieksekusi langsung, bukan diimpor sebagai modul ke dalam skrip lain.

Jadi, ketika Anda menjalankan skrip ini, fungsi `main()` akan dijalankan dan antarmuka pengguna yang diimplementasikan dalam fungsi tersebut akan muncul.