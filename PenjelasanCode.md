### 1

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

### 2