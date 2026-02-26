[README.md](https://github.com/user-attachments/files/25574331/README.md)
# 🚀 GoodbyeDPI Türkiye - Otomatik Konfigürasyon Seçici

GoodbyeDPI'nin 7 farklı konfigürasyonunu otomatik olarak dener, çalışanı bulur ve kurar.  
Farklı bilgisayarlarda tek tek deneme zahmetini ortadan kaldırır.

## Kullanım

1. [Python 3](https://www.python.org/downloads/) yükleyin (*kurulumda "Add to PATH" işaretleyin*)
2. `OTOMATIK_KONFIGÜRASYON_SEC.cmd` → **Sağ tık → Yönetici olarak çalıştır**
3. Script otomatik taramayı başlatır, sizden bir şey yapmanız gerekmez.

## Servis Kurulumu (E/H Seçimi)

Script çalışan konfigürasyonu bulduktan sonra size şunu sorar:

```
Servis olarak kurulsun mu?
[E] Evet - Windows servisi olarak kur
[H] Hayır - Sadece sonuçları kaydet
```

| Seçim | Ne olur? |
|:-----:|----------|
| **E** | GoodbyeDPI Windows servisi olarak kurulur. Bilgisayar her açıldığında **otomatik çalışır**, bir daha bu scripti çalıştırmanıza gerek kalmaz. |
| **H** | Servis kurulmaz. Sadece hangi konfigürasyonun çalıştığı `auto_selector_log.txt` dosyasına kaydedilir. İsterseniz daha sonra kendiniz kurabilirsiniz. |

## Kaldırma

Servisi kaldırmak için `service_remove.cmd` → **Sağ tık → Yönetici olarak çalıştır**.

## Gereksinimler

- Windows 7/8/10/11
- [Python 3.6+](https://www.python.org/downloads/)
- Yönetici yetkisi
