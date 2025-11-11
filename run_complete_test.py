#!/usr/bin/env python3
"""
ANPR Saldırı Simülasyonu - Tam Test Suite
Tüm testleri çalıştırır, sonuçları raporlar ve grafikleri oluşturur.

Kullanım:
    python run_complete_test.py
    
veya:
    chmod +x run_complete_test.py
    ./run_complete_test.py

Hazırlayan: Yusuf Kaymaz
Öğrenci No: 230541084
Ders: Bilgi Sistemleri Güvenliği
"""

import sys
import time
from datetime import datetime


def print_header():
    """Başlık yazdır"""
    print("\n" + "=" * 70)
    print("  🚗 ANPR (PLAKA TANIMA) YANILTMA SALDIRISI SİMÜLASYONU")
    print("=" * 70)
    print(f"  Hazırlayan: Yusuf Kaymaz")
    print(f"  Öğrenci No: 230541084")
    print(f"  Ders: Bilgi Sistemleri Güvenliği")
    print(f"  Tarih: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70 + "\n")


def print_section(title):
    """Bölüm başlığı yazdır"""
    print("\n" + "─" * 70)
    print(f"  {title}")
    print("─" * 70 + "\n")


def check_dependencies():
    """Gerekli kütüphaneleri kontrol et"""
    print_section("📦 BAĞIMLILIK KONTROLÜ")
    
    required_packages = {
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'matplotlib': 'Matplotlib',
        'seaborn': 'Seaborn'
    }
    
    missing_packages = []
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {name} kurulu")
        except ImportError:
            print(f"  ❌ {name} BULUNAMADI!")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n  ⚠️  EKSIK PAKETLER: {', '.join(missing_packages)}")
        print(f"  \n  Yüklemek için:")
        print(f"  pip install {' '.join(missing_packages)}")
        print(f"\n  veya:")
        print(f"  pip install -r requirements.txt\n")
        return False
    
    print("\n  ✅ Tüm bağımlılıklar mevcut!\n")
    return True


def run_simulation():
    """Simülasyonu çalıştır"""
    print_section("🎯 1. SİMÜLASYON ÇALIŞTIRILIYOR")
    
    try:
        from anpr_attack_simulation import ANPRAttackSimulator
        
        print("  Simülatör başlatılıyor...")
        simulator = ANPRAttackSimulator(num_legitimate_users=100, num_stations=10)
        
        print("  Simülasyon çalıştırılıyor (bu birkaç saniye sürebilir)...")
        start_time = time.time()
        
        results = simulator.run_simulation(
            num_normal=800,
            num_attacks=200,
            attack_distribution={'low': 50, 'medium': 100, 'high': 50}
        )
        
        elapsed_time = time.time() - start_time
        print(f"\n  ✅ Simülasyon tamamlandı! ({elapsed_time:.2f} saniye)")
        
        return simulator, results
        
    except Exception as e:
        print(f"\n  ❌ HATA: Simülasyon çalıştırılamadı!")
        print(f"  Hata mesajı: {str(e)}")
        return None, None


def calculate_and_display_metrics(simulator, results):
    """Metrikleri hesapla ve göster"""
    print_section("📊 2. PERFORMANS METRİKLERİ HESAPLANIYOR")
    
    try:
        metrics = simulator.calculate_metrics(results)
        
        print("  " + "=" * 66)
        print("  📈 PERFORMANS METRİKLERİ")
        print("  " + "=" * 66)
        print(f"  Toplam Oturum: {metrics['total_sessions']}")
        print(f"  Sahte Oturum: {metrics['fraudulent_sessions']}")
        print(f"  Engellenen Oturum: {metrics['blocked_sessions']}")
        print(f"\n  Doğru Pozitif (TP): {metrics['true_positives']}")
        print(f"  Yanlış Pozitif (FP): {metrics['false_positives']}")
        print(f"  Doğru Negatif (TN): {metrics['true_negatives']}")
        print(f"  Yanlış Negatif (FN): {metrics['false_negatives']}")
        print(f"\n  Doğruluk (Accuracy): {metrics['accuracy']*100:.2f}%")
        print(f"  Kesinlik (Precision): {metrics['precision']*100:.2f}%")
        print(f"  Duyarlılık (Recall): {metrics['recall']*100:.2f}%")
        print(f"  F1 Skoru: {metrics['f1_score']*100:.2f}%")
        print(f"\n  💰 FİNANSAL ETKİ")
        print(f"  Toplam Dolandırıcılık Maliyeti: {metrics['total_fraud_cost_tl']:,.2f} TL")
        print(f"  Önlenen Dolandırıcılık: {metrics['prevented_fraud_cost_tl']:,.2f} TL")
        print(f"  Tespit Edilemeyen Kayıp: {metrics['undetected_fraud_cost_tl']:,.2f} TL")
        print(f"  Dolandırıcılık Önleme Oranı: {metrics['fraud_prevention_rate']:.2f}%")
        print("  " + "=" * 66)
        
        # JSON'a kaydet
        simulator.save_results(results, metrics)
        
        return metrics
        
    except Exception as e:
        print(f"\n  ❌ HATA: Metrikler hesaplanamadı!")
        print(f"  Hata mesajı: {str(e)}")
        return None


def generate_visualizations(simulator, results, metrics):
    """Görselleştirmeleri oluştur"""
    print_section("📈 3. GRAFİKLER OLUŞTURULUYOR")
    
    try:
        from visualization import ANPRVisualizer
        
        visualizer = ANPRVisualizer(simulator, results, metrics)
        
        print("  Grafikler oluşturuluyor...")
        visualizer.generate_all_plots()
        
        print("\n  ✅ Tüm grafikler başarıyla oluşturuldu!")
        
        return True
        
    except Exception as e:
        print(f"\n  ❌ HATA: Grafikler oluşturulamadı!")
        print(f"  Hata mesajı: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def display_summary():
    """Özet rapor göster"""
    print_section("📋 4. ÖZET RAPOR")
    
    print("  ✅ Oluşturulan Dosyalar:")
    print("     • simulation_results.json - Simülasyon sonuçları")
    print("     • confusion_matrix.png - Karmaşıklık matrisi")
    print("     • performance_metrics.png - Performans metrikleri")
    print("     • anpr_confidence_dist.png - ANPR güven skoru dağılımı")
    print("     • risk_score_dist.png - Risk skoru dağılımı")
    print("     • anomaly_types.png - Anomali tipleri")
    print("     • weather_impact.png - Hava koşulları etkisi")
    print("     • financial_impact.png - Finansal etki")
    print("     • detection_by_level.png - Seviye bazlı tespit")
    print("     • roc_curve.png - ROC eğrisi")
    
    print("\n  📚 Ek Belgeler:")
    print("     • swot_analizi.md - Kapsamlı SWOT analizi")
    print("     • README.md - Proje dokümantasyonu")
    
    print("\n  💡 Öneriler:")
    print("     • Grafikleri görüntülemek için PNG dosyalarını açın")
    print("     • Detaylı sonuçlar için simulation_results.json'ı inceleyin")
    print("     • SWOT analizi için swot_analizi.md'yi okuyun")


def main():
    """Ana program akışı"""
    print_header()
    
    # 1. Bağımlılık kontrolü
    if not check_dependencies():
        print("\n  ⚠️  Lütfen önce gerekli paketleri yükleyin!")
        sys.exit(1)
    
    # 2. Simülasyonu çalıştır
    simulator, results = run_simulation()
    if simulator is None or results is None:
        print("\n  ❌ Test başarısız oldu!")
        sys.exit(1)
    
    # 3. Metrikleri hesapla ve göster
    metrics = calculate_and_display_metrics(simulator, results)
    if metrics is None:
        print("\n  ❌ Test başarısız oldu!")
        sys.exit(1)
    
    # 4. Grafikleri oluştur
    visualization_success = generate_visualizations(simulator, results, metrics)
    
    # 5. Özet rapor
    display_summary()
    
    # Sonuç
    print("\n" + "=" * 70)
    if visualization_success:
        print("  ✅ TÜM TESTLER BAŞARIYLA TAMAMLANDI!")
    else:
        print("  ⚠️  Testler tamamlandı ancak bazı grafikler oluşturulamadı.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ⚠️  İşlem kullanıcı tarafından iptal edildi!")
        sys.exit(0)
    except Exception as e:
        print(f"\n  ❌ BEKLENMEDİK HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

