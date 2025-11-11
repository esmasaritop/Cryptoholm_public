#!/bin/bash
# CypherCar Başlatma Scripti

echo "🚗 CypherCar başlatılıyor..."

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment oluşturuluyor..."
    python3 -m venv venv
fi

# Virtual environment'ı aktifleştir
source venv/bin/activate

# Gerekli paketleri yükle
echo "📦 Gerekli paketler kontrol ediliyor..."
pip install -q -r requirements.txt

# Ana programı çalıştır
echo ""
python3 main.py

# Virtual environment'tan çık
deactivate

