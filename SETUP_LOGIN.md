# Mengatur login (username & password tidak ada di kode)

Kode tidak lagi berisi username/password bawaan. Login hanya berfungsi bila Anda mengisinya di **Secrets**.
Tanpa itu, halaman login menampilkan "Login belum diatur" dan tidak ada yang bisa masuk.

## Langkah

1. Di komputer Anda, jalankan `python buat_hash_password.py`, ketik password baru (minimal 8 karakter) dua kali.
   Skrip mencetak dua baris: `APP_USERNAME` dan `APP_PASSWORD_HASH`.
2. Buka Streamlit Cloud -> aplikasi -> **Settings -> Secrets**. Tempel dua baris itu **di atas** bagian `[supabase]`
   (baris tanpa judul tabel harus ada sebelum `[supabase]`, kalau tidak TOML menganggapnya bagian `[supabase]`).
3. **Save**, lalu **Reboot app**. Isi Secrets dulu sebelum men-deploy kode baru, supaya tidak terkunci.
4. Coba masuk dengan username dan password baru.

## Penting

- Pakai password **baru**. Password lama (`admin` / `123`) pernah ada di kode dan riwayat Git, jadi anggap sudah diketahui.
- Hash tidak bisa dibalik menjadi password, jadi isi Secrets yang bocor pun tidak langsung membuka password Anda.
  (Alternatif tidak aman tetapi didukung: `APP_PASSWORD = "..."` teks biasa. Hash lebih disarankan.)
- Ganti password: ulangi langkah 1-3. Semua yang sedang login otomatis keluar (token login terikat ke hash).
- Jangan commit `secrets.toml`. File `.gitignore` sudah mengecualikannya.
- Percobaan salah 5 kali berturut-turut mengunci login selama 60 detik.
