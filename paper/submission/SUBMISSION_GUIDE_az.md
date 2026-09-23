# Cryptography and Communications-a göndərmə təlimatı

## 1. Springer şablonunu əlavə et (5 dəq)
Bu qovluqda (`springer/`) məqalənin jurnal versiyası var: `main.tex`, `refs.bib`, `fig_degree.pdf`, `fig_ablation.pdf`.
Kompilyasiya üçün Springer-in rəsmi şablonundan **iki fayl** lazımdır, onları yükləyə bilmədim (sayt bu serverdən bağlıdır):

- `sn-jnl.cls`
- `sn-mathphys-num.bst`

Google-da **"Springer Nature LaTeX template"** axtar, springernature.com-dan zip-i yüklə, bu iki faylı `springer/` qovluğuna at.
Sonra: `pdflatex main` → `bibtex main` → `pdflatex main` → `pdflatex main` (və ya Overleaf-də "Springer Nature LaTeX Template"-i aç, fayllarımızı yüklə).

**Vacib:** `sn-mathphys-num.bst` şablonda `bst/` qovluğunun içindədir, amma class onu əsas qovluqda axtarır. Onu əsas qovluğa köçür, yoxsa istinadlar `[?]` görünür. Editorial Manager-ə yükləyəndə də bu fayl digərləri ilə eyni səviyyədə olmalıdır.

Kompilyasiyada xəta çıxsa, xəta mesajını mənə göndər, düzəldərəm. `main.tex` şablonun interfeysinə uyğun yazılıb, amma rəsmi class faylı ilə yoxlaya bilmədim.

## 2. Təsdiqləməli olduğun 3 cümlə (`main.tex`, "Declarations" bölməsi)
- **Funding:** "The authors did not receive support from any organization…" — maliyyə/qrant varsa dəyiş.
- **Author contributions:** rolları mən təxmini yazmışam (Ali: konsepsiya, metod, kod, analiz, yazı; Yadigar və Jalal: rəhbərlik, yoxlama, redaktə). Həmmüəlliflərlə razılaşdır.
- **Competing interests:** "yoxdur" + Dipper-in sizin əvvəlki işiniz olduğu qeyd olunub. Düzdürsə saxla.

## 3. GitHub
- Repo-nu push et.
- **Release** yarat və sertifikat arxivinin 3 zip hissəsini ora əlavə et. Məqalədə "release archive of the repository" yazılıb, bu cümlə doğru olmalıdır.
- (İstəyə görə) Zenodo ilə GitHub-u bağla, release-ə DOI al.

## 4. Sistemə yükləmə (Editorial Manager)
Jurnalın səhifəsi → **Submit manuscript**.
- Article type: Original Research (Research article)
- Title, Abstract (main.tex-dən köçür), Keywords (6 ədəd), MSC: `94A60, 94D10, 68P25`
- Müəlliflər + e-poçtlar + ORCID (sənin: 0009-0003-4959-2887)
- Fayllar: `main.tex`, `refs.bib`, 2 fiqur PDF, `sn-jnl.cls`, `sn-mathphys-num.bst` — **alt qovluq olmadan**
- Cover letter: `cover_letter.txt`-in mətnini yapışdır və ya fayl kimi yüklə
- Declarations sahələri (Funding, Competing interests, Data availability, Author contributions) — məqalədəki mətnlərin eynisini yaz
- Sistem PDF yaradacaq — **mütləq aç və yoxla** (fiqurlar, cədvəllər, istinadlar)

## 5. Qeydlər
- Nəşr haqqı yoxdur (subscription yolu). Open Access istəsən APC var, lazım deyil.
- Rəy müddəti adətən ~4 aya qədər.
- Single-blind review: rəyçilər adlarınızı görür, siz onlarınkını yox.
