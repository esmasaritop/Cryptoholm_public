# False Positive Simulation Module
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

def generate_detection_scenario(num_events=100, threat_rate=0.2, false_positive_rate=0.15):
    """
    Gerçek tehdit ve algılama senaryosu oluşturur.

    Args:
        num_events: Toplam olay sayısı
        threat_rate: Gerçek tehdit oranı
        false_positive_rate: Yanlış alarm oranı
    """
    # Gerçek durumlar (0=normal, 1=tehdit)
    y_true = np.random.choice([0, 1], size=num_events, p=[1-threat_rate, threat_rate])

    # Tahmin edilen durumlar (başlangıçta gerçek durumla aynı)
    y_pred = y_true.copy()

    # Yanlış pozitif ekle (normal olayları tehdit olarak işaretle)
    normal_indices = np.where(y_true == 0)[0]
    num_false_positives = int(len(normal_indices) * false_positive_rate)
    false_positive_indices = np.random.choice(normal_indices, num_false_positives, replace=False)
    y_pred[false_positive_indices] = 1

    # Yanlış negatif ekle (bazı tehditleri kaçır)
    threat_indices = np.where(y_true == 1)[0]
    num_false_negatives = int(len(threat_indices) * 0.1)  # %10 kaçırma oranı
    if num_false_negatives > 0:
        false_negative_indices = np.random.choice(threat_indices, num_false_negatives, replace=False)
        y_pred[false_negative_indices] = 0

    return y_true, y_pred

def analyze_false_positives(y_true, y_pred):
    """
    Yanlış pozitifleri analiz eder ve metrikleri gösterir.
    """
    print("\n--- Yanlış Pozitif Analizi ---")

    # Confusion Matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    print(f"\nConfusion Matrix:")
    print(f"  True Negatives (TN):  {tn:3d} | Doğru Normal Tespiti")
    print(f"  False Positives (FP): {fp:3d} | YANLIŞ ALARM ⚠")
    print(f"  False Negatives (FN): {fn:3d} | Kaçırılan Tehdit ⚠⚠")
    print(f"  True Positives (TP):  {tp:3d} | Doğru Tehdit Tespiti")

    # Metrikler
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn)

    print(f"\n📊 Performans Metrikleri:")
    print(f"  False Positive Rate: {fpr:.2%} (Ne kadar düşükse o kadar iyi)")
    print(f"  False Negative Rate: {fnr:.2%} (Ne kadar düşükse o kadar iyi)")
    print(f"  Precision (Kesinlik): {precision:.2%}")
    print(f"  Recall (Duyarlılık):  {recall:.2%}")
    print(f"  Accuracy (Doğruluk):  {accuracy:.2%}")

    # Classification Report
    print(f"\n📋 Detaylı Rapor:")
    print(classification_report(y_true, y_pred, target_names=['Normal', 'Threat'], zero_division=0))

    return tn, fp, fn, tp

def visualize_confusion_matrix(y_true, y_pred):
    """
    Confusion matrix'i görselleştirir.
    """
    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Normal', 'Threat'],
                yticklabels=['Normal', 'Threat'])
    plt.title('Confusion Matrix - False Positive Analysis')
    plt.ylabel('Gerçek Durum')
    plt.xlabel('Tahmin Edilen Durum')
    plt.tight_layout()

    # Kaydet
    plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Grafik kaydedildi: confusion_matrix.png")
    plt.close()

def run_false_positive_simulation(num_events=100, visualize=True):
    """
    Yanlış pozitif simülasyonunu çalıştırır.
    """
    print("\n" + "="*60)
    print("     YANLIŞ ANOMALİ (FALSE POSITIVE) SİMÜLASYONU")
    print("="*60)

    print(f"\n🔍 {num_events} olay simüle ediliyor...")

    # Senaryo oluştur
    y_true, y_pred = generate_detection_scenario(num_events=num_events)

    # Analiz et
    analyze_false_positives(y_true, y_pred)

    # Görselleştir
    if visualize:
        try:
            visualize_confusion_matrix(y_true, y_pred)
        except Exception as e:
            print(f"⚠ Görselleştirme hatası: {e}")

    print("\n💡 Not: False Positive (Yanlış Alarm), normal bir olayın")
    print("   yanlışlıkla tehdit olarak algılanmasıdır.")
    print("   Bu durum gereksiz incelemelere ve kaynak israfına yol açar.")

    print("\n" + "="*60)

    return y_true, y_pred

if __name__ == "__main__":
    run_false_positive_simulation()
