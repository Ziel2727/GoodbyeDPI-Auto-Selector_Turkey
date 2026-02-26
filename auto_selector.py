#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║          GoodbyeDPI - Otomatik Konfigürasyon Seçici             ║
║                                                                  ║
║  Bu script internet bağlantınızı analiz eder, tüm GoodbyeDPI    ║
║  konfigürasyonlarını sırasıyla dener ve çalışan konfigürasyonu   ║
║  otomatik olarak Windows servisi olarak kurar.                   ║
║                                                                  ║
║  Kullanım: Yönetici olarak çalıştırın!                           ║
║  python auto_selector.py                                         ║
╚══════════════════════════════════════════════════════════════════╝
"""

import subprocess
import socket
import ssl
import sys
import os
import time
import ctypes
import platform
import urllib.request
import json
import signal
from pathlib import Path
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# RENK KODLARI (Windows Terminal)
# ═══════════════════════════════════════════════════════════════
class Colors:
    """ANSI renk kodları - modern terminal çıktısı için."""
    HEADER    = "\033[95m"
    BLUE      = "\033[94m"
    CYAN      = "\033[96m"
    GREEN     = "\033[92m"
    YELLOW    = "\033[93m"
    RED       = "\033[91m"
    BOLD      = "\033[1m"
    DIM       = "\033[2m"
    UNDERLINE = "\033[4m"
    RESET     = "\033[0m"
    WHITE     = "\033[97m"
    MAGENTA   = "\033[35m"
    BG_GREEN  = "\033[42m"
    BG_RED    = "\033[41m"
    BG_YELLOW = "\033[43m"
    BG_BLUE   = "\033[44m"


def enable_ansi_colors():
    """Windows terminalinde ANSI renk desteğini etkinleştirir."""
    if os.name == 'nt':
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


# ═══════════════════════════════════════════════════════════════
# UI HELPER FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════
def print_banner():
    """Ana başlık banner'ı yazdırır."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   ██████╗  ██████╗  ██████╗ ██████╗ ██████╗ ██╗   ██╗███████╗║
    ║  ██╔════╝ ██╔═══██╗██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝║
    ║  ██║  ███╗██║   ██║██║   ██║██║  ██║██████╔╝ ╚████╔╝ █████╗  ║
    ║  ██║   ██║██║   ██║██║   ██║██║  ██║██╔══██╗  ╚██╔╝  ██╔══╝  ║
    ║  ╚██████╔╝╚██████╔╝╚██████╔╝██████╔╝██████╔╝   ██║   ███████╗║
    ║   ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚══════╝║
    ║           DPI  -  Otomatik Konfigürasyon Seçici              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)


def print_section(title, icon="═"):
    """Bölüm başlığı yazdırır."""
    line = icon * 50
    print(f"\n{Colors.BLUE}{Colors.BOLD}  ┌{'─' * 56}┐{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}  │  {title:^52} │{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}  └{'─' * 56}┘{Colors.RESET}")


def print_status(icon, message, color=Colors.WHITE):
    """Durum mesajı yazdırır."""
    print(f"  {color}{icon} {message}{Colors.RESET}")


def print_success(message):
    print_status("✅", message, Colors.GREEN)


def print_error(message):
    print_status("❌", message, Colors.RED)


def print_warning(message):
    print_status("⚠️ ", message, Colors.YELLOW)


def print_info(message):
    print_status("ℹ️ ", message, Colors.CYAN)


def print_progress(current, total, message):
    """İlerleme çubuğu yazdırır."""
    bar_length = 30
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)
    percentage = int(100 * current / total)
    print(f"\r  {Colors.CYAN}[{bar}] {percentage}% - {message}{Colors.RESET}", end="", flush=True)


def print_config_card(index, name, args, status="Bekleniyor", status_color=Colors.DIM):
    """Konfigürasyon kartı yazdırır."""
    print(f"  {Colors.WHITE}┌{'─' * 54}┐{Colors.RESET}")
    print(f"  {Colors.WHITE}│ {Colors.BOLD}#{index}{Colors.RESET}{Colors.WHITE}  {name:<48} │{Colors.RESET}")
    print(f"  {Colors.WHITE}│ {Colors.DIM}Argümanlar: {args:<40}{Colors.RESET}{Colors.WHITE} │{Colors.RESET}")
    print(f"  {Colors.WHITE}│ {status_color}Durum: {status:<45}{Colors.RESET}{Colors.WHITE} │{Colors.RESET}")
    print(f"  {Colors.WHITE}└{'─' * 54}┘{Colors.RESET}")


# ═══════════════════════════════════════════════════════════════
# KONFİGÜRASYON TANIMLARI
# ═══════════════════════════════════════════════════════════════

# ─── Test edilecek site ───
# Sadece Discord üzerinden hızlı test yapılır
TEST_SITE = "discord.com"

# Bağlantı kontrolü - her zaman erişilebilir olması gereken siteler
BASELINE_SITES = [
    "www.google.com",
    "www.microsoft.com",
]

# Tüm GoodbyeDPI konfigürasyonları - sırasıyla denenecek
CONFIGS = [
    {
        "name": "Ana Metod (TTL 5 + DNS Yandex)",
        "args": "-5 --set-ttl 5 --dns-addr 77.88.8.8 --dns-port 1253 --dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253",
        "needs_manual_dns": False,
        "description": "Tam kapsamlı DPI bypass + Yandex DNS yönlendirmesi",
        "priority": 1,
    },
    {
        "name": "Alternatif 3 (TTL 3 + DNS Yandex)",
        "args": "--set-ttl 3 --dns-addr 77.88.8.8 --dns-port 1253 --dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253",
        "needs_manual_dns": False,
        "description": "Düşük TTL + Yandex DNS yönlendirmesi",
        "priority": 2,
    },
    {
        "name": "Alternatif 4 (Mod -5 + DNS Yandex)",
        "args": "-5 --dns-addr 77.88.8.8 --dns-port 1253 --dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253",
        "needs_manual_dns": False,
        "description": "DPI bypass mod 5 + Yandex DNS yönlendirmesi",
        "priority": 3,
    },
    {
        "name": "Alternatif 5 (Mod -9 + DNS Yandex)",
        "args": "-9 --dns-addr 77.88.8.8 --dns-port 1253 --dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253",
        "needs_manual_dns": False,
        "description": "DPI bypass mod 9 + Yandex DNS yönlendirmesi",
        "priority": 4,
    },
    {
        "name": "Alternatif (TTL 3 - DNS'siz)",
        "args": "--set-ttl 3",
        "needs_manual_dns": True,
        "description": "Sadece TTL ayarı - Manuel DNS gerekli",
        "priority": 5,
    },
    {
        "name": "Alternatif 2 (Mod -5 - DNS'siz)",
        "args": "-5",
        "needs_manual_dns": True,
        "description": "DPI bypass mod 5 - Manuel DNS gerekli",
        "priority": 6,
    },
    {
        "name": "Alternatif 6 (Mod -9 - DNS'siz)",
        "args": "-9",
        "needs_manual_dns": True,
        "description": "DPI bypass mod 9 - Manuel DNS gerekli",
        "priority": 7,
    },
]

# Timeout ayarları (saniye) - Hız için düşük tutuldu
CONNECTION_TIMEOUT = 4
PROCESS_STARTUP_WAIT = 2
SITE_TEST_TIMEOUT = 5


# ═══════════════════════════════════════════════════════════════
# SİSTEM KONTROL FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════

def is_admin():
    """Yönetici yetkisi kontrolü yapar."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """Scripti yönetici olarak yeniden başlatır."""
    if not is_admin():
        print_warning("Yönetici yetkisi gerekiyor! Yeniden başlatılıyor...")
        try:
            # Python'un exe yolunu al
            python_exe = sys.executable
            script_path = os.path.abspath(__file__)
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", python_exe, f'"{script_path}"', None, 1
            )
            sys.exit(0)
        except Exception as e:
            print_error(f"Yönetici olarak başlatılamadı: {e}")
            print_info("Lütfen bu scripti 'Yönetici olarak çalıştır' ile açın.")
            sys.exit(1)


def get_script_dir():
    """Script dizinini döndürür."""
    return Path(os.path.dirname(os.path.abspath(__file__)))


def get_arch():
    """Sistem mimarisini tespit eder."""
    if platform.machine().endswith('64') or os.environ.get('PROCESSOR_ARCHITECTURE') == 'AMD64':
        return "x86_64"
    return "x86"


def get_goodbyedpi_path():
    """GoodbyeDPI exe yolunu döndürür."""
    script_dir = get_script_dir()
    arch = get_arch()
    exe_path = script_dir / arch / "goodbyedpi.exe"
    return exe_path


# ═══════════════════════════════════════════════════════════════
# AĞ ANALİZ FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════

def check_basic_connectivity():
    """Temel internet bağlantısını kontrol eder."""
    print_info("Temel internet bağlantısı kontrol ediliyor...")
    for site in BASELINE_SITES:
        try:
            socket.create_connection((site, 443), timeout=5)
            print_success(f"{site} - Erişilebilir")
            return True
        except (socket.timeout, socket.error, OSError):
            print_warning(f"{site} - Erişilemiyor")
            continue
    return False


def get_isp_info():
    """ISP bilgilerini tespit eder."""
    print_info("ISP bilgileri tespit ediliyor...")
    try:
        req = urllib.request.Request(
            "http://ip-api.com/json/?fields=status,isp,org,as,query",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "success":
                return {
                    "ip": data.get("query", "Bilinmiyor"),
                    "isp": data.get("isp", "Bilinmiyor"),
                    "org": data.get("org", "Bilinmiyor"),
                    "asn": data.get("as", "Bilinmiyor"),
                }
    except Exception:
        pass
    return {"ip": "Tespit edilemedi", "isp": "Tespit edilemedi", "org": "-", "asn": "-"}


def detect_current_dns():
    """Mevcut DNS sunucusunu tespit eder."""
    try:
        result = subprocess.run(
            ["nslookup", "google.com"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Address' in line and 'Addresses' not in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    dns = parts[1].strip()
                    if dns and not dns.startswith('142.') and not dns.startswith('172.'):
                        return dns
    except Exception:
        pass
    return "Tespit edilemedi"


def test_blocked_site(hostname, timeout=CONNECTION_TIMEOUT):
    """Yasaklı bir siteye HTTPS bağlantısı test eder.
    
    Gerçek bir TLS handshake yaparak sitenin erişilebilir olup olmadığını kontrol eder.
    DPI tarafından engellenmiş sitelerde TLS handshake başarısız olur.
    """
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # TLS handshake başarılı - site erişilebilir
                return True
    except (socket.timeout, socket.error, ssl.SSLError, OSError, ConnectionResetError):
        return False


def test_blocked_site_http(hostname, timeout=CONNECTION_TIMEOUT):
    """HTTP GET isteği ile site erişimini kontrol eder (yedek yöntem)."""
    try:
        req = urllib.request.Request(
            f"https://{hostname}/",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status in (200, 301, 302, 303, 307, 308)
    except Exception:
        return False


def quick_test_discord():
    """Discord'a hızlı TLS bağlantı testi yapar. True/False döner."""
    # Yöntem 1: TLS handshake (en hızlı)
    if test_blocked_site(TEST_SITE, CONNECTION_TIMEOUT):
        return True
    # Yöntem 2: HTTP GET (yedek)
    if test_blocked_site_http(TEST_SITE, CONNECTION_TIMEOUT):
        return True
    return False


# ═══════════════════════════════════════════════════════════════
# GOODBYEDPI PROCESS YÖNETİMİ
# ═══════════════════════════════════════════════════════════════

def stop_existing_goodbyedpi():
    """Çalışan tüm GoodbyeDPI process'lerini ve servislerini durdurur."""
    # Servisi durdur
    try:
        subprocess.run(
            ["sc", "stop", "GoodbyeDPI"],
            capture_output=True, timeout=10
        )
    except Exception:
        pass
    
    # Process'leri öldür
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "goodbyedpi.exe"],
            capture_output=True, timeout=10
        )
    except Exception:
        pass
    
    time.sleep(1)  # Process'lerin kapanmasını bekle


def start_goodbyedpi_test(config):
    """Test amaçlı GoodbyeDPI'yi belirtilen konfigürasyon ile başlatır."""
    exe_path = get_goodbyedpi_path()
    
    if not exe_path.exists():
        print_error(f"goodbyedpi.exe bulunamadı: {exe_path}")
        return None
    
    args = config["args"].split()
    cmd = [str(exe_path)] + args
    
    try:
        # Arka planda başlat
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Process'in başlamasını bekle
        time.sleep(PROCESS_STARTUP_WAIT)
        
        # Process hala çalışıyor mu kontrol et
        if process.poll() is not None:
            # Process kapandı - hata var
            stderr_output = process.stderr.read().decode('utf-8', errors='ignore')
            print_error(f"GoodbyeDPI başlatılamadı: {stderr_output[:200]}")
            return None
        
        return process
    except Exception as e:
        print_error(f"GoodbyeDPI başlatma hatası: {e}")
        return None


def stop_goodbyedpi_test(process):
    """Test process'ini sonlandırır."""
    if process and process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=5)
        except Exception:
            try:
                process.kill()
                process.wait(timeout=3)
            except Exception:
                pass
    
    # Temizlik - kalan process'leri de öldür
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "goodbyedpi.exe"],
            capture_output=True, timeout=5
        )
    except Exception:
        pass
    
    time.sleep(1)


# ═══════════════════════════════════════════════════════════════
# SERVİS KURULUM FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════

def install_service(config):
    """Çalışan konfigürasyonu Windows servisi olarak kurar."""
    exe_path = get_goodbyedpi_path()
    args = config["args"]
    
    print_section("🔧 Servis Kurulumu")
    
    # Mevcut servisi durdur ve sil
    print_info("Eski servis kaldırılıyor...")
    subprocess.run(["sc", "stop", "GoodbyeDPI"], capture_output=True, timeout=10)
    time.sleep(1)
    subprocess.run(["sc", "delete", "GoodbyeDPI"], capture_output=True, timeout=10)
    time.sleep(1)
    
    # Yeni servisi oluştur
    bin_path = f'"{exe_path}" {args}'
    
    result = subprocess.run(
        [
            "sc", "create", "GoodbyeDPI",
            f"binPath=", bin_path,
            "start=", "auto"
        ],
        capture_output=True, text=True, timeout=15
    )
    
    if result.returncode != 0:
        print_error(f"Servis oluşturulamadı: {result.stderr}")
        return False
    
    print_success("Servis oluşturuldu")
    
    # Açıklama ekle
    subprocess.run(
        [
            "sc", "description", "GoodbyeDPI",
            f"Turkiye icin DPI bypass - {config['name']} - Otomatik tespit edildi"
        ],
        capture_output=True, timeout=10
    )
    
    # Servisi başlat
    result = subprocess.run(
        ["sc", "start", "GoodbyeDPI"],
        capture_output=True, text=True, timeout=15
    )
    
    if result.returncode != 0:
        print_warning(f"Servis başlatma uyarısı: {result.stderr}")
    else:
        print_success("Servis başarıyla başlatıldı!")
    
    return True


def save_result_log(config, isp_info):
    """Sonuçları log dosyasına kaydeder."""
    log_path = get_script_dir() / "auto_selector_log.txt"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n{'=' * 60}\n")
        f.write(f"Tarih: {timestamp}\n")
        f.write(f"ISP: {isp_info.get('isp', 'Bilinmiyor')}\n")
        f.write(f"IP: {isp_info.get('ip', 'Bilinmiyor')}\n")
        f.write(f"ASN: {isp_info.get('asn', 'Bilinmiyor')}\n")
        f.write(f"Mimari: {get_arch()}\n")
        f.write(f"\nSeçilen Konfigürasyon: {config['name']}\n")
        f.write(f"Argümanlar: {config['args']}\n")
        f.write(f"Manuel DNS Gerekli: {'Evet' if config['needs_manual_dns'] else 'Hayır'}\n")
        f.write(f"\nTest: {TEST_SITE} -> Erişilebilir ✓\n")
        f.write(f"{'=' * 60}\n")
    
    print_info(f"Sonuçlar kaydedildi: {log_path}")


# ═══════════════════════════════════════════════════════════════
# ANA ÇALIŞMA AKIŞI
# ═══════════════════════════════════════════════════════════════

def main():
    """Ana çalışma fonksiyonu."""
    enable_ansi_colors()
    print_banner()
    
    # ─── Yönetici Kontrolü ───
    if not is_admin():
        print_error("Bu script yönetici yetkisi ile çalıştırılmalıdır!")
        print_info("Yönetici olarak yeniden başlatmayı deniyorum...")
        run_as_admin()
        return
    
    print_success("Yönetici yetkisi mevcut")
    
    # ─── GoodbyeDPI Exe Kontrolü ───
    exe_path = get_goodbyedpi_path()
    if not exe_path.exists():
        print_error(f"goodbyedpi.exe bulunamadı!")
        print_error(f"Beklenen konum: {exe_path}")
        input("\nÇıkmak için Enter'a basın...")
        sys.exit(1)
    
    print_success(f"GoodbyeDPI bulundu: {exe_path}")
    print_info(f"Mimari: {get_arch()}")
    
    # ─── Ağ Analizi ───
    print_section("📡 Ağ Analizi")
    
    # Temel bağlantı kontrolü
    if not check_basic_connectivity():
        print_error("İnternet bağlantısı yok! Lütfen bağlantınızı kontrol edin.")
        input("\nÇıkmak için Enter'a basın...")
        sys.exit(1)
    
    # ISP bilgileri
    isp_info = get_isp_info()
    print()
    print(f"  {Colors.WHITE}┌{'─' * 50}┐{Colors.RESET}")
    print(f"  {Colors.WHITE}│ {Colors.BOLD}📋 Ağ Bilgileri{Colors.RESET}{Colors.WHITE}{' ' * 34}│{Colors.RESET}")
    print(f"  {Colors.WHITE}├{'─' * 50}┤{Colors.RESET}")
    print(f"  {Colors.WHITE}│  IP Adresi : {Colors.CYAN}{isp_info['ip']:<35}{Colors.WHITE}│{Colors.RESET}")
    print(f"  {Colors.WHITE}│  ISP       : {Colors.CYAN}{isp_info['isp'][:35]:<35}{Colors.WHITE}│{Colors.RESET}")
    print(f"  {Colors.WHITE}│  ASN       : {Colors.CYAN}{isp_info['asn'][:35]:<35}{Colors.WHITE}│{Colors.RESET}")
    print(f"  {Colors.WHITE}└{'─' * 50}┘{Colors.RESET}")
    
    # DNS bilgisi
    current_dns = detect_current_dns()
    print_info(f"Mevcut DNS: {current_dns}")
    
    # ─── GoodbyeDPI Olmadan Ön Test ───
    print_section("🔍 Ön Test (GoodbyeDPI Kapalı)")
    print_info(f"Discord ({TEST_SITE}) erişim testi yapılıyor...")
    
    # Önce çalışan GoodbyeDPI varsa durdur
    stop_existing_goodbyedpi()
    time.sleep(1)
    
    if quick_test_discord():
        print_success(f"{TEST_SITE} zaten erişilebilir! GoodbyeDPI'ye gerek yok.")
        input("\nÇıkmak için Enter'a basın...")
        sys.exit(0)
    else:
        print_error(f"{TEST_SITE} engelli. GoodbyeDPI konfigürasyonları denenecek...")
    
    # ─── Konfigürasyon Taraması ───
    print_section("🚀 Konfigürasyon Taraması")
    
    # Önce DNS yönlendirmesi olan konfigürasyonları dene (daha güvenli)
    # Sonra sadece DPI bypass olanları dene
    dns_configs = [c for c in CONFIGS if not c["needs_manual_dns"]]
    no_dns_configs = [c for c in CONFIGS if c["needs_manual_dns"]]
    ordered_configs = dns_configs + no_dns_configs
    
    total_configs = len(ordered_configs)
    working_config = None
    
    for i, config in enumerate(ordered_configs):
        config_num = i + 1
        print()
        print(f"  {Colors.YELLOW}{'━' * 56}{Colors.RESET}")
        print(f"  {Colors.BOLD}{Colors.YELLOW}  [{config_num}/{total_configs}] {config['name']}{Colors.RESET}")
        print(f"  {Colors.DIM}  {config['description']}{Colors.RESET}")
        if config["needs_manual_dns"]:
            print(f"  {Colors.YELLOW}  ⚠️  Manuel DNS gerektirir{Colors.RESET}")
        print(f"  {Colors.YELLOW}{'━' * 56}{Colors.RESET}")
        
        # Mevcut GoodbyeDPI process'lerini temizle
        stop_existing_goodbyedpi()
        
        # GoodbyeDPI'yi başlat
        print_info("GoodbyeDPI başlatılıyor...")
        process = start_goodbyedpi_test(config)
        
        if process is None:
            print_error("Başlatılamadı, sonraki deneniyor...")
            continue
        
        # Discord'u test et
        print_info(f"{TEST_SITE} test ediliyor...")
        discord_ok = quick_test_discord()
        
        # Process'i durdur
        stop_goodbyedpi_test(process)
        
        if discord_ok:
            print_success(f"{TEST_SITE} erişilebilir! ✓")
            print()
            print(f"  {Colors.GREEN}{Colors.BOLD}{'═' * 56}{Colors.RESET}")
            print(f"  {Colors.GREEN}{Colors.BOLD}  ✅ BAŞARILI! {config['name']}{Colors.RESET}")
            print(f"  {Colors.GREEN}{Colors.BOLD}{'═' * 56}{Colors.RESET}")
            working_config = config
            break
        else:
            print_error(f"{TEST_SITE} hala engelli ✗ → Sonraki deneniyor...")
    
    # ─── Sonuç ───
    if working_config is None:
        print_section("❌ Sonuç")
        print_error("Hiçbir konfigürasyon çalışmadı!")
        print()
        print_info("Öneriler:")
        print(f"  {Colors.WHITE}  1. İnternet bağlantınızı kontrol edin{Colors.RESET}")
        print(f"  {Colors.WHITE}  2. Farklı bir DNS sunucusu deneyin (1.1.1.1 veya 8.8.8.8){Colors.RESET}")
        print(f"  {Colors.WHITE}  3. VPN kullanmayı düşünün{Colors.RESET}")
        print(f"  {Colors.WHITE}  4. ISP'niz yeni bir engelleme yöntemi kullanıyor olabilir{Colors.RESET}")
        input("\nÇıkmak için Enter'a basın...")
        sys.exit(1)
    
    # Servis Kurulumu
    print_section("🎯 Sonuç & Servis Kurulumu")
    print()
    print(f"  {Colors.GREEN}{Colors.BOLD}╔{'═' * 54}╗{Colors.RESET}")
    print(f"  {Colors.GREEN}{Colors.BOLD}║  Çalışan Konfigürasyon Bulundu!{' ' * 22}║{Colors.RESET}")
    print(f"  {Colors.GREEN}{Colors.BOLD}╠{'═' * 54}╣{Colors.RESET}")
    print(f"  {Colors.GREEN}{Colors.BOLD}║  {working_config['name']:<52}║{Colors.RESET}")
    print(f"  {Colors.GREEN}{Colors.BOLD}╠{'═' * 54}╣{Colors.RESET}")
    args_display = working_config['args']
    if len(args_display) > 50:
        print(f"  {Colors.GREEN}{Colors.BOLD}║  Args: {args_display[:46]}...  ║{Colors.RESET}")
    else:
        print(f"  {Colors.GREEN}{Colors.BOLD}║  Args: {args_display:<46}║{Colors.RESET}")
    print(f"  {Colors.GREEN}{Colors.BOLD}╚{'═' * 54}╝{Colors.RESET}")
    
    if working_config["needs_manual_dns"]:
        print()
        print(f"  {Colors.YELLOW}{Colors.BOLD}╔{'═' * 54}╗{Colors.RESET}")
        print(f"  {Colors.YELLOW}{Colors.BOLD}║  ⚠️  ÖNEMLİ: Manuel DNS Ayarı Gereklidir!{' ' * 10}║{Colors.RESET}")
        print(f"  {Colors.YELLOW}{Colors.BOLD}╠{'═' * 54}╣{Colors.RESET}")
        print(f"  {Colors.YELLOW}{Colors.BOLD}║  Windows Ayarları > Ağ ve İnternet > Adaptör         ║{Colors.RESET}")
        print(f"  {Colors.YELLOW}{Colors.BOLD}║  Seçenekleri > IPv4 > DNS: 1.1.1.1 veya 8.8.8.8     ║{Colors.RESET}")
        print(f"  {Colors.YELLOW}{Colors.BOLD}║  Değişiklikten sonra bilgisayarı yeniden başlatın!   ║{Colors.RESET}")
        print(f"  {Colors.YELLOW}{Colors.BOLD}╚{'═' * 54}╝{Colors.RESET}")
    
    print()
    print_info("Servis olarak kurulsun mu?")
    print(f"  {Colors.WHITE}  [E] Evet - Windows servisi olarak kur (önerilen){Colors.RESET}")
    print(f"  {Colors.WHITE}  [H] Hayır - Sadece sonuçları kaydet{Colors.RESET}")
    print()
    
    choice = input(f"  {Colors.CYAN}Seçiminiz (E/H): {Colors.RESET}").strip().upper()
    
    if choice in ("E", "Y", "EVET", "YES", ""):
        # Mevcut process'leri temizle
        stop_existing_goodbyedpi()
        
        success = install_service(working_config)
        if success:
            print()
            print(f"  {Colors.GREEN}{Colors.BOLD}╔{'═' * 54}╗{Colors.RESET}")
            print(f"  {Colors.GREEN}{Colors.BOLD}║  🎉 Kurulum Tamamlandı!{' ' * 30}║{Colors.RESET}")
            print(f"  {Colors.GREEN}{Colors.BOLD}╠{'═' * 54}╣{Colors.RESET}")
            print(f"  {Colors.GREEN}{Colors.BOLD}║  GoodbyeDPI servisi otomatik çalışacak.{' ' * 13}║{Colors.RESET}")
            print(f"  {Colors.GREEN}{Colors.BOLD}║  Her bilgisayar açılışında otomatik başlar.{' ' * 9}║{Colors.RESET}")
            print(f"  {Colors.GREEN}{Colors.BOLD}║{' ' * 54}║{Colors.RESET}")
            print(f"  {Colors.GREEN}{Colors.BOLD}║  Kaldırmak için: service_remove.cmd{' ' * 18}║{Colors.RESET}")
            print(f"  {Colors.GREEN}{Colors.BOLD}╚{'═' * 54}╝{Colors.RESET}")
        else:
            print_error("Servis kurulumu başarısız oldu!")
            print_info("Manuel kurulum için uygun .cmd dosyasını kullanabilirsiniz.")
    else:
        print_info("Servis kurulmadı. Sonuçlar kaydediliyor...")
    
    # Log kaydet
    save_result_log(working_config, isp_info)
    
    print()
    print(f"  {Colors.DIM}{'─' * 56}{Colors.RESET}")
    print(f"  {Colors.DIM}  GoodbyeDPI Otomatik Seçici - Tamamlandı{Colors.RESET}")
    print(f"  {Colors.DIM}{'─' * 56}{Colors.RESET}")
    
    input("\nÇıkmak için Enter'a basın...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("İşlem kullanıcı tarafından iptal edildi.")
        # Temizlik
        stop_existing_goodbyedpi()
        sys.exit(0)
    except Exception as e:
        print()
        print_error(f"Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        input("\nÇıkmak için Enter'a basın...")
        sys.exit(1)
