# Generative AI Kullanım Günlüğü

Amaç: Rapordaki **"Generative AI Usage Disclosure"** bölümünü gerçeğe dayandırmak (yönerge §15). Tarihli, kısa, dürüst tut. Kullanılan araç: Claude (Anthropic) — sohbet arayüzü ve Claude Code.

| Tarih | Araç | Amaç (kod geliştirme / hata ayıklama / kavram açıklama / dil düzenleme / literatür / doküman) | Ne üretildi / ne yapıldı | Öğrencinin doğrulaması |
|---|---|---|---|---|
| 2026-10-18 | Claude (sohbet) | doküman, planlama | Yönerge ve makale analiz edildi; proje dokümanları (`CLAUDE.md`, `docs/*`) ve klasör iskeleti hazırlandı | Dokümanlar PDF'lerle karşılaştırılacak (Faz 1) |
| 2026-10-18 | Claude Code | doküman doğrulama | `docs/02` makale PDF'iyle karşılaştırıldı (Eq. 1–29, Tablo 1–9); w=5/7 çelişkisi, ödül kümesi aritmetiği (floor/round), t/T, tablo numarası notları düzeltildi/eklendi | Düzeltmeler PDF sayfalarından teyit edilecek (s.3–4, 6, 9, 20) |
| 2026-11-10 | Claude Code | ortam kurulumu, doküman | git init + ilk commit; Python 3.12 `.venv`; dtcwt–NumPy 2 uyumsuzluğu tespit edilip `numpy<2` ile çözüldü; `requirements.lock.txt`; hocaya mesaj taslağı; kararlar D-023…D-025 | Öğrenci `.venv` içinde import testini kendisi çalıştırıp görmeli |
| 2026-11-10 | Claude Code | literatür, doküman | Makale kaynakçasından 23 ve Crossref/OpenAlex aramasıyla 10 güncel çalışma seçildi; 33 DOI'nin tamamı Crossref API ile doğrulandı (`references/verification/`); 6 abstract okundu (5 güncel + makalenin kendisi), okunamayanlar "V-meta" diye işaretlendi; karşılaştırma tablosu, CP1 notu, Türkçe literatür notları ve İngilizce Related Work taslağı yazıldı | Öğrenci tabloyu ve özetleri okuyup en az 3 kaynağın DOI'sini kendisi açmalı; [29]'u okumalı |
| 2026-11-11 | Claude Code | kod geliştirme, veri hazırlama, test | sy1–3 etiket haritaları makale Fig. 9'dan çıkarıldı (araç betiği); `noise.py`, `synthetic.py`, `bsds500.py`, `matching.py`, `metrics.py` ve 27 birim test yazıldı; BSDS500 resmi arşivden indirildi; gürültü tanımı kâhin-ACC kontrolüyle makaleye karşı sınandı; kararlar D-027…D-030 | Öğrenci testleri kendisi çalıştırmalı, `metrics.py`'deki el hesaplı test örneğini kâğıtta doğrulamalı, `noise_oracle_check.csv`'yi yorumlayabilmeli |
| | | | | |

**Doğrulama notu:** Claude'un ürettiği her kod parçası çalıştırılıp test edilir; her atıf DOI ile elle doğrulanır; her sonuç betikle yeniden üretilebilir olmalıdır.
