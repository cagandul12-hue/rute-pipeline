# Simpan sesi otomatis dengan Supabase

Fitur ini menyimpan pekerjaan Anda (file yang diunggah, data Maps Extractor, edit tabel, dan pengaturan) ke Supabase,
lalu menawarkan untuk memulihkannya saat halaman di-refresh atau dibuka lagi. Tanpa pengaturan di bawah, fitur mati
dan aplikasi berjalan seperti biasa.

## Langkah

1. **Buat proyek Supabase khusus** untuk aplikasi ini (bukan proyek yang dipakai hal lain). Kunci rahasia punya akses
   penuh ke seluruh proyek, jadi sebaiknya proyeknya terpisah.
2. **Buat tabel**: buka *SQL Editor*, tempel isi `supabase_setup.sql`, lalu *Run*.
3. **Ambil kredensial**: *Project Settings -> API Keys*. Salin *Project URL* dan **secret key** (`sb_secret_...`).
   Kunci `service_role` lama (diawali `eyJ...`) juga bisa dipakai.
4. **Isi Secrets** di Streamlit Cloud (*App -> Settings -> Secrets*) dengan isi `.streamlit/secrets.toml.example`
   yang sudah diisi nilai asli. Untuk dijalankan di komputer sendiri, simpan sebagai `.streamlit/secrets.toml`
   (sudah dikecualikan di `.gitignore`).
5. **Reboot** aplikasi, lalu uji: unggah data -> sidebar menampilkan "☁️ Tersimpan otomatis" -> refresh halaman ->
   muncul tawaran "Ada sesi tersimpan" -> klik **Pulihkan sesi**. Di *Table Editor* Supabase akan ada satu baris.

## Jika sesi tidak muncul setelah refresh

1. Buka sidebar -> **🔧 Diagnosa simpan otomatis** -> **Tes koneksi Supabase**. Pesannya menyebut penyebab dan solusinya.
2. **"HTTP 403 ... permission denied (42501)"**: Supabase (sejak 2026) tidak lagi memberi akses otomatis ke tabel baru.
   Jalankan di *SQL Editor*:
   `grant select, insert, update, delete on public.rp_sessions to service_role;`
   (baris ini sudah ada di `supabase_setup.sql` versi terbaru).
3. **"HTTP 401"**: secret key salah. Salin ulang dari *Project Settings -> API Keys*, tanpa spasi tambahan.
4. **"HTTP 404" / tabel tidak ditemukan**: `supabase_setup.sql` belum dijalankan, atau *Project URL* salah.
5. Sidebar menampilkan "☁️ Tersimpan otomatis" dan *Table Editor -> rp_sessions* berisi satu baris, tetapi tawaran tidak muncul:
   cek baris "Cookie ID sesi" di panel diagnosa. Bila belum terbaca, cookie diblokir browser (mode privat / blokir cookie).

## Cara kerja singkat

- Browser diberi cookie acak `rp_sid` (14 hari). ID itu menjadi kunci satu baris di tabel `rp_sessions`.
- Penyimpanan terjadi otomatis saat isi berubah. Isinya di-gzip dulu, jadi kecil.
- Saat halaman dibuka dalam keadaan kosong dan ada sesi tersimpan, Anda ditawari **Pulihkan sesi** atau **Mulai baru**
  (tidak dipulihkan diam-diam, supaya tidak menimpa pekerjaan baru).
- **Keluar** menghapus sesi tersimpan dan cookie-nya. Sesi yang tidak disentuh lebih dari 14 hari dibersihkan otomatis.

## Yang perlu diketahui

- **Hasil rute tidak ikut tersimpan.** Setelah pemulihan, tekan *Buat Rute* lagi. Unduh Excel/PDF kalau hasilnya perlu disimpan.
- **Batas ukuran**: sesi terkompresi di atas 8 MB (atur lewat `max_mb`) tidak disimpan otomatis; sidebar memberi tahu.
  Paket gratis Supabase memberi database 500 MB total.
- **Jika Supabase tidak bisa dihubungi**, aplikasi tetap berjalan. Sidebar menampilkan peringatan dan penyimpanan dicoba lagi
  setelah 60 detik.
- **Proyek gratis dijeda** bila lama tidak aktif; aktifkan lagi dari dashboard Supabase. Data tidak dihapus saat dijeda.
- **Dua tab di browser yang sama** memakai ID yang sama, jadi tab yang terakhir menyimpan akan menimpa yang lain.
- **Privasi**: isi sesi berupa data merchant Anda. Simpan kunci rahasia hanya di Secrets, jangan di kode atau repositori.
