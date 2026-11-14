# data_notes.md — Tanım kararları ve NaN gerekçeleri (lider sahipliği)

AGENTS.md §5 gereği: bir özelliğin tanımı bedenler arasında farklıysa, ya da
NaN bırakılıyorsa gerekçesi buraya yazılır. Sözleşmeyi değiştiren hiçbir şey
buraya lider onayı olmadan girmez.

## 1. Tanım kararları (bedenler arası tutarlılık)

| Konu | Karar | Durum |
|---|---|---|
| Eğim hesabı | Yerel metrik CRS (UTM zon; lat>=84 → EPSG:3413, lat<=-80 → EPSG:3031), 30 m native grid, `np.gradient` → atan. Derece tabanlı eğim yasak. | Aktif (p3 uyguluyor) |
| slope_mean/p90 belirsizliği | Radius içi piksellerin 200 çekiliş bootstrap'ı; mean/p90 bootstrap std'si = 1-sigma. | Aktif (p3 uyguluyor) |
| roughness detrend yöntemi | Radius içi elevasyona planar fit (en küçük kareler) uygulanıp artıkların std'si (ddof=1). | Aktif — p3 uygulaması (lstsq planar fit) onaylandı 2026-11-14 |
| temp_amplitude mevsimsellik | Yıllık çevrim ortalaması tercih edilir (mevsimsel pencere Earth'ü yaz tarafına önyargılı yapar); mevsimsel pencere kaçınılmazsa `_src` etiketlenir (ör. `MOD11A2.061_summer_2025`). | Karar: yıllık — p3'e iletildi, uygulama bekleniyor |
| z-mesafe saturation (similarity) | Referans, aday havuzunun ±3σ'sunun dışına düştüğünde skor `e^-3`'e yakın çakılıyor (dry run: thermal ~1e-10). Öneri: özellik z-diff'lerini ±3σ'da kırpmak. | Karar: ERTLENDİ — gerçek Moon referans verisi (p2) gelince etki gerçek veriyle ölçülecek; o zamana kadar skorlar mock referansla yorumlanmaz |
| temp_amplitude | Gündüz-gece LST farkı (MOD11A2.061, DN x 0.02 K); yıllık çevre ortalaması kullanılırsa `_src`'e `..._annual_mean` eklenir. | Aktif |
| albedo | MCD43A3.061 shortwave (BSA/WSA seçimi için not: BSA, sabit güneş açısı analoguna daha yakın — lider kararı TODO(verify)). | TODO(verify) |
| thermal_inertia (Earth) | Doğrudan küresel ürün yok; ATI (apparent thermal inertia) türetmesi kalibrasyon gerektiriyor. | Onaysız sayı yasak → NaN |

## 2. NaN gerekçeleri (hiçbir 0 yer tutucu kullanılmıyor)

- **Earth `thermal_inertia`**: NaN + boş `_src` (bkz. tablo satırı). Kalibre edilmeden doldurulmaz.
- **Earth `roughness`/`relief`**: p3 pipeline'ında sıradaki özellikler; kolonlar sözleşme gereği NaN ile mevcut.
- **Earth `temp_amplitude`/`albedo`**: MODIS ürünleri bağlanınca dolacak; `_res_m` değerleri gerçek çözünürlükle (1000 / 500) yazılıyor.
- **Mock veri (data/mock/)**: tüm değerler sahte; `X_sd` değerin %5-20'si (uydurma), `X_src="MOCK"`. Uygulamada MOCK bandı zorunlu.

## 3. Bilinen bozulma alanları (breakdown kartı için)

Dünya hiçbir sahada şunları analog etmez (kartta sayılacak): yerçekimi
(1.62 / 3.71 m/s²), vakum (Ay) / 6-7 mbar CO₂ (Mars), radyasyon (atmosfer
yok/atmosfer ince), Ay kutbu termal çevrim hızı. Bunlar sayısal skorun
DIŞINDA, ayrı kart olarak sunulur (AGENTS.md §8 madde 2).
