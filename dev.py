import streamlit as st
import requests
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import io
import time
from multiprocessing import cpu_count

def download_chunk(url, start_byte, end_byte, buffer, total_size, progress_list):
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    response = requests.get(url, headers=headers, stream=True)

    chunk_size = end_byte - start_byte + 1
    buffer.write(response.content)

    progress = (start_byte + chunk_size) / total_size
    progress_list.append(progress)

def download_with_progress(url, num_threads=None, max_threads=8):
    if num_threads is None:
        num_threads = min(cpu_count(), max_threads)  # Use min to limit the threads to max_threads

    if num_threads > max_threads:
        st.warning(f"Number of threads ({num_threads}) exceeds the maximum allowed (8). Using 8 threads instead.")
        num_threads = max_threads

    response = requests.head(url)
    total_size = int(response.headers.get('content-length', 0))

    chunk_size = total_size // num_threads
    ranges = [(i * chunk_size, (i + 1) * chunk_size - 1) for i in range(num_threads - 1)]
    ranges.append(((num_threads - 1) * chunk_size, total_size - 1))

    content_buffers = [io.BytesIO() for _ in range(num_threads)]

    progress_list = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []

        for i in range(num_threads):
            future = executor.submit(download_chunk, url, ranges[i][0], ranges[i][1], content_buffers[i], total_size, progress_list)
            futures.append(future)

        for future in as_completed(futures):
            future.result()

    final_content = b"".join(buffer.getvalue() for buffer in content_buffers)

    return final_content, response.headers.get('Content-Type'), progress_list

def save_file(url, content, content_type, target_directory):
    if content_type:
        extension = content_type.split('/')[-1]
    else:
        extension = 'unknown'

    os.makedirs(target_directory, exist_ok=True)

    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    filename = filename.replace('%20', ' ')

    if '.' in filename:
        parts = filename.split('.')
        filename = '.'.join(parts[:-1])

    with open(os.path.join(target_directory, f"{filename}.{extension}"), "wb") as f:
        f.write(content)

def show_sidebar():
    st.sidebar.title("📚 About this project 📚")
    st.sidebar.write("Project ini ditujukan untuk memenuhi tugas besar mata kuliah Sistem Paralel Dan Terdistribusi.")
    st.sidebar.write("Pada project ini Anda dapat melakukan unduh file dengan menggunakan beberapa thread sekaligus.")
    st.sidebar.subheader("User Manual 📖")
    st.sidebar.write("1. Masukkan URL yang ingin diunduh pada kolom URL")
    st.sidebar.write("2. Masukkan jumlah thread yang ingin digunakan pada kolom Thread")
    st.sidebar.write("3. Klik tombol Mulai Unduh untuk memulai proses unduh")
    st.sidebar.subheader("Author 📝")
    st.sidebar.markdown("**Karina Khairunnisa Putri (1301213106)**")
    st.sidebar.write("Diandra Lintang Hanintya (1301213072)")
    st.sidebar.write("Naufal Hilmi Majid (1301213430)")
    st.sidebar.write("Muhammad Fatih Yumna Lajuwirdi Lirrahman (1301213389)")
    st.sidebar.write("Benito Raymond (1301213345)")
    st.sidebar.subheader("Find us at 🔎")
    st.sidebar.button("Github", key="github")

def main():
    st.title("✨ MultiFetch Download Manager ✨")

    show_sidebar()

    num_urls = st.number_input("🔗 Masukkan jumlah URL yang ingin diunduh 🔗", min_value=1, step=1, value=1)
    num_threads = st.number_input("🧬 Masukkan jumlah threads yang ingin digunakan 🧬", min_value=1, step=1, value=4)

    target_directory = st.text_input("📂 Pilih direktori penyimpanan file (e.g., result_files):", "result_files")

    urls = []
    for i in range(num_urls):
        url = st.text_input(f"Masukkan URL ke-{i + 1}:")
        urls.append(url)

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

if __name__ == "__main__":
    main()
