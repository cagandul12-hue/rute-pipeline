-- Penyimpanan sesi otomatis untuk Routing & Extractor.
-- Jalankan di Supabase: SQL Editor -> New query -> tempel -> Run.

create table if not exists public.rp_sessions (
  id          text        primary key,                 -- ID acak dari cookie browser (rp_sid)
  data        text        not null,                    -- isi sesi: JSON -> gzip -> base64
  size_bytes  integer     not null default 0,          -- ukuran terkompresi
  meta        jsonb       not null default '{}'::jsonb, -- ringkasan untuk tawaran pemulihan (jumlah file, edit, dll.)
  updated_at  timestamptz not null default now()
);

create index if not exists rp_sessions_updated_at_idx on public.rp_sessions (updated_at);

-- KEAMANAN: aktifkan RLS dan JANGAN membuat policy apa pun.
-- Kunci publik (anon / publishable) lalu tidak bisa membaca atau menulis tabel ini.
-- Hanya kunci rahasia server (secret key / service_role) yang bisa, karena melewati RLS.
alter table public.rp_sessions enable row level security;
revoke all on public.rp_sessions from anon, authenticated;

-- IZIN UNTUK APLIKASI: sejak 2026 Supabase tidak lagi memberi akses Data API otomatis ke tabel baru
-- (termasuk untuk service_role). Tanpa baris ini, simpan gagal dengan "HTTP 403 ... permission denied (42501)".
-- Aman dijalankan berulang, dan tidak membuka akses untuk kunci publik (anon / authenticated).
grant select, insert, update, delete on public.rp_sessions to service_role;
