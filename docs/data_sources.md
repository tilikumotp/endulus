# Birincil Veri Kaynakları ve Doğrulanmış Literatür Kaynakçası (`docs/data_sources.md`)

Bu belge, `AGENTS.md` (§5 Veri Sözleşmesi, §6 Kural 2–3, §7) uyarınca proje genelinde kullanılan doğrulanmış uydu/yörünge ürünlerinin ve hakemli literatür atıflarının tekil ana dizinidir. Ay (`body == "moon"`) bölümü Emirhan'ın (`p2-moonmars`) [`docs/data_sources_moon.md`](data_sources_moon.md) belgesinden, Dünya (`body == "earth"`) bölümü Eray'ın (`p3-earth`) [`docs/data_sources_earth.md`](data_sources_earth.md), [`docs/validation_expectations.md`](validation_expectations.md) ve [`src/earth/sites.py`](../src/earth/sites.py) dosyalarından, metodoloji ve sözleşme kuralları ise [`docs/data_notes.md`](data_notes.md) belgesinden derlenmiştir.

---

## 1. Uydu ve Yörünge Veri Ürünleri Özeti (`data/processed/`)

### 1.1 Ay Güney Kutbu (`features_moon.parquet` — 5 Referans Saha, `r = 1000 m`)

| Özellik Grubu | Sözleşme Kolonu | Doğrulanmış Ürün Kodu (`*_src`) | Versiyon / Çözünürlük (`*_res_m`) | Kapsam & Notlar | Birincil Kaynak |
|---|---|---|---|---|---|
| Topoğrafya & Eğim | `slope_mean`, `slope_p90`, `roughness`, `relief` (+ `_sd`) | `LRO_LOLA_PGDA_{Site04,Site01,Site11,Site07,LM7}_5mpp_v2021` (`*_surf.tif`, `*_slperr.tif`, `*_toterr.tif`) | `v2021` / **`5.0 m`** | Kutupsal Stereografik (`MOON_ME` DE421, metre); her `r = 1000 m` pencerede `~125,664–125,676` piksel; 200 bootstrap + PGDA klon RMS birleşik `_sd` | NASA GSFC PGDA Product 78 (`Barker et al., 2021`) |
| Yüzey Parlaklığı | `albedo` (+ `_sd`) | `LRO-L-LOLA-4-GDR-V1.0:LDAM_50S_1000M_V1.0_broadband_eq` (`LDAM_50S_1000M_FLOAT.IMG`) | `V1.0` / **`1000.0 m`** | `50°S–90°S`; 1064 nm sıfır-faz (`α = 0°`) normal albedo değerleri Earth `MCD43A3.061` geniş bant güneş albedosuyla hizalamak için `× 0.38` ile ölçeklenmiştir (`TODO(verify)`: `0.38` tekil tablo kaynağı proje kararıdır, bkz. [`docs/data_sources_moon.md`](data_sources_moon.md) §5.1) | MIT LOLA GDR (`Lucey et al., 2014`; `Lemelin et al., 2016`) |
| Termal Eksen | `temp_amplitude`, `thermal_inertia` | `""` *(v1'de bilinçli olarak `NaN` — Lider Kararı #30)* | Referans PDS: `240.0 m` | LRO Diviner `LRO-L-DLRE-5-PCP-V1.0` (`pcp_avg_tbol_pols_sum_ltim01..96_240`, `80°S–90°S`) 29.53 günlük vakumlu sinodik döngü üretir; Dünya MODIS 24 saatlik yıllık ortalama farkıyla eşdeğer olmadığı ve Hayne et al. (2017) küresel `H` haritası `±70°` dışındaki kutbu kapsamadığı için v1 sayısal skorundan çıkarılmıştır | `Williams et al., 2019`; `Paige et al., 2010`; `Hayne et al., 2017` |
| 3B & Görsel Atlas | `moon_3d/`, `moon_atlas/`, `thumbs/moon/` | LRO LOLA PGDA `5 m/px` yerel karolar (`442 × 442 px`, `2.2 × 2.2 km`) | `5.0 m` (thumb `9.82 m`) | Tamamen çevrimdışı yerel 3B DEM ve kutupsal kabartma / eğim haritaları (`Illustrative slope bins; not a landing-safety assessment`) | `docs/data_sources_moon.md` §5.2–5.4 |

### 1.2 Dünya (`features_earth.parquet` — 10 Doğrulama + 30 Aday Saha, `r = 1000 m`)

| Özellik Grubu | Sözleşme Kolonu | Doğrulanmış Ürün Kodu (`*_src`) | Versiyon / Çözünürlük (`*_res_m`) | Kapsam & Notlar | Birincil Kaynak |
|---|---|---|---|---|---|
| Topoğrafya & Eğim (Birincil — 39/40 saha) | `slope_mean`, `slope_p90`, `roughness`, `relief` (+ `_sd`) | `Copernicus_DEM_GLO-30` (DGED COG) | **`30.0 m`** (1 arc-sec) | **EGM2008 (`EPSG:3855`)** ortometrik yükseklik; yerel UTM/UPS metrik projeksiyonda `np.gradient → atan`; `sigma_z_rel = 1.0 m` (Airbus/ESA Product Handbook `GEO.2018-1988-2 §4.2`, `LE90 < 2.0 m`) | AWS Open Data S3 / Planetary Computer `cop-dem-glo-30` |
| Topoğrafya & Eğim (Yedek — 1/40 saha) | `slope_mean`, `slope_p90`, `roughness`, `relief` (+ `_sd`) | `NASADEM_HGT_v001` (`C2763264762-LPCLOUD`) | **`30.0 m`** (1 arc-sec) | Yalnızca Copernicus GLO-30 arşivinde bulunmayan `N39 E044` (`earth_agri_dogubayazit_flow`) için otomatik yedek; yükseklikleri **EGM96** geoid datumundadır (eğim/pürüzlülük/rölyef yerel türev olduğu için ofsetten pratikte etkilenmez) | NASA LP DAAC / `doi:10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001` |
| Yüzey Parlaklığı (Albedo — 40/40 saha) | `albedo` (+ `_sd`) | `MCD43A3.061` (`Albedo_BSA_shortwave`, `C2278860820-LPCLOUD`) | V061 / **`500.0 m`** (gerçek `463.3 m`) | `5 × 5` piksel yaz penceresi (Kuzey: Tem–Ağu 2024; `lat < -45°` McMurdo: Oca–Şub 2024); `MCD43A4.061` + `Liang (2001)` + `NDSI < 0.40` ile çapraz doğrulandı | NASA Earthdata LP DAAC & `Liang (2001)` |
| Sıcaklık Genliği (Earth veri setinde kayıtlı, v1 skorda kullanılmaz) | `temp_amplitude` (+ `_sd`) | `MOD11A2.061_annual_mean` (`C2269056084-LPCLOUD`) | V061 / **`1000.0 m`** (gerçek `926.6 m`) | 2024 yıllık 24-kompozit gündüz–gece farkı (`QC <= 1`, `3 × 3` piksel); **Ay `temp_amplitude = NaN` olduğundan v1 skorlamasına katılmaz** | Planetary Computer `modis-11A2-061` / LP DAAC |
| Termal Eylemsizlik | `thermal_inertia` | `""` (`NaN` — 40/40 saha) | Nominal `1000.0 m` | Her iki gök cisminde standart eşdeğer küresel uydu ürünü yoktur (`AGENTS.md` §5, Karar #30) | `docs/data_sources_earth.md` §1 |
| 3B & Karışık Piksel Denetimi | `earth_3d_grids.npz`, `earth_atlas/` | `Copernicus_DEM_GLO-30` / `NASADEM` (`74 × 74 px`, `2.22 × 2.22 km`), Sentinel-2 L2A & ESA WorldCover `v200` (10 m) | `30 m` (DEM), `10–20 m` (optik/sınıf) | `earth_atlas/*.webp` tamamen çevrimdışı; WorldCover + S2 denetiminde `5` saha `MIXED_*` olarak belgelenmiştir (bkz. `docs/data_sources_earth.md` §7) | Planetary Computer STAC / `src/earth/mixed_pixel.py` |

---

## 2. Emirhan (`p2-moonmars`) — Doğrulanmış Ay Literatürü

Tüm künyeler [`docs/data_sources_moon.md`](data_sources_moon.md) içinden doğrudan kontrol edilerek aktarılmıştır:

1. **Barker, M. K., Mazarico, E., Neumann, G. A., Zuber, M. T., Haruyama, J., & Smith, D. E. (2021).** *Improved LOLA elevation maps for south pole landing sites: Error estimates and their impact on illumination conditions.* *Planetary and Space Science*, 203, 105119. DOI: `10.1016/j.pss.2020.105119` — PGDA Product 78 (`5 m/px` DEM ve eğim/düşey klon hata haritaları; **birebir eğim aralığı karşılaştırması `TODO(verify)`**).
2. **Mazarico, E., Neumann, G. A., Smith, D. E., Zuber, M. T., & Torrence, M. H. (2011).** *Illumination conditions of the lunar polar regions using LOLA topography.* *Icarus*, 211(2), 1066–1081. — Kutup aydınlanma koşulları ve ROI bağlamı.
3. **Zuber, M. T., Head, J. W., Smith, D. E., Neumann, G. A., Mazarico, E., et al. (2012).** *Constraints on the volatile distribution within Shackleton crater at the lunar south pole.* *Nature*, 486, 378–381. DOI: `10.1038/nature11216` — Shackleton LOLA topografyası ve 1064 nm albedosu.
4. **Spudis, P. D., Bussey, B., Plescia, J., Josset, J.-L., & Beauvivre, S. (2008).** *Geology of Shackleton Crater and the south pole of the Moon.* *Geophysical Research Letters*, 35, L14201. DOI: `10.1029/2008GL034468` — Güney kutbu jeolojisi (**saha-bazlı anortozit/breş atfı `TODO(verify)`**).
5. **Lucey, P. G., Neumann, G. A., Riner, M. A., Mazarico, E., Smith, D. E., et al. (2014).** *The global albedo of the Moon at 1064 nm from LOLA.* *Journal of Geophysical Research: Planets*, 119(7), 1665–1679. DOI: `10.1002/2013JE004592` — 1064 nm sıfır-faz normal albedo haritası (**`0.38` dönüşüm çarpanının tekil tablo kaynağı `TODO(verify)`**).
6. **Lemelin, M., Lucey, P. G., Neumann, G. A., Mazarico, E., Barker, M. K., et al. (2016).** *Improved calibration of reflectance data from the LRO Lunar Orbiter Laser Altimeter (LOLA) and implications for space weathering.* *Icarus*, 273, 315–328. DOI: `10.1016/j.icarus.2016.02.006` — İyileştirilmiş LOLA kalibrasyonu (`afdbd06`).
7. **Vasavada, A. R., Bandfield, J. L., Greenhagen, B. T., Hayne, P. O., Siegler, M. A., Williams, J.-P., & Paige, D. A. (2012).** *Lunar equatorial surface temperatures and regolith properties from the Diviner Lunar Radiometer Experiment.* *Journal of Geophysical Research*, 117, E00H18. DOI: `10.1029/2011JE003987` — Albedo–termal bağlam (yalnızca nitel bağlam).
8. **Paige, D. A., Siegler, M. A., Zhang, J. A., Hayne, P. O., Foote, E. J., et al. (2010).** *Diviner Lunar Radiometer observations of cold traps in the Moon's south polar region.* *Science*, 330(6003), 479–482. — Kalıcı gölgeli bölgelerde `~38 K` düzeyinde düşük kutup sıcaklıkları (v1'de askıda).
9. **Williams, J.-P., Greenhagen, B. T., Paige, D. A., Schorghofer, N., Sefton-Nash, E., et al. (2019).** *Seasonal polar temperatures on the Moon.* *Journal of Geophysical Research: Planets*, 124(10), 2505–2521. DOI: `10.1029/2019JE006028` — `80°` enlem üzeri mevsimsel kutup sıcaklıkları.
10. **Hayne, P. O., Bandfield, J. L., Siegler, M. A., Vasavada, A. R., Ghent, R. R., et al. (2017).** *Global regolith thermophysical properties of the Moon from the Diviner Lunar Radiometer Experiment.* *Journal of Geophysical Research: Planets*, 122(12), 2371–2400. DOI: `10.1002/2017JE005387` — Regolit termofiziksel özellikleri (v1'de Kapı 1 ile askıda; PDS `±70°` kapsam sınırı notu `TODO(verify)`).

---

## 3. Eray (`p3-earth`) — Doğrulanmış Dünya Literatürü

### 3.1 Ön-Kayıtlı Kör Doğrulama (E1) ve Buz/Permafrost (E8) DOI Kaynakları (`10 Doğrulama Sahası`)

Ayrıntılı beklenti gerekçeleri ve DOI bağlantıları [`docs/validation_expectations.md`](validation_expectations.md) içindedir:

- **`earth_etna_cisternazza` (İtalya):** *Mobilite (Kesin)* — Schuster et al. (2020, *IEEE RA-L*, 5(4):5315–5322, DOI `10.1109/LRA.2020.3007468`); Vayugundla et al. (2018, *ISR 2018*, `https://elib.dlr.de/124514/`). *Buz/Permafrost (`kısmi`)* — Oliva et al. (2018, *Earth-Sci. Rev.*, 185:397–436, DOI `10.1016/j.earscirev.2018.06.018`, kuzey yamaç Grotta del Gelo) + kış kar gözlemi.
- **`earth_atacama_yungay` (Şili):** *Mobilite (Kesin)* — Wettergreen et al. (2005, *IEEE ICRA*, DOI `10.1109/ROBOT.2005.1570227`, *Zoë* rover). *Termal/Hiperkurak (Kesin)* — McKay et al. (2003, *Astrobiology*, 3(2):393–406, DOI `10.1089/153110703769016460`); Navarro-González et al. (2003, *Science*, 302:1018–1021, DOI `10.1126/science.1089143`). *Buz (`yok`)* — McKay et al. (2003).
- **`earth_haughton_crater` (Kanada):** *Mobilite & Termal/Permafrost (Kesin)* — Lee & Osinski (2005, *MAPS*, 40(12):1755–1758, DOI `10.1111/j.1945-5100.2005.tb00144.x`); Osinski, Spray & Lee (2005, *MAPS*, 40(12):1789–1812, DOI `10.1111/j.1945-5100.2005.tb00147.x`); Thomson, Osinski & Pollard (2012, *JGR Planets*, 117:E09003, DOI `10.1029/2012JE004053`). *Buz (`var`)*.
- **`earth_mauna_loa_hiseas` (Hawaii, ABD):** *Mobilite (Kesin)* — Shiro et al. (2022, *Planet. Space Sci.*, 212:105409, DOI `10.1016/j.pss.2021.105409`); ayrıca `sites.py` bağlamında Binsted et al. (2016) & Bleacher et al. (2017, *JVGR* 342:1–10). *Buz (`veri yok`, saha-dışı yüksek rakım Icecave için `Pflitsch et al., 2016` notu)*.
- **`earth_mcmurdo_wright_valley` (Antarktika):** *Termal/Soğuk Çöl & Permafrost (Kesin)* — Marchant & Head (2007, *Icarus*, 192(1):187–222, DOI `10.1016/j.icarus.2007.06.018`); Levy, Marchant & Head (2010, *Icarus*, 206(1):229–252, DOI `10.1016/j.icarus.2009.09.005`); Levy, Head & Marchant (2008, *Antarctic Science*, DOI `10.1017/S0954102008001375`). *Buz (`var`)*.
- **`earth_lanzarote_timanfaya` (İspanya):** *Mobilite (Kesin)* — Sauro et al. (2023, *Acta Astronautica*, 204:222–238, DOI `10.1016/j.actaastro.2022.12.034`); Sauro et al. (2020, *Earth-Sci. Rev.*, 209:103288, DOI `10.1016/j.earscirev.2020.103288`); ayrıca Bessone et al. (2018). *Buz (`veri yok`)*.
- **`earth_meteor_crater_arizona` (Arizona, ABD):** *Mobilite (Kesin)* — Kring (2007/2017, LPI Contrib. 1355); Poelchau, Kenkmann & Kring (2009, *JGR Planets*, DOI `10.1029/2008JE003235`); Kumar, Head & Kring (2010, *Icarus*, DOI `10.1016/j.icarus.2010.03.032`); Shoemaker (1959, USGS OFR 59-108, DOI `10.3133/ofr59108`). *Buz (`veri yok`)*.
- **`earth_craters_of_the_moon` (Idaho, ABD):** *Mobilite (Kesin)* — Hughes et al. (2019, *Astrobiology*, 19(3):260–283, DOI `10.1089/ast.2018.1847` — künye hatası `docs/validation_expectations.md` içinde düzeltilmiştir); Lim et al. (2019, *Astrobiology*, 19(3):245–259, DOI `10.1089/ast.2018.1869`). *Buz (`veri yok`)*.
- **`earth_svalbard_bockfjorden` (Norveç):** *E1 eksenleri (`kaynak doğrulanamadı`)*; AMASE bağlamı: Steele et al. (2011, *Astrobiology* 11), Amundsen et al. (2012), Treiman (2012, *Polar Research*, DOI `10.3402/polar.v31i0.17320`). *Buz/Permafrost (`var`)* — Humlum, Instanes & Sollid (2003, *Polar Research*, 22(2):191–215, DOI `10.3402/polar.v22i2.6455`).
- **`earth_lunar_crater_nevada` (Nevada, ABD):** *Mobilite (Kesin)* — Evans, Farr & van Zyl (1992, *IEEE TGRS*, 30(2):382–389, DOI `10.1109/36.134087`); Valentine et al. (2017, *Geosphere*, 13(2):391–438, DOI `10.1130/GES01428.1`); Scott & Trask (1971, USGS Prof. Paper 599-I, DOI `10.3133/pp599i`). *(Termal/Yüzey beklentisi GRSFE TIMS & Lunar Lake playa sınırları nedeniyle E1'de Aday düzeyine indirilmiştir).* *Buz (`veri yok`)*.

### 3.2 `src/earth/sites.py` İçindeki 30 Aday Sahanın Koordinat ve Literatür Atıfları

#### 3.2.1 Türkiye Aday Sahaları (`14` Saha — Bilimsel Öncelik / Yenilik Disiplini ile)

> **Önemli Literatür Ayrımı (`docs/data_sources_earth.md` §3):** Salda Gölü (*Horgan et al., 2020*), Acıgöl/Karapınar Meke ve Tuz Gölü (*Keller, 1974; Druitt et al., 1995; Kashima, 2002; Çiner et al., 2021*) uluslararası literatürde halihazırda incelenmiş sahalardır; yeni keşif olarak değil karşılaştırmalı aday olarak sunulurlar. Karacadağ, Kula, Tendürek, Ağrı, Süphan, Erciyes, Hasandağı, Nemrut ve Kapadokya sahaları ise jeoloji/petroloji literatüründe belgelenmiş olup nicel çok-eksenli uzaysal adaylar (`role == "candidate"`) olarak değerlendirilmektedir.

| `#` | `site_id` | Saha Adı (`name`) | Litoloji | Doğrulanmış Kaynak (`src/earth/sites.py` & `docs/data_sources_earth.md` §4) |
|---|---|---|---|---|
| 1 | `earth_karacadag_summit` | Karacadağ Shield Volcano (Kollubaba / Lav Platosu) | `basalt` | Lustrino et al. (2010, *Lithos* 117:135–151), Keskin et al. (2012) & Ekici et al. (2014) |
| 2 | `earth_karacadag_ovabag` | Karacadağ NE Flank (Ovabağ Low-Slope Basalt Flow, Diyarbakır) | `basalt` | Ekici et al. (2014, *Geodinamica Acta* 26:3–4) & Lustrino et al. (2012) |
| 3 | `earth_kula_divlit` | Kula Volcanic Geopark (Divlit Scoria Cone & ʻAʻā Basalt, Manisa) | `basalt` | Ersoy et al. (2010, *JVGR* 190:291–306) & Aldanmaz et al. (2015) |
| 4 | `earth_tendurek_shield` | Tendürek Shield Volcano (Çaldıran Basalt Lava Apron, Ağrı-Van) | `basalt` | Lebedev et al. (2016, *Petrology* 24:127–163) & Yılmaz et al. (1998, *JVGR* 85:173–210) |
| 5 | `earth_erciyes_kojugedigi` | Mount Erciyes (Koçdağ SE Flank Basalt-Andesite Plateau, Kayseri) | `basalt` | Şen et al. (2003, *JVGR* 125:225–246) & Friedrichs et al. (2020) |
| 6 | `earth_hasandagi_kecekalecik` | Mount Hasan / Hasandağı (NW Flank Basalt-Andesite Apron, Aksaray) | `basalt` | Deniel et al. (1998, *JVGR* 87:275–302) & Aydar & Gourgaud (1998) |
| 7 | `earth_acigol_guneydag` | Acıgöl-Nevşehir Caldera (Güneydağ Maar & Tephra Ring, Nevşehir) | `pyroclastic_tuff` | Druitt et al. (1995, *J. Geol. Soc. London* 152:655–667) & Schmitt et al. (2011) |
| 8 | `earth_cappadocia_kavakkoy` | Cappadocia Ignimbrite Plateau (Kavak / Göreme Tuff Tableland, Nevşehir) | `pyroclastic_tuff` | Le Pennec et al. (1994, *JVGR* 63:59–87) & Aydar et al. (2012, *Bull. Volcanol.* 74:739–762) |
| 9 | `earth_tuz_golu_south` | Tuz Gölü Basin (Southern Evaporite Marginal Flat, Aksaray) | `evaporite` | Çiner et al. (2021) & Kashima (2002, *Catena* 48:3–20) |
| 10 | `earth_salda_terrace` | Lake Salda Onshore Terrace (Hydromagnesite/Ultramafic Shore, Burdur) | `evaporite` | Horgan et al. (2020, *Icarus* 339:113526) & Russell et al. (1999, *J. Geol. Soc.* 156:869–888) |
| 11 | `earth_karapinar_meke` | Karapınar Volcanic Field (Meke Maar & Scoria Apron, Konya) | `basalt` | Keller (1974, *Bull. Volcanol.* 38:378–396) & Reid et al. (2017, *JVGR* 338:1–13) |
| 12 | `earth_suphan_south_apron` | Mount Süphan (Lower Adilcevaz Basalt-Andesite Lava Apron, Bitlis) | `basalt` | Özdemir et al. (2011, *Lithos* 127:68–85) & Yılmaz et al. (1998, *JVGR* 85:173–210) |
| 13 | `earth_nemrut_caldera_flank` | Nemrut Volcano (Tatvan Eastern Ignimbrite & Lava Flank, Bitlis) | `pyroclastic_tuff` | Çubukçu et al. (2012, *JVGR* 209–210:33–60) & Ulusoy et al. (2008) |
| 14 | `earth_agri_dogubayazit_flow` | Mount Ararat / Ağrı Dağı (Western Basalt Lava Flank, Doğubayazıt) | `basalt` | Yılmaz et al. (1998, *JVGR* 85:173–210) & Pearce et al. (1990, *JVGR* 44:189–229) |

#### 3.2.2 Küresel Aday Sahalar (`16` Saha)

| `#` | `site_id` | Saha Adı (`name`) | Litoloji | Doğrulanmış Kaynak (`src/earth/sites.py` & `docs/data_sources_earth.md` §4) |
|---|---|---|---|---|
| 1 | `earth_askja_holuhraun` | Askja / Holuhraun Basalt Sand & Lava Plain (Dyngjusandur, Iceland) | `basalt` | Pedersen et al. (2017, *JVGR* 340:155–170) & Greeley et al. (2000) |
| 2 | `earth_harrat_rahat_madinah` | Harrat Rahat Volcanic Field (Northern Basalt Plateau, Saudi Arabia) | `basalt` | Camp & Roobol (1989, *GSA Bulletin* 101:71–95) & Downs et al. (2018) |
| 3 | `earth_pinacate_el_elegante` | Sierra del Pinacate Volcanic Field (El Elegante Maar Rim, Sonora, Mexico) | `basalt` | Gutmann (2002, *GSA Special Paper* 365) & Greeley et al. (1985) |
| 4 | `earth_puna_campo_piedra_pomez` | Puna de Atacama (Campo de Piedra Pómez Ignimbrite & Basalt, Argentina) | `pyroclastic_tuff` | de Silva et al. (2010, *Geology* 38:219–222) & Bridges et al. (2015, *JGR Planets*) |
| 5 | `earth_deccan_mahabaleshwar` | Deccan Traps Flood Basalt Plateau (Panchgani Tableland, India) | `basalt` | Self et al. (2006, *EPSL* 248:518–532) & Jay & Widdowson (2008) |
| 6 | `earth_harrat_ash_shaam` | Harrat Ash Shaam Basalt Desert (Badia Black Basalt Plateau, Jordan) | `basalt` | Ibrahim et al. (2006) & Shaw et al. (2003, *J. Petrology* 44:1657–1679) |
| 7 | `earth_kilbourne_hole_nm` | Potrillo Volcanic Field (Kilbourne Hole Maar & Basalt Rim, New Mexico) | `basalt` | Seeger et al. (2019) & Padovani & Carter (1977) |
| 8 | `earth_qaidam_dalangtan` | Qaidam Basin (Dalangtan Hyperarid Evaporite Flat, China) | `evaporite` | Xiao et al. (2017, *ESR* 164:84–101) & Anglés & Li (2017, *JGR Planets*) |
| 9 | `earth_payunia_pampa_negra` | Payunia Volcanic Province (Pampa Negra Basalt & Lapilli Plain, Argentina) | `basalt` | Søager et al. (2013, *Chem. Geol.* 349–350:36–53) & Hernando et al. (2014, *JVGR* 272:1–19) |
| 10 | `earth_chajnantor_plateau` | Altiplano-Puna Complex (Chajnantor High-Altitude Ignimbrite Plateau, Chile) | `pyroclastic_tuff` | Salisbury et al. (2011, *GSA Bull.* 123:821–840) & de Silva (1989, *Geology* 17:1102–1106) |
| 11 | `earth_waw_an_namus_apron` | Waw an Namus Volcano (Dark Basaltic Tephra Apron, Fezzan, Libya) | `basalt` | Bardintzeff et al. (2012, *Chemie der Erde* 72:135–145) & Busrewil & Wadsworth (1983) |
| 12 | `earth_tibesti_tarso_voon` | Tibesti Volcanic Massif (Tarso Voon Ignimbrite & Basalt Plateau, Chad) | `pyroclastic_tuff` | Permenter & Oppenheimer (2007, *Bull. Volcanol.* 69:609–626) & Gourgaud & Vincent (2004, *JVGR* 129:261–294) |
| 13 | `earth_paricutin_lava_field` | Michoacán-Guanajuato Field (Parícutin Basaltic-Andesite Flow, Mexico) | `basalt` | Luhr & Simkin (1993) & Erlund et al. (2010, *Bull. Volcanol.* 72:347–363) |
| 14 | `earth_tolbachik_apron` | Tolbachik Volcanic Massif (Basalt Scoria & Lava Plain, Kamchatka) | `basalt` | Belousov et al. (2015, *JVGR* 307:22–37) & Fedotov et al. (1991) |
| 15 | `earth_kilauea_kau_desert` | Kīlauea SW Rift Zone (Kaʻū Desert Basalt & Tephra Plain, Hawaii) | `basalt` | Craddock et al. (2012, *JGR Planets* 117:E08009) & Schiffman et al. (2006, *Geology* 34:921–924) |
| 16 | `earth_tongariro_rangipo` | Tongariro Volcanic Centre (Rangipo Andesitic-Basaltic Tephra Plain, NZ) | `basalt` | Donoghue et al. (1995, *Bull. Volcanol.* 57:563–576) & Hobden et al. (1999, *J. Petrology* 40:1965–1990) |

---

## 4. Çapraz Belgeler Dizini

- [`docs/data_sources_moon.md`](data_sources_moon.md) — Emirhan'ın ayrıntılı Ay Güney Kutbu ölçüm, `×0.38` albedo hassasiyet ve Diviner `ltim01..ltim96` teknik raporu.
- [`docs/data_sources_earth.md`](data_sources_earth.md) — Eray'ın Dünya uydu ürünleri, yıllık `MOD11A2` denetimi, MTA 1:500.000 litoloji alt-sınıf notları ve Sentinel-2/WorldCover karışık piksel denetimi.
- [`docs/validation_expectations.md`](validation_expectations.md) — Eray'ın ön-kayıtlı `10 × 3` doğrulama beklenti matrisi ve E8 buz/permafrost envanteri.
- [`docs/data_notes.md`](data_notes.md) — Lider metodoloji kararları (CRS, `Karar #30` termal eksen askısı, Z-ölçekleme, Monte Carlo belirsizlik, `expanded_interval`).
