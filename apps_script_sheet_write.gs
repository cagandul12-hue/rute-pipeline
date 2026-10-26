// Tempel di Google Sheet: Ekstensi -> Apps Script. Lihat SETUP_SHEET_WRITE.md.
// ===== Pengaturan =====
const SHEET_NAME = 'Sheet1';          // GANTI: nama tab yang dipakai
const ID_COLUMN  = 'merchant_id';     // nama kolom ID unik (jangan diubah isinya)
// Hanya kolom ini yang boleh ditulis oleh website.
const ALLOWED = ['merchant_name', 'latitude', 'longitude', 'status', 'alamat', 'prioritas', 'jam_buka', 'jam_tutup', 'petugas'];

function doPost(e) {
  let body;
  try { body = JSON.parse(e.postData.contents); }
  catch (err) { return out({ ok: false, error: 'JSON tidak valid' }); }

  const secret = PropertiesService.getScriptProperties().getProperty('SECRET');
  if (!secret || body.secret !== secret) return out({ ok: false, error: 'Tidak diizinkan' });

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const sh = SpreadsheetApp.getActive().getSheetByName(SHEET_NAME);
    if (!sh) return out({ ok: false, error: 'Tab tidak ditemukan' });

    const header = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].map(String);
    const idIdx = header.indexOf(ID_COLUMN);
    if (idIdx < 0) return out({ ok: false, error: 'Kolom ID tidak ditemukan' });

    const lastRow = sh.getLastRow();
    const ids = lastRow > 1 ? sh.getRange(2, idIdx + 1, lastRow - 1, 1).getValues().map(r => String(r[0])) : [];
    const rowOf = {};
    ids.forEach((id, i) => { rowOf[id] = i + 2; });

    let updated = 0; const missing = [];
    (body.updates || []).forEach(u => {
      const row = rowOf[String(u.id)];
      if (!row) { missing.push(u.id); return; }
      Object.keys(u.values || {}).forEach(col => {
        if (!ALLOWED.includes(col)) return;
        let c = header.indexOf(col);
        if (c < 0) {
          sh.getRange(1, header.length + 1).setValue(col);
          header.push(col);
          c = header.length - 1;
        }
        sh.getRange(row, c + 1).setValue(u.values[col]);
      });
      updated++;
    });
    return out({ ok: true, updated: updated, missing: missing });
  } finally {
    lock.releaseLock();
  }
}

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
