/usr/local/bin/python3.14 /Users/esmasaritop/PycharmProjects/Cryptoholm-private/main_test.py 
DLT: DECISION_ECU_01 başarıyla kaydedildi.
DLT: LIDAR_SIM_01 başarıyla kaydedildi.

==================================================
SENARYO 1: YASAL (GÜVENLİ) MESAJ AKIŞI
==================================================

[YASAL]: Yasal Mesaj Gönderiliyor: '10m'de Araç Var'
DLT: Yeni işlem eklendi. (Beklemede)
DLT: Yeni blok (1) zincire eklendi. Hash: d1133fd60f...

[ECU]: Gelen Veri İşleniyor: {"distance": 10, "object": "car", "speed": 40}
[ECU KARAR]: Kritik Tehdit Algılandı! ACİL FRENLEME BAŞLATILDI.

[SENARYO 1 SONUÇ]: BAŞARILI. ECU Kararı: Başarılı

==================================================
SENARYO 2: ANOMALİ (SAHTE VERİ ENJEKSİYONU) TESTİ
Blokzincir bütünlüğü koruyacak mı?
==================================================

[ECU]: Gelen Veri İşleniyor: {"speed": 40, "distance": 50, "object": "none"}
GÜVENLİK REDDİ: Mesaj içeriği DLT'deki kayıt ile UYUŞMUYOR.

*** TEST BAŞARILI ***
Blokzincir/Hash Kontrolü, değiştirilmiş sensör verisini tespit etti ve reddetti.

Process finished with exit code 0
