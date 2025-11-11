"""
ANPR Saldırı Simülasyonu - Görselleştirme Modülü
Simülasyon sonuçlarını grafiklerle görselleştirir.

Hazırlayan: Yusuf Kaymaz
Öğrenci No: 230541084
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import List, Dict
from anpr_attack_simulation import ANPRAttackSimulator, ChargingSession


# Türkçe karakter desteği için
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")
sns.set_palette("husl")


class ANPRVisualizer:
    """ANPR simülasyon sonuçlarını görselleştiren sınıf"""
    
    def __init__(self, simulator: ANPRAttackSimulator, results: List[Dict], metrics: Dict):
        """
        Görselleştirici başlatma
        
        Args:
            simulator: ANPR simülatör nesnesi
            results: Tespit sonuçları
            metrics: Performans metrikleri
        """
        self.simulator = simulator
        self.results = results
        self.metrics = metrics
        self.sessions = simulator.sessions
        
    def plot_confusion_matrix(self, save_path: str = 'confusion_matrix.png'):
        """Confusion Matrix (Karmaşıklık Matrisi) çiz"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        cm = np.array([
            [self.metrics['true_negatives'], self.metrics['false_positives']],
            [self.metrics['false_negatives'], self.metrics['true_positives']]
        ])
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Normal Tahmin', 'Saldırı Tahmin'],
                   yticklabels=['Gerçek Normal', 'Gerçek Saldırı'],
                   cbar_kws={'label': 'Oturum Sayısı'},
                   annot_kws={'size': 16, 'weight': 'bold'})
        
        ax.set_title('Confusion Matrix - ANPR Anomali Tespiti', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Tahmin Edilen Sınıf', fontsize=14, fontweight='bold')
        ax.set_ylabel('Gerçek Sınıf', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Confusion Matrix kaydedildi: {save_path}")
        plt.close()
        
    def plot_performance_metrics(self, save_path: str = 'performance_metrics.png'):
        """Performans metriklerini bar grafiği ile göster"""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        metrics_data = {
            'Doğruluk\n(Accuracy)': self.metrics['accuracy'] * 100,
            'Kesinlik\n(Precision)': self.metrics['precision'] * 100,
            'Duyarlılık\n(Recall)': self.metrics['recall'] * 100,
            'F1 Skoru': self.metrics['f1_score'] * 100
        }
        
        bars = ax.bar(metrics_data.keys(), metrics_data.values(), 
                     color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'],
                     edgecolor='black', linewidth=1.5, alpha=0.8)
        
        # Bar değerlerini üzerine yaz
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        ax.set_ylabel('Yüzde (%)', fontsize=14, fontweight='bold')
        ax.set_title('ANPR Anomali Tespit Sistemi - Performans Metrikleri', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_ylim([0, 105])
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Performans metrikleri grafiği kaydedildi: {save_path}")
        plt.close()
        
    def plot_anpr_confidence_distribution(self, save_path: str = 'anpr_confidence_dist.png'):
        """ANPR güven skoru dağılımı - normal vs saldırı"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        normal_confidence = [s.anpr_confidence for s in self.sessions if not s.is_fraudulent]
        attack_confidence = [s.anpr_confidence for s in self.sessions if s.is_fraudulent]
        
        # Histogram
        ax1.hist(normal_confidence, bins=30, alpha=0.7, label='Normal Oturum', 
                color='#2ecc71', edgecolor='black')
        ax1.hist(attack_confidence, bins=30, alpha=0.7, label='Saldırı Oturumu', 
                color='#e74c3c', edgecolor='black')
        ax1.axvline(self.simulator.anpr_confidence_threshold, color='orange', 
                   linestyle='--', linewidth=2, label='Güven Eşiği')
        ax1.set_xlabel('ANPR Güven Skoru', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Oturum Sayısı', fontsize=12, fontweight='bold')
        ax1.set_title('ANPR Güven Skoru Dağılımı', fontsize=14, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(alpha=0.3)
        
        # Box plot
        data = pd.DataFrame({
            'Oturum Tipi': ['Normal']*len(normal_confidence) + ['Saldırı']*len(attack_confidence),
            'ANPR Güven Skoru': normal_confidence + attack_confidence
        })
        sns.boxplot(data=data, x='Oturum Tipi', y='ANPR Güven Skoru', ax=ax2,
                   palette={'Normal': '#2ecc71', 'Saldırı': '#e74c3c'})
        ax2.axhline(self.simulator.anpr_confidence_threshold, color='orange', 
                   linestyle='--', linewidth=2, label='Güven Eşiği')
        ax2.set_title('ANPR Güven Skoru - Box Plot', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ ANPR güven skoru dağılımı kaydedildi: {save_path}")
        plt.close()
        
    def plot_risk_score_distribution(self, save_path: str = 'risk_score_dist.png'):
        """Risk skoru dağılımı"""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        normal_risks = [r['risk_score'] for r in self.results if not r['is_fraudulent']]
        attack_risks = [r['risk_score'] for r in self.results if r['is_fraudulent']]
        
        bins = np.linspace(0, 100, 21)
        ax.hist(normal_risks, bins=bins, alpha=0.6, label='Normal Oturum', 
               color='#2ecc71', edgecolor='black')
        ax.hist(attack_risks, bins=bins, alpha=0.6, label='Saldırı Oturumu', 
               color='#e74c3c', edgecolor='black')
        
        # Risk eşikleri
        ax.axvline(40, color='orange', linestyle='--', linewidth=2, 
                  label='Manuel Doğrulama Eşiği (40)')
        ax.axvline(60, color='red', linestyle='--', linewidth=2, 
                  label='Engelleme Eşiği (60)')
        
        ax.set_xlabel('Risk Skoru', fontsize=12, fontweight='bold')
        ax.set_ylabel('Oturum Sayısı', fontsize=12, fontweight='bold')
        ax.set_title('Risk Skoru Dağılımı - Anomali Tespit Sistemi', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper center', fontsize=10)
        ax.grid(alpha=0.3)
        
        # Risk bölgeleri renklendir
        ax.axvspan(0, 40, alpha=0.1, color='green', label='_nolegend_')
        ax.axvspan(40, 60, alpha=0.1, color='orange', label='_nolegend_')
        ax.axvspan(60, 100, alpha=0.1, color='red', label='_nolegend_')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Risk skoru dağılımı kaydedildi: {save_path}")
        plt.close()
        
    def plot_anomaly_types(self, save_path: str = 'anomaly_types.png'):
        """Tespit edilen anomali tipleri"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Tüm anomalileri say
        anomaly_counts = {}
        for result in self.results:
            if result['is_fraudulent']:
                for anomaly in result['anomalies']:
                    anomaly_counts[anomaly] = anomaly_counts.get(anomaly, 0) + 1
        
        # Anomali isimlerini Türkçeleştir
        anomaly_names = {
            'LOW_ANPR_CONFIDENCE': 'Düşük ANPR\nGüven Skoru',
            'GPS_MISMATCH': 'GPS\nUyuşmazlığı',
            'DEVICE_NOT_PRESENT': 'Cihaz\nBulunamadı',
            'WEATHER_LOW_CONFIDENCE': 'Hava Koşulu +\nDüşük Güven',
            'AMBIGUOUS_CHARACTERS': 'Belirsiz\nKarakterler'
        }
        
        sorted_anomalies = sorted(anomaly_counts.items(), key=lambda x: x[1], reverse=True)
        labels = [anomaly_names.get(k, k) for k, v in sorted_anomalies]
        values = [v for k, v in sorted_anomalies]
        
        bars = ax.barh(labels, values, color=sns.color_palette("Reds_r", len(labels)),
                      edgecolor='black', linewidth=1.5)
        
        # Bar değerlerini yaz
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{int(width)}',
                   ha='left', va='center', fontsize=12, fontweight='bold', 
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel('Tespit Sayısı', fontsize=12, fontweight='bold')
        ax.set_title('Saldırı Oturumlarında Tespit Edilen Anomali Tipleri', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Anomali tipleri grafiği kaydedildi: {save_path}")
        plt.close()
        
    def plot_weather_impact(self, save_path: str = 'weather_impact.png'):
        """Hava koşullarının ANPR güven skoruna etkisi"""
        fig, ax = plt.subplots(figsize=(14, 7))
        
        weather_data = {}
        for session in self.sessions:
            weather = session.weather_condition
            if weather not in weather_data:
                weather_data[weather] = []
            weather_data[weather].append(session.anpr_confidence)
        
        # Türkçe isimler
        weather_names = {
            'normal': 'Normal',
            'rain': 'Yağmurlu',
            'night': 'Gece',
            'fog': 'Sisli',
            'dirty_plate': 'Kirli Plaka'
        }
        
        data = []
        for weather, confidences in weather_data.items():
            for conf in confidences:
                data.append({
                    'Hava Koşulu': weather_names.get(weather, weather),
                    'ANPR Güven Skoru': conf
                })
        
        df = pd.DataFrame(data)
        sns.violinplot(data=df, x='Hava Koşulu', y='ANPR Güven Skoru', ax=ax,
                      palette='Set2', inner='box')
        
        ax.axhline(self.simulator.anpr_confidence_threshold, color='red', 
                  linestyle='--', linewidth=2, label='Güven Eşiği')
        ax.set_title('Hava Koşullarının ANPR Güven Skoruna Etkisi', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Hava Koşulu', fontsize=12, fontweight='bold')
        ax.set_ylabel('ANPR Güven Skoru', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Hava koşulları etkisi grafiği kaydedildi: {save_path}")
        plt.close()
        
    def plot_financial_impact(self, save_path: str = 'financial_impact.png'):
        """Finansal etki analizi"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Pie chart - Dolandırıcılık dağılımı
        sizes = [
            self.metrics['prevented_fraud_cost_tl'],
            self.metrics['undetected_fraud_cost_tl']
        ]
        labels = ['Önlenen\nDolandırıcılık', 'Tespit Edilemeyen\nKayıp']
        colors = ['#2ecc71', '#e74c3c']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, 
                                           colors=colors, autopct='%1.1f%%',
                                           shadow=True, startangle=90,
                                           textprops={'fontsize': 12, 'fontweight': 'bold'})
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(14)
        
        ax1.set_title('Dolandırıcılık Önleme Oranı', 
                     fontsize=14, fontweight='bold', pad=20)
        
        # Bar chart - Maliyet detayı
        categories = ['Toplam\nDolandırıcılık', 'Önlenen\nDolandırıcılık', 
                     'Tespit\nEdilemeyen']
        values = [
            self.metrics['total_fraud_cost_tl'],
            self.metrics['prevented_fraud_cost_tl'],
            self.metrics['undetected_fraud_cost_tl']
        ]
        colors_bar = ['#3498db', '#2ecc71', '#e74c3c']
        
        bars = ax2.bar(categories, values, color=colors_bar, 
                      edgecolor='black', linewidth=1.5, alpha=0.8)
        
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f} TL',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax2.set_ylabel('Maliyet (TL)', fontsize=12, fontweight='bold')
        ax2.set_title('Finansal Etki Analizi', fontsize=14, fontweight='bold', pad=20)
        ax2.grid(axis='y', alpha=0.3)
        
        # Y eksenini formatla
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Finansal etki grafiği kaydedildi: {save_path}")
        plt.close()
        
    def plot_detection_rate_by_attack_level(self, save_path: str = 'detection_by_level.png'):
        """Saldırı seviyesine göre tespit oranı"""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Saldırı seviyelerini güven skoruna göre grupla
        level_data = {
            'Yüksek Seviye\n(0.75-0.95)': {'detected': 0, 'missed': 0},
            'Orta Seviye\n(0.65-0.85)': {'detected': 0, 'missed': 0},
            'Düşük Seviye\n(0.45-0.75)': {'detected': 0, 'missed': 0}
        }
        
        for session, result in zip(self.sessions, self.results):
            if session.is_fraudulent:
                conf = session.anpr_confidence
                if 0.75 <= conf <= 0.95:
                    level = 'Yüksek Seviye\n(0.75-0.95)'
                elif 0.65 <= conf <= 0.85:
                    level = 'Orta Seviye\n(0.65-0.85)'
                else:
                    level = 'Düşük Seviye\n(0.45-0.75)'
                
                if result['should_block']:
                    level_data[level]['detected'] += 1
                else:
                    level_data[level]['missed'] += 1
        
        levels = list(level_data.keys())
        detected = [level_data[l]['detected'] for l in levels]
        missed = [level_data[l]['missed'] for l in levels]
        
        x = np.arange(len(levels))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, detected, width, label='Tespit Edildi', 
                      color='#2ecc71', edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, missed, width, label='Kaçırıldı', 
                      color='#e74c3c', edgecolor='black', linewidth=1.5)
        
        # Bar değerlerini yaz
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_xlabel('Saldırı Seviyesi (ANPR Güven Skoru Aralığı)', 
                     fontsize=12, fontweight='bold')
        ax.set_ylabel('Oturum Sayısı', fontsize=12, fontweight='bold')
        ax.set_title('Saldırı Seviyesine Göre Tespit Başarısı', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(levels)
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Seviye bazlı tespit grafiği kaydedildi: {save_path}")
        plt.close()
        
    def plot_roc_curve(self, save_path: str = 'roc_curve.png'):
        """ROC Eğrisi (Receiver Operating Characteristic)"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Risk skorlarını al ve sırala
        risk_scores = [(r['risk_score'], r['is_fraudulent']) for r in self.results]
        risk_scores.sort(key=lambda x: x[0], reverse=True)
        
        # Farklı eşikler için TPR ve FPR hesapla
        tpr_list = []
        fpr_list = []
        
        total_positives = sum(1 for _, is_fraud in risk_scores if is_fraud)
        total_negatives = len(risk_scores) - total_positives
        
        for threshold in np.linspace(0, 100, 101):
            tp = sum(1 for score, is_fraud in risk_scores if score >= threshold and is_fraud)
            fp = sum(1 for score, is_fraud in risk_scores if score >= threshold and not is_fraud)
            
            tpr = tp / total_positives if total_positives > 0 else 0
            fpr = fp / total_negatives if total_negatives > 0 else 0
            
            tpr_list.append(tpr)
            fpr_list.append(fpr)
        
        # ROC eğrisini çiz
        ax.plot(fpr_list, tpr_list, color='#3498db', linewidth=3, 
               label=f'ROC Eğrisi')
        ax.plot([0, 1], [0, 1], color='red', linestyle='--', linewidth=2, 
               label='Rastgele Tahmin')
        
        # AUC hesapla (basit trapezoid yöntemi)
        auc = np.trapz(tpr_list, fpr_list)
        
        ax.set_xlabel('Yanlış Pozitif Oranı (FPR)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Doğru Pozitif Oranı (TPR)', fontsize=12, fontweight='bold')
        ax.set_title(f'ROC Eğrisi - ANPR Anomali Tespiti\nAUC = {abs(auc):.3f}', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='lower right', fontsize=11)
        ax.grid(alpha=0.3)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ ROC eğrisi kaydedildi: {save_path}")
        plt.close()
        
    def generate_all_plots(self):
        """Tüm grafikleri oluştur"""
        print("\n" + "=" * 60)
        print("📊 GRAFİKLER OLUŞTURULUYOR...")
        print("=" * 60)
        
        self.plot_confusion_matrix()
        self.plot_performance_metrics()
        self.plot_anpr_confidence_distribution()
        self.plot_risk_score_distribution()
        self.plot_anomaly_types()
        self.plot_weather_impact()
        self.plot_financial_impact()
        self.plot_detection_rate_by_attack_level()
        self.plot_roc_curve()
        
        print("\n✅ Tüm grafikler başarıyla oluşturuldu!")
        print("=" * 60)


def main():
    """Görselleştirme ana fonksiyonu"""
    # Önce simülasyonu çalıştır
    from anpr_attack_simulation import main as run_simulation
    
    simulator, results, metrics = run_simulation()
    
    # Görselleştirici oluştur ve tüm grafikleri oluştur
    visualizer = ANPRVisualizer(simulator, results, metrics)
    visualizer.generate_all_plots()


if __name__ == "__main__":
    main()

