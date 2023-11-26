import streamlit as st
import requests
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import io
import time
import pandas as pd

def download_chunk(url, start_byte, end_byte, buffer, total_size, progress_queue):
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    response = requests.get(url, headers=headers, stream=True)

    chunk_size = end_byte - start_byte + 1
    buffer.write(response.content)

    # Calculate progress
    progress = (start_byte + chunk_size) / total_size

    # Enqueue progress value to the queue
    progress_queue.put(progress)

def download_with_progress(url, num_threads=4):
    response = requests.head(url)
    total_size = int(response.headers.get('content-length', 0))

    chunk_size = total_size // num_threads
    ranges = [(i * chunk_size, (i + 1) * chunk_size - 1) for i in range(num_threads - 1)]
    ranges.append(((num_threads - 1) * chunk_size, total_size - 1))

    content_buffers = [io.BytesIO() for _ in range(num_threads)]

    progress_queue = Queue()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []

        for i in range(num_threads):
            future = executor.submit(download_chunk, url, ranges[i][0], ranges[i][1], content_buffers[i], total_size, progress_queue)
            futures.append(future)

        for future in as_completed(futures):
            # Use result() to propagate exceptions if any
            future.result()

        final_content = b"".join(buffer.getvalue() for buffer in content_buffers)

    return final_content, response.headers.get('Content-Type'), progress_queue

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

    num_urls = st.number_input("🔽 Masukkan jumlah URL yang ingin diunduh 🔽", min_value=1, step=1, value=1)
    num_threads = st.number_input("🧬 Masukkan jumlah threads yang ingin digunakan 🧬", min_value=1, step=1, value=4)

    target_directory = st.text_input("📂 Pilih direktori penyimpanan file (e.g., result_files):", "result_files")

    urls = []
    for i in range(num_urls):
        url = st.text_input(f"Masukkan URL ke-{i + 1}:")
        urls.append(url)

    if st.button("Mulai Unduh 🚀"):
        st.write("Proses unduh dimulai...")

        start_time = time.time()

        for url in urls:
            content, content_type, progress_queue = download_with_progress(url, num_threads)
            save_file(url, content, content_type, target_directory)

            # Retrieve progress values from the queue and update the progress bar
            while not progress_queue.empty():
                progress = progress_queue.get()
                st.progress(progress)

        end_time = time.time()
        elapsed_time = end_time - start_time
        st.success(f"Proses unduh selesai! 🎉 Waktu yang diperlukan: {elapsed_time:.2f} detik ⌛️")
        

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

if __name__ == "__main__":
    main()