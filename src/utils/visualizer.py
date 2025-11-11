"""
Visualizer Module
Veri gÃ¶rselleÅŸtirme modÃ¼lÃ¼
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
import json


class ChargingVisualizer:
    """
    Åarj simÃ¼lasyonu gÃ¶rselleÅŸtirici
    GerÃ§ek zamanlÄ± grafik gÃ¶sterimi
    """
    
    def __init__(self, title: str = "EV Charging Simulation"):
        """
        Args:
            title: Grafik baÅŸlÄ±ÄŸÄ±
        """
        self.title = title
        
        # Veri listeleri
        self.time_data = []
        self.soc_real_data = []
        self.soc_fake_data = []
        self.temp_data = []
        self.voltage_data = []
        self.current_data = []
        
        # EÅŸikler
        self.soc_threshold = 95.0
        self.temp_threshold = 45.0
        
        # FigÃ¼r
        self.fig = None
        self.axes = None
        
    def add_data_point(self, time_point: float, soc_real: float, 
                      soc_fake: Optional[float] = None,
                      temperature: Optional[float] = None,
                      voltage: Optional[float] = None,
                      current: Optional[float] = None):
        """
        Veri noktasÄ± ekle
        
        Args:
            time_point: Zaman (saniye)
            soc_real: GerÃ§ek SOC
            soc_fake: Sahte SOC (manipÃ¼lasyon varsa)
            temperature: SÄ±caklÄ±k
            voltage: Voltaj
            current: AkÄ±m
        """
        self.time_data.append(time_point)
        self.soc_real_data.append(soc_real)
        self.soc_fake_data.append(soc_fake if soc_fake is not None else soc_real)
        
        if temperature is not None:
            self.temp_data.append(temperature)
        if voltage is not None:
            self.voltage_data.append(voltage)
        if current is not None:
            self.current_data.append(current)
    
    def plot_static(self, save_path: Optional[str] = None):
        """
        Statik grafik oluÅŸtur
        
        Args:
            save_path: Kaydedilecek dosya yolu
        """
        self.fig, self.axes = plt.subplots(2, 2, figsize=(15, 10))
        self.fig.suptitle(self.title, fontsize=16, fontweight='bold')
        
        # SOC grafiÄŸi
        ax1 = self.axes[0, 0]
        ax1.plot(self.time_data, self.soc_real_data, 'g-', linewidth=2, label='Real SOC')
        if any(r != f for r, f in zip(self.soc_real_data, self.soc_fake_data)):
            ax1.plot(self.time_data, self.soc_fake_data, 'r--', linewidth=2, label='Fake SOC (Attack)')
        ax1.axhline(y=self.soc_threshold, color='orange', linestyle=':', label='SOC Threshold')
        ax1.axhline(y=100, color='red', linestyle='--', label='Overcharge')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('SOC (%)')
        ax1.set_title('State of Charge')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([0, 110])
        
        # SÄ±caklÄ±k grafiÄŸi
        if self.temp_data:
            ax2 = self.axes[0, 1]
            ax2.plot(self.time_data[:len(self.temp_data)], self.temp_data, 'b-', linewidth=2)
            ax2.axhline(y=self.temp_threshold, color='orange', linestyle=':', label='Safe Limit')
            ax2.axhline(y=60, color='red', linestyle='--', label='Critical')
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Temperature (Â°C)')
            ax2.set_title('Battery Temperature')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Tehlikeli bÃ¶lgeyi vurgula
            if any(t > self.temp_threshold for t in self.temp_data):
                ax2.fill_between(
                    self.time_data[:len(self.temp_data)],
                    self.temp_threshold,
                    [max(t, self.temp_threshold) for t in self.temp_data],
                    where=[t > self.temp_threshold for t in self.temp_data],
                    alpha=0.3,
                    color='red',
                    label='Danger Zone'
                )
        
        # Voltaj grafiÄŸi
        if self.voltage_data:
            ax3 = self.axes[1, 0]
            ax3.plot(self.time_data[:len(self.voltage_data)], self.voltage_data, 'm-', linewidth=2)
            ax3.set_xlabel('Time (s)')
            ax3.set_ylabel('Voltage (V)')
            ax3.set_title('Battery Voltage')
            ax3.grid(True, alpha=0.3)
        
        # AkÄ±m grafiÄŸi
        if self.current_data:
            ax4 = self.axes[1, 1]
            ax4.plot(self.time_data[:len(self.current_data)], self.current_data, 'c-', linewidth=2)
            ax4.set_xlabel('Time (s)')
            ax4.set_ylabel('Current (A)')
            ax4.set_title('Charging Current')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\nğŸ“Š Visualization saved to: {save_path}")
        
        plt.show()
    
    def plot_comparison(self, vulnerable_data: Dict, secure_data: Dict, 
                       save_path: Optional[str] = None):
        """
        Zafiyet vs GÃ¼venli sistem karÅŸÄ±laÅŸtÄ±rmasÄ±
        
        Args:
            vulnerable_data: ZayÄ±f sistem verileri
            secure_data: GÃ¼venli sistem verileri
            save_path: Kaydedilecek dosya yolu
        """
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Vulnerable vs Secure System Comparison', fontsize=16, fontweight='bold')
        
        # Zafiyet durumu
        ax1 = axes[0]
        time_v = vulnerable_data['time']
        soc_real_v = vulnerable_data['soc_real']
        soc_fake_v = vulnerable_data['soc_fake']
        
        ax1.plot(time_v, soc_real_v, 'g-', linewidth=2, label='Real SOC')
        ax1.plot(time_v, soc_fake_v, 'r--', linewidth=2, label='Reported SOC (Manipulated)')
        ax1.axhline(y=95, color='orange', linestyle=':', label='Safe Limit')
        ax1.axhline(y=100, color='red', linestyle='--', label='Overcharge')
        ax1.fill_between(time_v, 100, 110, alpha=0.2, color='red', label='Danger Zone')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('SOC (%)')
        ax1.set_title('âš ï¸ VULNERABLE SYSTEM\n(No Security Checks)', color='red')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([0, 110])
        
        # GÃ¼venli durum
        ax2 = axes[1]
        time_s = secure_data['time']
        soc_s = secure_data['soc']
        
        ax2.plot(time_s, soc_s, 'g-', linewidth=2, label='SOC')
        ax2.axhline(y=95, color='orange', linestyle=':', label='Safe Limit')
        ax2.axhline(y=100, color='green', linestyle='--', label='Max')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('SOC (%)')
        ax2.set_title('âœ… SECURE SYSTEM\n(Cryptographic Validation)', color='green')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([0, 110])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\nğŸ“Š Comparison saved to: {save_path}")
        
        plt.show()
    
    def plot_attack_timeline(self, events: List[Dict], save_path: Optional[str] = None):
        """
        SaldÄ±rÄ± zaman Ã§izelgesi
        
        Args:
            events: Olay listesi
            save_path: Kaydedilecek dosya yolu
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # Olay tiplerini renklendir
        event_colors = {
            "NORMAL": "green",
            "ATTACK_START": "orange",
            "MANIPULATION": "red",
            "DETECTION": "blue",
            "EMERGENCY_STOP": "purple"
        }
        
        y_pos = 0
        for event in events:
            time = event['time']
            event_type = event['type']
            description = event['description']
            
            color = event_colors.get(event_type, "gray")
            
            ax.scatter(time, y_pos, c=color, s=200, zorder=3)
            ax.text(time, y_pos + 0.3, description, fontsize=9, ha='center')
            
            y_pos += 1
        
        ax.set_xlabel('Time (s)', fontsize=12)
        ax.set_title('Attack Timeline', fontsize=16, fontweight='bold')
        ax.set_ylim([-1, y_pos])
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_yticks([])
        
        # Legend
        handles = [plt.Line2D([0], [0], marker='o', color='w', 
                             markerfacecolor=color, markersize=10, label=event_type)
                  for event_type, color in event_colors.items()]
        ax.legend(handles=handles, loc='upper right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\nğŸ“Š Attack timeline saved to: {save_path}")
        
        plt.show()
    
    def clear_data(self):
        """Veriyi temizle"""
        self.time_data.clear()
        self.soc_real_data.clear()
        self.soc_fake_data.clear()
        self.temp_data.clear()
        self.voltage_data.clear()
        self.current_data.clear()


if __name__ == "__main__":
    print("=== Visualizer Test ===\n")
    
    # Test verisi oluÅŸtur
    visualizer = ChargingVisualizer("Attack Simulation Test")
    
    # Normal ÅŸarj simÃ¼lasyonu
    for t in range(0, 30):
        soc_real = 30 + (t * 2.0)  # GerÃ§ek SOC artÄ±yor
        soc_fake = 30.0  # Sahte SOC sabit (manipÃ¼lasyon)
        temp = 25 + (t * 0.8)  # SÄ±caklÄ±k artÄ±yor
        voltage = 320 + (t * 2.0)
        current = 150.0
        
        visualizer.add_data_point(t, soc_real, soc_fake, temp, voltage, current)
    
    # t=30'da aÅŸÄ±rÄ± ÅŸarj baÅŸlÄ±yor
    for t in range(30, 40):
        soc_real = 90 + ((t - 30) * 2.0)  # 100'Ã¼ geÃ§iyor!
        soc_fake = 30.0  # Hala dÃ¼ÅŸÃ¼k gÃ¶steriliyor
        temp = 49 + ((t - 30) * 1.5)  # SÄ±caklÄ±k kritik seviyelere
        voltage = 380 + ((t - 30) * 2.0)
        current = 150.0
        
        visualizer.add_data_point(t, soc_real, soc_fake, temp, voltage, current)
    
    print("Generating visualization...")
    visualizer.plot_static(save_path="logs/attack_simulation.png")
    
    print("\n\nGenerating comparison...")
    
    # KarÅŸÄ±laÅŸtÄ±rma verisi
    vulnerable_data = {
        'time': list(range(40)),
        'soc_real': visualizer.soc_real_data,
        'soc_fake': visualizer.soc_fake_data
    }
    
    secure_data = {
        'time': list(range(30)),
        'soc': [30 + (t * 2.0) for t in range(30)]  # GÃ¼venli sistemde 95'te durur
    }
    
    vis2 = ChargingVisualizer()
    vis2.plot_comparison(vulnerable_data, secure_data, save_path="logs/comparison.png")
