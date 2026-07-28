<div align="center">

<img src="docs/images/figures/00-logo-polsri.png" width="110" alt="Politeknik Negeri Sriwijaya">

# Dadu Digital — Dua Seven-Segment, Waktu Spin Berbeda

**Dua dadu d6 independen yang dibangun sepenuhnya dari logika diskrit. Tanpa mikrokontroler, tanpa firmware, tanpa satu baris kode pun di jalur sinyal.**

Sebuah pencacah desimal CD4017 dilipat menjadi pencacah mod-6, dan tepat tiga gerbang OR menerjemahkan keluaran one-hot-nya menjadi BCD yang dipahami 74LS47 — sehingga angka 0, 7, 8, dan 9 bukan disaring lewat program, melainkan **secara struktural tidak punya jalur listrik** menuju display.

[![Logika Terverifikasi](https://img.shields.io/badge/logika-terverifikasi%20formal-2ea44f?style=flat-square)](#verifikasi)
[![Jumlah Gerbang](https://img.shields.io/badge/gerbang%20OR-3%20per%20kanal-blue?style=flat-square)](#gagasan-intinya)
[![Mikrokontroler](https://img.shields.io/badge/mikrokontroler-tidak%20ada-lightgrey?style=flat-square)](#filosofi-desain)
[![Mata Kuliah](https://img.shields.io/badge/mata%20kuliah-Elektronika%20Digital-orange?style=flat-square)](#tentang-proyek)
[![Lisensi](https://img.shields.io/badge/lisensi-CC%20BY--NC--SA%204.0-informational?style=flat-square)](LICENSE)

<img src="docs/images/build/build-01.jpg" width="440" alt="Alat dadu digital">

*Politeknik Negeri Sriwijaya · Teknik Elektro · Proyek Semester 3 · 2024*

**[English →](README.md)**

</div>

---

## Daftar Isi

- [Gagasan intinya](#gagasan-intinya)
- [Filosofi desain](#filosofi-desain)
- [Cara kerja](#cara-kerja)
- [Verifikasi](#verifikasi)
- [Timing dan dua kecepatan spin](#timing-dan-dua-kecepatan-spin)
- [Daftar komponen](#daftar-komponen)
- [Struktur repositori](#struktur-repositori)
- [Mulai dari mana](#mulai-dari-mana)
- [Galeri](#galeri)
- [Keterbatasan yang diketahui](#keterbatasan-yang-diketahui)
- [Dokumentasi](#dokumentasi)
- [Tentang proyek](#tentang-proyek)
- [Penulis](#penulis)

---

## Gagasan intinya

Dadu menampilkan 1 sampai 6. CD4017 mencacah 0 sampai 9. 74LS47 berbicara dalam BCD. Menjembatani ketiga fakta itu adalah keseluruhan persoalan desainnya — dan bagian menariknya adalah betapa murah jembatan itu bisa dibuat.

Ada dua kendala yang harus dipenuhi sekaligus:

1. **Cacahan harus berputar setelah enam keadaan.** Diselesaikan dengan mengumpanbalikkan `Q6` ke Master Reset pencacah itu sendiri. Begitu keadaan ketujuh hendak muncul, ia menghapus dirinya sendiri — sebuah *glitch* selebar puluhan nanodetik yang tidak pernah sempat ditampilkan.

2. **Setiap keluaran one-hot harus menjadi angka BCD.** CD4017 mengaktifkan tepat satu dari `Q0..Q5` pada satu waktu, sedangkan 74LS47 menginginkan kode biner berbobot 4 bit. Menuliskan ekspansi biner keenam angka target membuat jawabannya muncul sendiri:

| Angka | D (8) | C (4) | B (2) | A (1) |
|:-----:|:-----:|:-----:|:-----:|:-----:|
| 1 | 0 | 0 | 0 | **1** |
| 2 | 0 | 0 | **1** | 0 |
| 3 | 0 | 0 | **1** | **1** |
| 4 | 0 | **1** | 0 | 0 |
| 5 | 0 | **1** | 0 | **1** |
| 6 | 0 | **1** | **1** | 0 |

Baca tabel itu per **kolom**, bukan per baris, dan logikanya menulis dirinya sendiri:

```
A = Q0 + Q2 + Q4        (bit 1 aktif untuk angka 1, 3, 5)
B = Q1 + Q2 + Q5        (bit 2 aktif untuk angka 2, 3, 6)
C = Q3 + Q4 + Q5        (bit 4 aktif untuk angka 4, 5, 6)
D = GND                 (bit 8 tidak pernah aktif di bawah 8)
```

Tiga suku OR, masing-masing tiga masukan. CD4075 berisi **tiga gerbang OR 3-input dalam satu kemasan** — kebutuhan dan komponennya cocok persis, tanpa sisa dan tanpa kurang.

Poin terakhir itulah yang membuat desain ini layak dipamerkan. `D` bukan sekadar tidak dipakai; ia **diikat ke ground**. Angka 8 dan 9 sama sekali tidak punya jalur listrik menuju display. Dan karena `Q6` tak pernah bertahan cukup lama untuk didekode, 0 dan 7 pun tidak.

Aturan "dadu menampilkan 1 sampai 6" ditegakkan oleh topologi papan rangkaian, bukan oleh sebuah kondisi program yang bisa salah tulis.

> [!NOTE]
> Versi mikrokontroler dari proyek ini kira-kira empat baris kode. Versi itu juga bisa menampilkan `7` kalau modulusnya salah tulis. Versi ini tidak bisa — dan mendemonstrasikan perbedaan itu adalah inti dari latihan ini.

---

## Filosofi desain

| Keputusan | Alasan |
|---|---|
| **Tanpa mikrokontroler** | Mata kuliahnya Elektronika Digital. Menyembunyikan *state machine* di dalam firmware berarti menyembunyikan justru materi yang sedang dinilai. |
| **CD4017 + CD4075 + 74LS47**, bukan CD4026 | CD4026 menyatukan pencacah dan driver segmen — lebih ringkas, tetapi membuat pembatasan 1–6 jadi canggung dan tak terlihat. Memisahkan peran membuka bus BCD, tempat pembatasan itu bisa dinyatakan secara eksplisit dan terukur. Lihat [THEORY.md](docs/THEORY.md#why-not-the-cd4026). |
| **`Q6 → MR`, bukan menggerbang clock** | Reset asinkron bersifat seketika dan tidak butuh komponen tambahan. Menggerbang clock butuh latch dan memunculkan keadaan-antara yang terlihat. |
| **Dua osilator terpisah** | Dengan satu clock bersama, kedua display maju serempak dan selalu menunjukkan angka yang sama — satu dadu ditampilkan dua kali, bukan dua dadu. |
| **`D` di-ground, bukan dibiarkan mengambang** | Masukan CMOS dan TTL tidak boleh mengambang. `D` yang mengambang akan menangkap derau dan bisa sesaat terdekode sebagai 8 atau 9. |

---

## Cara kerja

<div align="center">
<img src="docs/images/figures/16-blok-diagram.png" width="600" alt="Blok diagram">
</div>

Jalur sinyal per kanal:

```
  NE555          CD4017           CD4075          74LS47        7-segment
 astabil  --->  pencacah  --->   3 x OR_3  --->  BCD ke    --->  common
  clock         desimal          pemetaan        7-seg          anode
                   |                              |
                   +-- Q6 -> MR                   +-- D ke GND
                       (lipatan mod-6)                (8 dan 9 mustahil)
```

**Tahap 1 — NE555 astabil.** Gelombang kotak bebas. Frekuensinya menentukan seberapa cepat angka berganti, dan karenanya menentukan apakah display terbaca sebagai *spin* atau sebagai *hitungan*.

**Tahap 2 — CD4017.** Maju satu keluaran setiap tepi naik clock. Perhatikan bahwa keluaran terdekodenya **tidak** urut nomor pin — `Q5` ada di pin 1, `Q0` di pin 3. Ini kesalahan perakitan paling umum pada rangkaian ini.

**Tahap 3 — CD4075.** Tiga gerbang OR hasil penurunan di atas. Murni kombinasional; tanpa clock, tanpa memori.

**Tahap 4 — 74LS47.** BCD masuk, tujuh jalur segmen keluar. Keluarannya **aktif RENDAH**, karena itulah display **harus common anode** — keluaran rendah menarik arus keluar dari segmen. Memasang display common cathode di sini menghasilkan pola terbalik yang tak bermakna.

**Tahap 5 — Display.** Resistor seri di setiap jalur segmen. Bukan opsional; lihat [ASSEMBLY.md](docs/ASSEMBLY.md#segment-current-limiting).

Penjelasan lengkap beserta tabel kebenaran dan detail per pin ada di **[docs/THEORY.md](docs/THEORY.md)**.

---

## Verifikasi

Klaim logika di atas tidak sekadar dinyatakan — ia diuji. `tools/logic_verify.py` menelusuri secara menyeluruh pencacah, jaringan OR, dan dekoder, lalu gagal dengan keras bila ada lapisan yang salah.

```bash
python3 tools/logic_verify.py --table
```

```
[counter (mod-6 feedback)]
  counter cycle       : Q0 -> Q1 -> Q2 -> Q3 -> Q4 -> Q5 -> (repeat)
  cycle length        : 6 states, as required for a d6
  negative control    : Q5 -> MR gives 5 states (rejected)
  negative control    : Q7 -> MR gives 7 states (rejected)

[combinational mapping]
  decoded digits      : [1, 2, 3, 4, 5, 6]
  gate widths         : {'A': 3, 'B': 3, 'C': 3} -> fits one CD4075 exactly
  forbidden digits    : 0, 7, 8, 9 all unreachable

[end-to-end chain]

  clk  4017    A B C D   BCD   digit   segments lit
  ----------------------------------------------------
    0  Q0      1 0 0 0   0001     1     bc
    1  Q1      0 1 0 0   0010     2     abdeg
    2  Q2      1 1 0 0   0011     3     abcdg
    3  Q3      0 0 1 0   0100     4     bcfg
    4  Q4      1 0 1 0   0101     5     acdfg
    5  Q5      0 1 1 0   0110     6     cdefg

       _     _           _
  |    _|    _|   |_|   |_    |_
  |   |_     _|     |    _|   |_|

All checks passed. The three-OR-gate design is correct.
```

Kontrol negatif sama pentingnya dengan yang positif. Kalau `Q5` atau `Q7` juga menghasilkan siklus enam keadaan yang bersih, pengujiannya tidak membuktikan apa pun tentang pemilihan `Q6`. Skrip ini dijalankan otomatis setiap push lewat [GitHub Actions](.github/workflows/verify.yml).

---

## Timing dan dua kecepatan spin

Kedua kanal memakai rangkaian astabil NE555 standar:

$$f = \frac{1.44}{(R_1 + 2R_2)\,C}$$

Satu angka ditampilkan selama tepat satu periode clock, terlepas dari duty cycle — CD4017 hanya peduli pada tepi naik.

Yang berbeda antar kanal hanyalah kapasitor timing:

| Kanal | C | Frekuensi | Satu angka | Siklus 1→6 | Terlihat sebagai |
|---|---|---|---|---|---|
| 1 (cepat) | 10 µF | 9,43 Hz | 106 ms | 636 ms | kedip cepat |
| 2 (lambat) | 100 µF | 0,94 Hz | 1,06 s | 6,36 s | hitungan terbaca |

Rasio 10×, dan itulah maksudnya: kedua display tidak pernah sefase, sehingga menghentikannya menghasilkan dua hasil yang benar-benar independen — bukan angka yang sama dua kali.

```bash
python3 tools/timing_calculator.py            # kedua kanal seperti yang dibangun
python3 tools/timing_calculator.py --sweep    # tabel pemilihan kapasitor
python3 tools/timing_calculator.py --target-hz 30 --c 1u   # cari nilai R2
```

> [!TIP]
> Pada 9,4 Hz kanal "cepat" berkedip, bukan mengabur — pemain masih bisa mengikuti angkanya dan mengatur waktu tekan tombol. *Persistence of vision* butuh sekitar **20 Hz ke atas** sebelum angka benar-benar tak terbaca. Menurunkan C ke **1–2,2 µF** memindahkan kanal cepat ke 42–94 Hz dan membuat spin-nya terasa jujur. Ini perubahan pertama yang sebaiknya dilakukan pada revisi; penalarannya diuraikan di [THEORY.md](docs/THEORY.md#choosing-the-spin-rate).

---

## Daftar komponen

Jumlah untuk satu unit lengkap dua display.

| # | Komponen | Jml | Peran |
|---|---|:---:|---|
| 1 | NE555 timer | 2 | Sumber clock, satu per kanal |
| 2 | CD4017 pencacah desimal | 2 | Pengurut mod-6 |
| 3 | CD4075 triple OR 3-input | 2 | Pemetaan one-hot → BCD |
| 4 | 74LS47 BCD → 7-segment | 2 | Driver display, aktif rendah |
| 5 | Display 7-segment, **common anode** | 2 | Keluaran |
| 6 | Resistor 5,1 kΩ | 4 | Jaringan timing NE555 |
| 7 | Resistor 1 kΩ | 2 | Pull-down Master Reset CD4017 |
| 8 | Resistor 220 Ω | 14 | Pembatas arus segmen |
| 9 | Kapasitor 10 µF | 1 | Timing, kanal cepat |
| 10 | Kapasitor 100 µF | 1 | Timing, kanal lambat |
| 11 | Kapasitor 100 nF | 4+ | Decoupling, satu per IC |
| 12 | Push button | 3 | Spin / stop / reset |
| 13 | Catu daya 5 V teregulasi | 1 | Lihat peringatan di bawah |
| 14 | Kabel jumper, breadboard/PCB | — | — |

> [!WARNING]
> Proposal awal mencantumkan catu daya **12 V**. 74LS47 adalah komponen TTL dengan **batas mutlak 7 V** — 12 V akan merusaknya. CD4017 dan CD4075 tahan 3–15 V, tetapi begitu ada komponen TTL di rel yang sama, seluruh papan menjadi papan 5 V. Pembahasan lengkap di [BOM.md](docs/BOM.md#supply-voltage).

Catatan pembelian, substitusi, dan toleransi selengkapnya: **[docs/BOM.md](docs/BOM.md)**

---

## Struktur repositori

```
dadu-digital-7segment/
├── README.md                      Versi Inggris
├── README.id.md                   Berkas ini
├── LICENSE                        CC BY-NC-SA 4.0
├── CONTRIBUTING.md
├── docs/
│   ├── THEORY.md                  Penurunan, tabel kebenaran, rasional desain
│   ├── ASSEMBLY.md                Urutan perakitan, peta pin, prosedur pengujian
│   ├── BOM.md                     Komponen, substitusi, tegangan catu
│   ├── TROUBLESHOOTING.md         Gejala → penyebab → perbaikan
│   ├── Laporan-Akhir-...docx      Laporan akademik asli
│   ├── Proposal-Awal-...pdf       Proposal awal, desain CD4026
│   ├── datasheets/                Tautan dan salinan datasheet
│   └── images/
│       ├── figures/               Gambar dari laporan
│       └── build/                 Foto alat yang sudah dirakit
├── hardware/
│   ├── schematic/                 Ekspor skematik (PDF)
│   ├── netlist/digital-dice.net   Referensi koneksi per pin
│   └── enclosure/                 Desain casing 3D
├── simulation/                    Catatan Proteus / Falstad / LTspice
├── tools/
│   ├── logic_verify.py            Verifikasi formal logika
│   └── timing_calculator.py       Alat bantu desain NE555
└── .github/workflows/verify.yml   CI: menjalankan verifikasi tiap push
```

---

## Mulai dari mana

**Untuk memahami desainnya** — baca [THEORY.md](docs/THEORY.md), lalu jalankan `python3 tools/logic_verify.py --table`. Tidak butuh perangkat keras maupun dependensi; kedua tool memakai Python 3.9+ standar saja.

**Untuk membangunnya** — mulai dari [BOM.md](docs/BOM.md), lalu ikuti [ASSEMBLY.md](docs/ASSEMBLY.md). Rakit dan uji **satu kanal sampai tuntas** sebelum memulai kanal kedua. Kanal yang sudah bekerja adalah pembanding yang akan Anda butuhkan saat kanal kedua bermasalah.

**Untuk mensimulasikannya lebih dulu** — [simulation/README.md](simulation/README.md) membahas Proteus, Falstad, dan Logisim, termasuk komponen apa yang disubstitusi masing-masing tool dan di mana simulasi menyimpang dari papan fisik.

```bash
git clone https://github.com/revaldinotr/dadu-digital-7segment.git
cd dadu-digital-7segment
python3 tools/logic_verify.py --table
python3 tools/timing_calculator.py
```

---

## Galeri

<div align="center">

<table>
<tr>
<td width="33%"><img src="docs/images/figures/17-desain-rangkaian.png" alt="Desain rangkaian"></td>
<td width="33%"><img src="docs/images/figures/18-desain-3d.png" alt="Desain 3D"></td>
<td width="33%"><img src="docs/images/build/build-02.jpg" alt="Alat jadi"></td>
</tr>
<tr>
<td align="center"><sub>Skematik</sub></td>
<td align="center"><sub>Desain casing</sub></td>
<td align="center"><sub>Alat jadi</sub></td>
</tr>
<tr>
<td><img src="docs/images/build/build-03.jpg" alt="Detail perakitan"></td>
<td><img src="docs/images/build/build-05.jpg" alt="Pengujian"></td>
<td><img src="docs/images/build/build-06.jpg" alt="Pengujian"></td>
</tr>
<tr>
<td align="center"><sub>Pengawatan</sub></td>
<td align="center"><sub>Uji meja</sub></td>
<td align="center"><sub>Uji meja</sub></td>
</tr>
</table>

</div>

---

## Keterbatasan yang diketahui

Dinyatakan terus terang, karena halaman proyek yang mengaku tanpa kelemahan tidak kredibel.

| Keterbatasan | Rincian |
|---|---|
| **Bukan acak kriptografis** | Hasilnya adalah pencacah deterministik yang dicuplik pada saat yang dipilih manusia. Entropinya berasal dari waktu reaksi pemain relatif terhadap fase clock — memadai untuk permainan papan, tidak untuk hal lain. |
| **Kanal lambat bisa "diakali"** | Pada 0,94 Hz pemain bisa mengamati urutannya dan menekan tombol dengan sengaja. Ini cacat keadilan, bukan sekadar estetika. Lihat [THEORY.md](docs/THEORY.md#choosing-the-spin-rate). |
| **Kanal cepat berkedip, bukan mengabur** | 9,4 Hz berada di bawah ambang *persistence of vision*. Sudah didokumentasikan beserta perbaikannya di atas. |
| **Dua osilator bisa berdenyut (beat)** | Dengan kapasitor toleransi ±20 %, kedua kanal saling menghanyut — di sini justru diinginkan, tetapi berarti rasio persisnya tidak sama antar unit. |
| **Tanpa debouncing** | Tombol terhubung langsung. Pantulan kontak dapat menyuntikkan tepi clock tambahan. Kapasitor 100 nF di kontak saklar, atau inverter Schmitt 74HC14, akan mengatasinya. |
| **Direkonstruksi dari dokumentasi** | Referensi netlist ditranskripsi dari ekspor skematik yang tidak menganotasi setiap resistor per kanal. Nilai bertanda "verify" di [digital-dice.net](hardware/netlist/digital-dice.net) sebaiknya diukur sebelum dikutip. |

---

## Dokumentasi

| Dokumen | Isi |
|---|---|
| [docs/THEORY.md](docs/THEORY.md) | Penurunan lengkap pemetaan OR, lipatan mod-6, tabel kebenaran, analisis kecepatan spin, alasan tidak memakai CD4026 |
| [docs/ASSEMBLY.md](docs/ASSEMBLY.md) | Urutan perakitan bertahap, peta pin lengkap, prosedur pengujian |
| [docs/BOM.md](docs/BOM.md) | Daftar komponen, substitusi, analisis tegangan catu, sumber pembelian |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Gejala → penyebab → perbaikan, diurutkan berdasarkan frekuensi kejadian |
| [hardware/netlist/digital-dice.net](hardware/netlist/digital-dice.net) | Referensi koneksi per pin |
| [simulation/README.md](simulation/README.md) | Simulasi di Proteus, Falstad, Logisim |

---

## Tentang proyek

Tugas proyek mata kuliah **Elektronika Digital**, semester 3, Program Studi Teknik Elektronika, Jurusan Teknik Elektro, **Politeknik Negeri Sriwijaya**, Palembang — 2024.

Judul asli: *Perancangan dan Implementasi Sistem Dadu Digital Dua Display dengan Waktu Spin Berbeda*.

Dosen pembimbing: **Ratna Atika, S.T., M.T.**

Laporan akademik lengkap tersimpan utuh di [`docs/`](docs/). Repositori ini menyusun ulang karya tersebut sebagai artefak rekayasa: penalarannya dibuat eksplisit, klaimnya dibuat terverifikasi, dan kekeliruan yang ditemukan saat peninjauan didokumentasikan alih-alih diperbaiki diam-diam.

---

## Penulis

**Tim OhmFusion — Kelompok 6**

<table>
  <thead>
    <tr>
      <th align="left">Penulis</th>
      <th align="left">NIM</th>
      <th align="left">Kontribusi</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="left"><a href="https://www.linkedin.com/in/revaldino"><b>Reval Dino Try Rahmady</b></a></td>
      <td align="left">062330320631</td>
      <td align="left">Ketua tim · desain skematik · jaringan timing</td>
    </tr>
    <tr>
      <td align="left"><b>Alsya Amanda Putri</b></td>
      <td align="left">062330320612</td>
      <td align="left">Logika kombinasional · tabel kebenaran · laporan</td>
    </tr>
    <tr>
      <td align="left"><b>M. Indra Cahaya</b></td>
      <td align="left">062330320620</td>
      <td align="left">Perakitan · desain casing · pengujian</td>
    </tr>
  </tbody>
</table>

> [!NOTE]
> Kolom kontribusi merupakan perkiraan dari laporan dan sebaiknya dikoreksi tim sebelum dipublikasikan.

---

## Lisensi

Dirilis di bawah [CC BY-NC-SA 4.0](LICENSE). Anda boleh membagikan dan mengadaptasi karya ini untuk tujuan non-komersial dengan atribusi, di bawah lisensi yang sama. Ini karya akademik — mohon cantumkan penulisnya bila Anda mengembangkannya.

<div align="center">
<br>

**[github.com/revaldinotr/dadu-digital-7segment](https://github.com/revaldinotr/dadu-digital-7segment)**

<sub>Politeknik Negeri Sriwijaya · Elektronika Digital · 2024</sub>

</div>
