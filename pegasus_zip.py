#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
                    🔥 ZIP-KRAKEN v2.0 - The Ultimate ZIP Cracker 🔥
              Professional Grade ZIP Password Recovery Tool
             堪比 John the Ripper - Akurat & Tepat untuk File ZIP
================================================================================
"""

import zipfile
import argparse
import os
import sys
import time
import threading
import queue
import itertools
import hashlib
import struct
import binascii
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Set, Dict, Tuple
import subprocess
import platform
import random
import re
import signal
import gc

# ==================== KONFIGURASI WARNA ====================
class Colors:
    """Warna untuk tampilan terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    WHITE = '\033[97m'
    BLACK = '\033[90m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    RESET = '\033[0m'
    
    @staticmethod
    def rgb(r, g, b):
        return f'\033[38;2;{r};{g};{b}m'

# ==================== KONFIGURASI GLOBAL ====================
VERSION = "2.0"
AUTHOR = "ZIP-KRAKEN Team"
BANNER = f"""
{Colors.MAGENTA}{Colors.BOLD}

 ██▓███  ▓█████   ▄████  ▄▄▄        ██████  █    ██   ██████    ▒███████▒ ██▓ ██▓███  
▓██░  ██▒▓█   ▀  ██▒ ▀█▒▒████▄    ▒██    ▒  ██  ▓██▒▒██    ▒    ▒ ▒ ▒ ▄▀░▓██▒▓██░  ██▒
▓██░ ██▓▒▒███   ▒██░▄▄▄░▒██  ▀█▄  ░ ▓██▄   ▓██  ▒██░░ ▓██▄      ░ ▒ ▄▀▒░ ▒██▒▓██░ ██▓▒
▒██▄█▓▒ ▒▒▓█  ▄ ░▓█  ██▓░██▄▄▄▄██   ▒   ██▒▓▓█  ░██░  ▒   ██▒     ▄▀▒   ░░██░▒██▄█▓▒ ▒
▒██▒ ░  ░░▒████▒░▒▓███▀▒ ▓█   ▓██▒▒██████▒▒▒▒█████▓ ▒██████▒▒   ▒███████▒░██░▒██▒ ░  ░
▒▓▒░ ░  ░░░ ▒░ ░ ░▒   ▒  ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░   ░▒▒ ▓░▒░▒░▓  ▒▓▒░ ░  ░
░▒ ░      ░ ░  ░  ░   ░   ▒   ▒▒ ░░ ░▒  ░ ░░░▒░ ░ ░ ░ ░▒  ░ ░   ░░▒ ▒ ░ ▒ ▒ ░░▒ ░     
░░          ░   ░ ░   ░   ░   ▒   ░  ░  ░   ░░░ ░ ░ ░  ░  ░     ░ ░ ░ ░ ░ ▒ ░░░       
            ░  ░      ░       ░  ░      ░     ░           ░       ░ ░     ░           
                                                                ░                     
{Colors.RESET}
"""

# ==================== KELAS UTAMA ====================
class ZIPKraken:
    """
    ZIP-KRAKEN - Professional ZIP Password Cracker
    Dengan kemampuan setara John the Ripper untuk file ZIP
    """
    
    def __init__(self):
        self.found_password = None
        self.lock = threading.Lock()
        self.attempts = 0
        self.start_time = None
        self.total_attempts = 0
        self.stop_flag = False
        self.pause_flag = False
        self.successful_method = None
        self.extracted_files = []
        self.current_mode = None
        self.session_file = "zipkraken.session"
        self.pot_file = "zipkraken.pot"  # File like John's pot file
        
        # Statistik
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_attempts': 0,
            'crack_speed': 0,
            'passwords_per_second': 0,
            'methods_tried': [],
            'crack_time': 0
        }
        
        # Load pot file (password yang sudah ditemukan sebelumnya)
        self.load_pot_file()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def load_pot_file(self):
        """Load password yang sudah ditemukan sebelumnya (like john.pot)"""
        self.cracked_passwords = set()
        if os.path.exists(self.pot_file):
            try:
                with open(self.pot_file, 'r') as f:
                    for line in f:
                        if ':' in line:
                            hash_val, pwd = line.strip().split(':', 1)
                            self.cracked_passwords.add(pwd)
            except:
                pass
    
    def save_to_pot(self, zip_path: str, password: str):
        """Simpan password yang berhasil ke pot file"""
        try:
            # Buat hash identifier sederhana
            file_hash = hashlib.md5(zip_path.encode()).hexdigest()[:8]
            with open(self.pot_file, 'a') as f:
                f.write(f"{file_hash}:{password}\n")
        except:
            pass
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C dengan graceful"""
        print(f"\n\n{Colors.YELLOW}{Colors.BOLD}⚠️  INTERRUPT DETECTED{Colors.RESET}")
        print(f"{Colors.CYAN}Menyimpan session...{Colors.RESET}")
        self.stop_flag = True
        self.save_session()
        self.print_stats()
        sys.exit(0)
    
    def save_session(self):
        """Simpan session untuk resume"""
        try:
            with open(self.session_file, 'w') as f:
                f.write(f"mode={self.current_mode}\n")
                f.write(f"attempts={self.attempts}\n")
                f.write(f"total={self.total_attempts}\n")
                f.write(f"time={time.time() - self.start_time if self.start_time else 0}\n")
        except:
            pass
    
    def cprint(self, text, color=Colors.WHITE, bold=False, end='\n'):
        """Print dengan warna"""
        if bold:
            print(f"{Colors.BOLD}{color}{text}{Colors.RESET}", end=end)
        else:
            print(f"{color}{text}{Colors.RESET}", end=end)
    
    def print_header(self, text, color=Colors.CYAN):
        """Print header dengan border"""
        print(f"\n{color}{Colors.BOLD}╔══ {text} ══╗{Colors.RESET}")
    
    def print_success(self, text):
        """Print success message"""
        print(f"{Colors.GREEN}{Colors.BOLD}✅ {text}{Colors.RESET}")
    
    def print_error(self, text):
        """Print error message"""
        print(f"{Colors.RED}{Colors.BOLD}❌ {text}{Colors.RESET}")
    
    def print_warning(self, text):
        """Print warning message"""
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  {text}{Colors.RESET}")
    
    def print_info(self, text):
        """Print info message"""
        print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")
    
    def print_progress(self, text):
        """Print progress message"""
        print(f"{Colors.BLUE}➤ {text}{Colors.RESET}")
    
    def print_stats(self):
        """Print statistik cracking"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            speed = self.attempts / elapsed if elapsed > 0 else 0
            
            print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
            print(f"{Colors.YELLOW}{Colors.BOLD}📊 CRACKING STATISTICS{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
            print(f"  Total attempts: {self.attempts:,}")
            print(f"  Time elapsed: {timedelta(seconds=int(elapsed))}")
            print(f"  Average speed: {speed:,.0f} passwords/second")
            print(f"  Mode: {self.current_mode or 'N/A'}")
            if self.found_password:
                print(f"{Colors.GREEN}  Password found: {self.found_password}{Colors.RESET}")
            print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
    
    # ==================== ZIP ANALYSIS ====================
    def analyze_zip(self, zip_path: str) -> Dict:
        """
        Analisis mendalam file ZIP seperti kemampuan John
        """
        analysis = {
            'filename': os.path.basename(zip_path),
            'path': zip_path,
            'size': os.path.getsize(zip_path) if os.path.exists(zip_path) else 0,
            'exists': os.path.exists(zip_path),
            'valid_zip': False,
            'encrypted': False,
            'encryption_type': 'Unknown',
            'compression_method': 'Unknown',
            'file_count': 0,
            'files': [],
            'password_protected': False,
            'hash_type': 'Unknown',
            'recoverable': True,
            'recommended_attack': 'Unknown',
            'estimated_crack_time': 'Unknown',
            'complexity': 'Unknown'
        }
        
        if not analysis['exists']:
            return analysis
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                analysis['valid_zip'] = True
                analysis['file_count'] = len(zf.namelist())
                analysis['files'] = zf.namelist()[:10]  # First 10 files
                
                # Deteksi enkripsi dan metode
                for file_info in zf.infolist():
                    if file_info.flag_bits & 0x1:
                        analysis['encrypted'] = True
                        analysis['password_protected'] = True
                        
                        # Deteksi tipe enkripsi
                        if file_info.flag_bits & 0x40:
                            analysis['encryption_type'] = 'AES-256'
                            analysis['hash_type'] = 'ZIP AES-256'
                        elif file_info.flag_bits & 0x800:
                            analysis['encryption_type'] = 'AES-128'
                            analysis['hash_type'] = 'ZIP AES-128'
                        else:
                            analysis['encryption_type'] = 'ZIP 2.0 (Legacy)'
                            analysis['hash_type'] = 'ZIP Classic'
                        
                        # Deteksi kompresi
                        if file_info.compress_type == 8:
                            analysis['compression_method'] = 'DEFLATED'
                        elif file_info.compress_type == 0:
                            analysis['compression_method'] = 'STORED'
                        
                        break
                
                # Rekomendasi attack berdasarkan analisis
                if analysis['encrypted']:
                    if analysis['encryption_type'] == 'ZIP 2.0 (Legacy)':
                        analysis['recommended_attack'] = 'Dictionary Attack (Fast)'
                        analysis['estimated_crack_time'] = 'Fast (seconds to minutes)'
                        analysis['complexity'] = 'Low'
                    elif 'AES' in analysis['encryption_type']:
                        analysis['recommended_attack'] = 'Dictionary + Brute Force'
                        analysis['estimated_crack_time'] = 'Slow (hours to days)'
                        analysis['complexity'] = 'High'
                        
        except RuntimeError as e:
            if 'encrypted' in str(e).lower():
                analysis['encrypted'] = True
                analysis['password_protected'] = True
                analysis['encryption_type'] = 'Password Protected'
                analysis['valid_zip'] = True
            else:
                analysis['recoverable'] = False
        except Exception:
            analysis['recoverable'] = False
        
        return analysis
    
    # ==================== PASSWORD GENERATION ====================
    def generate_indonesian_wordlist(self) -> List[str]:
        """
        Generate wordlist spesifik Indonesia (sangat lengkap)
        """
        words = set()
        
        # ===== KATA DASAR INDONESIA =====
        dasar = [
            'indonesia', 'jakarta', 'bandung', 'surabaya', 'medan', 'bali',
            'merdeka', 'pancasila', 'garuda', 'bhinneka', 'nusantara',
            'rakyat', 'bangsa', 'negara', 'tanahair', 'pertiwi',
            'satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan', 'sepuluh',
            'pulau', 'jawa', 'sumatra', 'kalimantan', 'sulawesi', 'papua',
            'maluku', 'flores', 'timor', 'sumba', 'komodo', 'rinjani',
            'bromo', 'merapi', 'semeru', 'agung', 'batur', 'ijien',
        ]
        words.update(dasar)
        
        # ===== NAMA PROVINSI =====
        provinsi = [
            'aceh', 'sumut', 'sumbar', 'riau', 'jambi', 'sumsel', 'bengkulu',
            'lampung', 'babel', 'kepri', 'jakarta', 'jabar', 'jateng', 'jogja',
            'jatim', 'banten', 'bali', 'ntb', 'ntt', 'kalbar', 'kalteng',
            'kalsel', 'kaltim', 'kalut', 'sulut', 'sulteng', 'sultra', 'sulsel',
            'gorontalo', 'sulbar', 'maluku', 'malut', 'papua', 'pabar', 'papeg',
        ]
        words.update(provinsi)
        
        # ===== NAMA KOTA =====
        kota = [
            'medan', 'padang', 'pekanbaru', 'jambi', 'palembang', 'pangkalpinang',
            'tanjungpinang', 'bandarlampung', 'jakarta', 'bandung', 'semarang',
            'yogyakarta', 'surabaya', 'serang', 'denpasar', 'mataram', 'kupang',
            'pontianak', 'palangkaraya', 'banjarmasin', 'samarinda', 'tarakan',
            'manado', 'palu', 'makassar', 'kendari', 'gorontalo', 'mamuju',
            'ambon', 'ternate', 'jayapura', 'manokwari', 'sorong',
        ]
        words.update(kota)
        
        # ===== NAMA ORANG INDONESIA =====
        nama = [
            # Nama laki-laki
            'agus', 'budi', 'cahyo', 'dwi', 'eko', 'fajar', 'gunawan', 'heru',
            'ibnu', 'joko', 'kurniawan', 'lukman', 'mulyono', 'nugroho', 'prasetyo',
            'rahmat', 'slamet', 'tri', 'utomo', 'wahyu', 'yulianto', 'zainal',
            
            # Nama perempuan
            'siti', 'dewi', 'ratna', 'sari', 'maya', 'rina', 'tuti', 'yanti',
            'wati', 'kurnia', 'lestari', 'pertiwi', 'utami', 'handayani',
            'susanti', 'wahyuni', 'setyawati', 'puspita', 'kartika',
            
            # Nama modern
            'kevin', 'michael', 'steven', 'jessica', 'angel', 'natasha',
            'wilson', 'hendra', 'sugianto', 'wijaya', 'halim', 'salim',
        ]
        words.update(nama)
        
        # ===== KATA SEHARI-HARI =====
        sehari = [
            'saya', 'kamu', 'dia', 'mereka', 'kita', 'kami',
            'makan', 'minum', 'tidur', 'mandi', 'kerja', 'main',
            'rumah', 'sekolah', 'kantor', 'pasar', 'mall', 'warung',
            'mobil', 'motor', 'sepeda', 'bus', 'angkot', 'becak',
            'hujan', 'panas', 'angin', 'mendung', 'cerah', 'petir',
            'senang', 'sedih', 'marah', 'cinta', 'benci', 'rindu',
            'pagi', 'siang', 'sore', 'malam', 'subuh', 'dzuhur',
        ]
        words.update(sehari)
        
        # ===== HEWAN DAN TUMBUHAN =====
        alam = [
            'harimau', 'gajah', 'badak', 'orangutan', 'komodo', 'rusa',
            'buaya', 'ular', 'kadal', 'bunglon', 'tokek', 'cicak',
            'elang', 'garuda', 'merpati', 'kenari', 'jalak', 'beo',
            'mawar', 'melati', 'anggrek', 'kenanga', 'cempaka', 'kamboja',
            'pohon', 'bambu', 'jati', 'mahoni', 'akasia', 'cemara',
        ]
        words.update(alam)
        
        # ===== MAKANAN KHAS =====
        makanan = [
            'nasi', 'goreng', 'rendang', 'sate', 'gado', 'soto', 'bakso',
            'mie', 'ayam', 'bakar', 'tahu', 'tempe', 'sambal', 'kecap',
            'rawon', 'nasipadang', 'nasiliwet', 'nasikuning', 'nasuduk',
            'satepadang', 'satebali', 'satemadura', 'sateayam', 'satekambing',
        ]
        words.update(makanan)
        
        # ===== TAHUN PENTING =====
        tahun = []
        for year in range(1945, 2026):
            tahun.append(str(year))
            tahun.append(str(year)[2:])  # 2 digit
        tahun.extend(['1945', '19450817', '17081945', '1998', '1999', '2000'])
        words.update(tahun)
        
        # ===== KOMBINASI UMUM =====
        kombinasi = []
        base_words = list(words)[:100]  # Ambil 100 kata pertama
        
        for word in base_words:
            kombinasi.extend([
                word + '123', word + '1234', word + '12345',
                word + '2023', word + '2024', word + '2025',
                word.upper(), word.capitalize(),
                word + '!', word + '@', word + '#', word + '$',
                '123' + word, '2023' + word, '2024' + word,
            ])
        words.update(kombinasi)
        
        return list(words)
    
    def generate_smart_wordlist(self, zip_path: str) -> List[str]:
        """
        Generate wordlist cerdas berdasarkan konteks file
        """
        words = set()
        
        # Ambil nama file tanpa ekstensi
        base_name = os.path.splitext(os.path.basename(zip_path))[0]
        
        # Bersihkan dari karakter khusus
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', base_name)
        if clean_name:
            words.add(clean_name.lower())
            words.add(clean_name.upper())
            words.add(clean_name.capitalize())
        
        # Split berdasarkan pemisah umum
        parts = re.split(r'[_\-\s\.]', base_name)
        for part in parts:
            if len(part) > 2:
                words.add(part.lower())
        
        # Tambah variasi
        for word in list(words):
            words.add(word + '123')
            words.add(word + '2024')
            words.add(word + '!')
            words.add('123' + word)
        
        return list(words)
    
    def generate_rule_based(self, word: str) -> List[str]:
        """
        Generate variasi password berdasarkan rules (seperti John rules)
        """
        variations = []
        
        # Rule 1: Capitalize first letter
        variations.append(word.capitalize())
        
        # Rule 2: All uppercase
        variations.append(word.upper())
        
        # Rule 3: Add numbers at end
        for num in ['123', '1234', '12345', '2024', '2025', '69', '99', '00']:
            variations.append(word + num)
        
        # Rule 4: Add numbers at beginning
        for num in ['123', '2024', '99']:
            variations.append(num + word)
        
        # Rule 5: Leet speak
        leet = word
        leet = leet.replace('a', '4').replace('i', '1').replace('e', '3')
        leet = leet.replace('o', '0').replace('s', '5').replace('t', '7')
        variations.append(leet)
        
        # Rule 6: Toggle case
        variations.append(''.join(c.upper() if i%2 else c.lower() for i, c in enumerate(word)))
        
        # Rule 7: Duplicate
        variations.append(word * 2)
        
        # Rule 8: Reverse
        variations.append(word[::-1])
        
        # Rule 9: Add special chars
        for char in ['!', '@', '#', '$', '%', '&', '*']:
            variations.append(word + char)
            variations.append(char + word)
        
        return list(set(variations))  # Hapus duplikat
    
    # ==================== ATTACK METHODS ====================
    def test_password(self, zip_path: str, password: str, output_path: str = None) -> bool:
        """
        Test satu password dengan multiple methods
        """
        # Cek di pot file dulu (seperti John)
        if password in self.cracked_passwords:
            return False
        
        # Method 1: zipfile with multiple encodings
        for encoding in ['utf-8', 'latin-1', 'cp437', 'cp1252']:
            try:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    pwd_bytes = password.encode(encoding)
                    
                    # Test dengan extract (fast check)
                    if output_path:
                        zf.extractall(path=output_path, pwd=pwd_bytes)
                    else:
                        # Just test first file
                        first_file = zf.namelist()[0]
                        zf.read(first_file, pwd=pwd_bytes)
                    
                    return True
            except (RuntimeError, zipfile.BadZipFile):
                continue
            except:
                continue
        
        # Method 2: 7zip jika tersedia
        if platform.system() == "Windows":
            seven_zip_paths = [
                r"C:\Program Files\7-Zip\7z.exe",
                r"C:\Program Files (x86)\7-Zip\7z.exe"
            ]
            for sz_path in seven_zip_paths:
                if os.path.exists(sz_path):
                    try:
                        if output_path:
                            cmd = [sz_path, 't', f'-p{password}', zip_path]
                        else:
                            cmd = [sz_path, 't', f'-p{password}', zip_path]
                        
                        result = subprocess.run(cmd, capture_output=True, timeout=5)
                        if result.returncode == 0:
                            return True
                    except:
                        continue
        
        return False
    
    def dictionary_attack(self, zip_path: str, wordlist: List[str], 
                          output_path: str = None, threads: int = 4) -> Optional[str]:
        """
        Dictionary attack dengan multi-threading
        """
        self.current_mode = "Dictionary Attack"
        self.print_header(f"DICTIONARY ATTACK with {len(wordlist):,} words")
        
        # Setup queue
        password_queue = queue.Queue()
        for pwd in wordlist:
            password_queue.put(pwd)
        
        total = len(wordlist)
        found = threading.Event()
        start_time = time.time()
        
        # Progress display
        def progress_display():
            while not found.is_set() and not self.stop_flag:
                elapsed = time.time() - start_time
                tested = total - password_queue.qsize()
                speed = tested / elapsed if elapsed > 0 else 0
                percent = (tested / total) * 100 if total > 0 else 0
                
                sys.stdout.write(f"\r{Colors.CYAN}Progress: {percent:6.2f}% | "
                                 f"Tested: {tested:,}/{total:,} | "
                                 f"Speed: {speed:8.0f} p/s | "
                                 f"Time: {timedelta(seconds=int(elapsed))}{Colors.RESET}")
                sys.stdout.flush()
                time.sleep(0.5)
        
        # Worker thread
        def worker():
            while not found.is_set() and not self.stop_flag:
                try:
                    password = password_queue.get_nowait()
                except queue.Empty:
                    break
                
                if self.test_password(zip_path, password, output_path):
                    found.set()
                    with self.lock:
                        self.found_password = password
                        self.successful_method = "Dictionary Attack"
                        self.save_to_pot(zip_path, password)
                    break
                
                with self.lock:
                    self.attempts += 1
                
                password_queue.task_done()
        
        # Start progress display
        progress_thread = threading.Thread(target=progress_display)
        progress_thread.daemon = True
        progress_thread.start()
        
        # Start workers
        worker_threads = []
        for _ in range(min(threads, total)):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            worker_threads.append(t)
        
        # Wait for completion
        try:
            for t in worker_threads:
                t.join(timeout=1)
                if found.is_set() or self.stop_flag:
                    break
        except KeyboardInterrupt:
            self.stop_flag = True
        
        print()  # New line after progress
        
        return self.found_password
    
    def brute_force_numeric(self, zip_path: str, min_len: int = 1, max_len: int = 8,
                           output_path: str = None, threads: int = 4) -> Optional[str]:
        """
        Brute force untuk password numerik
        """
        self.current_mode = "Numeric Brute Force"
        
        total_combs = sum(10 ** i for i in range(min_len, max_len + 1))
        self.print_header(f"NUMERIC BRUTE FORCE ({min_len}-{max_len} digits)")
        self.print_info(f"Total combinations: {total_combs:,}")
        
        if total_combs > 10_000_000:
            self.print_warning("This will take a VERY long time!")
            resp = input("Continue? (y/n): ").lower()
            if resp != 'y':
                return None
        
        start_time = time.time()
        
        for length in range(min_len, max_len + 1):
            if self.found_password or self.stop_flag:
                break
            
            self.print_progress(f"Trying length {length}...")
            
            # Generate combinations in batches
            batch = []
            batch_size = 100_000
            
            for combo in itertools.product('0123456789', repeat=length):
                password = ''.join(combo)
                batch.append(password)
                
                if len(batch) >= batch_size:
                    if self.dictionary_attack(zip_path, batch, output_path, threads):
                        return self.found_password
                    batch = []
                    
                    # Show progress
                    elapsed = time.time() - start_time
                    speed = self.attempts / elapsed if elapsed > 0 else 0
                    self.print_progress(f"Tested: {self.attempts:,} | Speed: {speed:,.0f} p/s")
            
            if batch:
                if self.dictionary_attack(zip_path, batch, output_path, threads):
                    return self.found_password
        
        return None
    
    def brute_force_alpha(self, zip_path: str, min_len: int = 1, max_len: int = 5,
                         output_path: str = None, threads: int = 4) -> Optional[str]:
        """
        Brute force untuk huruf
        """
        self.current_mode = "Alpha Brute Force"
        charset = 'abcdefghijklmnopqrstuvwxyz'
        
        total_combs = sum(len(charset) ** i for i in range(min_len, max_len + 1))
        self.print_header(f"ALPHA BRUTE FORCE ({min_len}-{max_len} letters)")
        self.print_info(f"Total combinations: {total_combs:,}")
        self.print_warning("This is extremely SLOW for length > 4!")
        
        if total_combs > 1_000_000:
            resp = input("Continue? (y/n): ").lower()
            if resp != 'y':
                return None
        
        start_time = time.time()
        
        for length in range(min_len, max_len + 1):
            if self.found_password or self.stop_flag:
                break
            
            self.print_progress(f"Trying length {length}...")
            
            batch = []
            batch_size = 50_000
            
            for combo in itertools.product(charset, repeat=length):
                password = ''.join(combo)
                
                # Try lowercase
                batch.append(password)
                
                # Try uppercase
                batch.append(password.upper())
                
                # Try capitalize
                batch.append(password.capitalize())
                
                if len(batch) >= batch_size:
                    if self.dictionary_attack(zip_path, batch, output_path, threads):
                        return self.found_password
                    batch = []
                    
                    elapsed = time.time() - start_time
                    speed = self.attempts / elapsed if elapsed > 0 else 0
                    self.print_progress(f"Tested: {self.attempts:,} | Speed: {speed:,.0f} p/s")
            
            if batch:
                if self.dictionary_attack(zip_path, batch, output_path, threads):
                    return self.found_password
        
        return None
    
    def mask_attack(self, zip_path: str, mask: str, output_path: str = None,
                   threads: int = 4) -> Optional[str]:
        """
        Mask attack seperti ?l?d?d?d di John
        ?l = lowercase, ?u = uppercase, ?d = digit, ?s = special, ?a = all
        """
        self.current_mode = "Mask Attack"
        self.print_header(f"MASK ATTACK: {mask}")
        
        # Parse mask
        charsets = {
            '?l': 'abcdefghijklmnopqrstuvwxyz',
            '?u': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            '?d': '0123456789',
            '?s': '!@#$%^&*()-_+=[]{}|;:,.<>?/~`',
            '?a': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_+=[]{}|;:,.<>?/~`',
        }
        
        # Build charset list
        charset_list = []
        i = 0
        while i < len(mask):
            if mask[i] == '?' and i + 1 < len(mask):
                key = mask[i:i+2]
                if key in charsets:
                    charset_list.append(charsets[key])
                else:
                    self.print_error(f"Invalid mask: {key}")
                    return None
                i += 2
            else:
                charset_list.append(mask[i])
                i += 1
        
        # Calculate total combinations
        total = 1
        for cs in charset_list:
            if isinstance(cs, str) and len(cs) > 1:
                total *= len(cs)
        
        self.print_info(f"Total combinations: {total:,}")
        
        if total > 10_000_000:
            self.print_warning("This will take a VERY long time!")
            resp = input("Continue? (y/n): ").lower()
            if resp != 'y':
                return None
        
        # Generate combinations
        start_time = time.time()
        batch = []
        batch_size = 100_000
        
        for combo in itertools.product(*[cs if isinstance(cs, str) else [cs] for cs in charset_list]):
            password = ''.join(combo)
            batch.append(password)
            
            if len(batch) >= batch_size:
                if self.dictionary_attack(zip_path, batch, output_path, threads):
                    return self.found_password
                batch = []
                
                elapsed = time.time() - start_time
                speed = self.attempts / elapsed if elapsed > 0 else 0
                self.print_progress(f"Tested: {self.attempts:,} | Speed: {speed:,.0f} p/s")
        
        if batch:
            if self.dictionary_attack(zip_path, batch, output_path, threads):
                return self.found_password
        
        return None
    
    def incremental_attack(self, zip_path: str, output_path: str = None,
                          threads: int = 4) -> Optional[str]:
        """
        Incremental attack dengan prioritas password umum
        """
        self.current_mode = "Incremental Attack"
        self.print_header("INCREMENTAL ATTACK")
        
        # Priority 1: Common Indonesian passwords
        self.print_progress("Phase 1: Common Indonesian passwords")
        wordlist = self.generate_indonesian_wordlist()
        if self.dictionary_attack(zip_path, wordlist, output_path, threads):
            return self.found_password
        
        # Priority 2: Smart wordlist based on filename
        self.print_progress("Phase 2: Smart wordlist from filename")
        wordlist = self.generate_smart_wordlist(zip_path)
        if self.dictionary_attack(zip_path, wordlist, output_path, threads):
            return self.found_password
        
        # Priority 3: Years (1945-2025)
        self.print_progress("Phase 3: Years")
        years = [str(y) for y in range(1945, 2026)]
        years.extend([str(y)[2:] for y in range(1945, 2026)])
        years.extend(['17081945', '19450817', '1998', '1999', '2000'])
        if self.dictionary_attack(zip_path, years, output_path, threads):
            return self.found_password
        
        # Priority 4: Dates (DDMMYYYY)
        self.print_progress("Phase 4: Common dates")
        dates = []
        for day in range(1, 32):
            for month in range(1, 13):
                dates.append(f"{day:02d}{month:02d}")
                dates.append(f"{day:02d}{month:02d}2024")
        if self.dictionary_attack(zip_path, dates, output_path, threads):
            return self.found_password
        
        # Priority 5: Numeric (1-6 digits)
        self.print_progress("Phase 5: Numeric (1-6 digits)")
        numeric = []
        for length in range(1, 7):
            for combo in itertools.product('0123456789', repeat=length):
                numeric.append(''.join(combo))
                if len(numeric) >= 100000:
                    if self.dictionary_attack(zip_path, numeric, output_path, threads):
                        return self.found_password
                    numeric = []
        
        if numeric:
            if self.dictionary_attack(zip_path, numeric, output_path, threads):
                return self.found_password
        
        return None
    
    # ==================== MAIN METHODS ====================
    def crack_zip(self, zip_path: str, output_path: str = None, 
                  wordlist_file: str = None, mode: str = 'auto',
                  threads: int = 4, mask: str = None) -> bool:
        """
        Main method untuk crack ZIP file
        """
        self.start_time = time.time()
        self.attempts = 0
        
        print(BANNER)
        
        # Analisis file
        self.print_header("ZIP FILE ANALYSIS")
        analysis = self.analyze_zip(zip_path)
        
        print(f"  File: {analysis['filename']}")
        print(f"  Size: {analysis['size']:,} bytes")
        print(f"  Valid ZIP: {'✅' if analysis['valid_zip'] else '❌'}")
        print(f"  Encrypted: {'✅' if analysis['encrypted'] else '❌'}")
        print(f"  Encryption: {analysis['encryption_type']}")
        print(f"  Files: {analysis['file_count']}")
        print(f"  Recommended: {analysis['recommended_attack']}")
        
        if not analysis['encrypted']:
            self.print_success("File is not encrypted!")
            if output_path:
                self.extract_zip(zip_path, '', output_path)
            return True
        
        # Load external wordlist jika ada
        external_words = []
        if wordlist_file and os.path.exists(wordlist_file):
            self.print_progress(f"Loading wordlist: {wordlist_file}")
            try:
                with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
                    external_words = [line.strip() for line in f if line.strip()]
                self.print_success(f"Loaded {len(external_words):,} words")
            except Exception as e:
                self.print_error(f"Failed to load wordlist: {e}")
        
        # Pilih mode
        if mode == 'auto':
            self.print_header("AUTO MODE - Trying all methods")
            
            # Method 1: External wordlist
            if external_words:
                self.print_progress("Method 1: External wordlist")
                if self.dictionary_attack(zip_path, external_words, output_path, threads):
                    self.print_success(f"Password found: {self.found_password}")
                    self.print_stats()
                    return True
            
            # Method 2: Indonesian wordlist
            self.print_progress("Method 2: Indonesian wordlist")
            indo_words = self.generate_indonesian_wordlist()
            if self.dictionary_attack(zip_path, indo_words, output_path, threads):
                self.print_success(f"Password found: {self.found_password}")
                self.print_stats()
                return True
            
            # Method 3: Smart wordlist
            self.print_progress("Method 3: Smart wordlist from filename")
            smart_words = self.generate_smart_wordlist(zip_path)
            if self.dictionary_attack(zip_path, smart_words, output_path, threads):
                self.print_success(f"Password found: {self.found_password}")
                self.print_stats()
                return True
            
            # Method 4: Years
            self.print_progress("Method 4: Years (1945-2025)")
            years = [str(y) for y in range(1945, 2026)]
            if self.dictionary_attack(zip_path, years, output_path, threads):
                self.print_success(f"Password found: {self.found_password}")
                self.print_stats()
                return True
            
            # Method 5: Numeric (1-6 digits)
            self.print_progress("Method 5: Numeric (1-6 digits)")
            numeric = []
            for length in range(1, 7):
                for combo in itertools.product('0123456789', repeat=length):
                    numeric.append(''.join(combo))
                    if len(numeric) >= 100000:
                        if self.dictionary_attack(zip_path, numeric, output_path, threads):
                            self.print_success(f"Password found: {self.found_password}")
                            self.print_stats()
                            return True
                        numeric = []
            
            if numeric:
                if self.dictionary_attack(zip_path, numeric, output_path, threads):
                    self.print_success(f"Password found: {self.found_password}")
                    self.print_stats()
                    return True
            
        elif mode == 'dictionary':
            if external_words:
                self.dictionary_attack(zip_path, external_words, output_path, threads)
            else:
                words = self.generate_indonesian_wordlist()
                self.dictionary_attack(zip_path, words, output_path, threads)
        
        elif mode == 'numeric':
            self.brute_force_numeric(zip_path, 1, 8, output_path, threads)
        
        elif mode == 'alpha':
            self.brute_force_alpha(zip_path, 1, 5, output_path, threads)
        
        elif mode == 'incremental':
            self.incremental_attack(zip_path, output_path, threads)
        
        elif mode == 'mask' and mask:
            self.mask_attack(zip_path, mask, output_path, threads)
        
        # Hasil akhir
        self.print_stats()
        
        if self.found_password:
            self.print_success(f"✅ PASSWORD FOUND: {self.found_password}")
            self.print_success(f"Method: {self.successful_method}")
            
            # Ekstrak file jika diminta
            if output_path:
                self.extract_zip(zip_path, self.found_password, output_path)
            
            return True
        else:
            self.print_error("❌ PASSWORD NOT FOUND")
            self.print_info("Try with larger wordlist or different mode")
            return False
    
    def extract_zip(self, zip_path: str, password: str, output_path: str):
        """
        Ekstrak file ZIP dengan password yang ditemukan
        """
        self.print_header("EXTRACTING FILES")
        
        # Buat direktori dengan timestamp
        extract_dir = os.path.join(output_path, f"extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(extract_dir, exist_ok=True)
        
        self.print_progress(f"Extracting to: {extract_dir}")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Coba berbagai encoding
                for encoding in ['utf-8', 'latin-1', 'cp437']:
                    try:
                        pwd_bytes = password.encode(encoding)
                        zf.extractall(path=extract_dir, pwd=pwd_bytes)
                        
                        # Hitung file
                        extracted = os.listdir(extract_dir)
                        self.print_success(f"Successfully extracted {len(extracted)} files")
                        
                        # Tampilkan beberapa file
                        for f in extracted[:10]:
                            size = os.path.getsize(os.path.join(extract_dir, f))
                            print(f"  📄 {f} ({size:,} bytes)")
                        
                        if len(extracted) > 10:
                            print(f"  ... and {len(extracted) - 10} more files")
                        
                        return
                    except:
                        continue
            
            self.print_error("Failed to extract with all encodings")
            
        except Exception as e:
            self.print_error(f"Extraction failed: {e}")
    
    def run_interactive(self):
        """Mode interaktif dengan menu"""
        
        print(BANNER)
        
        while True:
            print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
            print(f"{Colors.YELLOW}{Colors.BOLD}🔥 ZIP-KRAKEN v{VERSION} - INTERACTIVE MENU 🔥{Colors.RESET}")
            print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
            
            print(f"\n{Colors.GREEN}[1]{Colors.RESET} 🎯 AUTO CRACK (Recommended)")
            print(f"{Colors.GREEN}[2]{Colors.RESET} 📚 Dictionary Attack")
            print(f"{Colors.GREEN}[3]{Colors.RESET} 🔢 Numeric Brute Force")
            print(f"{Colors.GREEN}[4]{Colors.RESET} 🔤 Alpha Brute Force")
            print(f"{Colors.GREEN}[5]{Colors.RESET} 📈 Incremental Attack")
            print(f"{Colors.GREEN}[6]{Colors.RESET} 🎭 Mask Attack (like John)")
            print(f"{Colors.GREEN}[7]{Colors.RESET} 🔍 Analyze ZIP Only")
            print(f"{Colors.GREEN}[8]{Colors.RESET} 🇮🇩 Indonesian Wordlist Generator")
            print(f"{Colors.GREEN}[9]{Colors.RESET} 📊 Show Statistics")
            print(f"{Colors.GREEN}[0]{Colors.RESET} 🚪 Exit")
            
            choice = input(f"\n{Colors.YELLOW}Select option [0-9]: {Colors.RESET}").strip()
            
            if choice == '0':
                print(f"\n{Colors.GREEN}Thank you for using ZIP-KRAKEN!{Colors.RESET}")
                break
            
            elif choice == '1':
                zip_file = input("📁 ZIP file path: ").strip()
                if not os.path.exists(zip_file):
                    self.print_error("File not found!")
                    continue
                
                output = input("📂 Output directory (optional): ").strip() or None
                wordlist = input("📚 Wordlist file (optional): ").strip() or None
                threads = int(input("⚡ Threads [default=4]: ").strip() or "4")
                
                self.crack_zip(zip_file, output, wordlist, 'auto', threads)
            
            elif choice == '2':
                zip_file = input("📁 ZIP file path: ").strip()
                if not os.path.exists(zip_file):
                    self.print_error("File not found!")
                    continue
                
                wordlist = input("📚 Wordlist file: ").strip()
                if not os.path.exists(wordlist):
                    self.print_error("Wordlist not found!")
                    continue
                
                output = input("📂 Output directory (optional): ").strip() or None
                threads = int(input("⚡ Threads [default=4]: ").strip() or "4")
                
                self.crack_zip(zip_file, output, wordlist, 'dictionary', threads)
            
            elif choice == '3':
                zip_file = input("📁 ZIP file path: ").strip()
                if not os.path.exists(zip_file):
                    self.print_error("File not found!")
                    continue
                
                min_len = int(input("🔢 Min length [default=1]: ").strip() or "1")
                max_len = int(input("🔢 Max length [default=8]: ").strip() or "8")
                output = input("📂 Output directory (optional): ").strip() or None
                threads = int(input("⚡ Threads [default=4]: ").strip() or "4")
                
                self.brute_force_numeric(zip_file, min_len, max_len, output, threads)
            
            elif choice == '4':
                zip_file = input("📁 ZIP file path: ").strip()
                if not os.path.exists(zip_file):
                    self.print_error("File not found!")
                    continue
                
                min_len = int(input("🔤 Min length [default=1]: ").strip() or "1")
                max_len = int(input("🔤 Max length [default=4]: ").strip() or "4")
                output = input("📂 Output directory (optional): ").strip() or None
                threads = int(input("⚡ Threads [default=4]: ").strip() or "4")
                
                self.brute_force_alpha(zip_file, min_len, max_len, output, threads)
            
            elif choice == '5':
                zip_file = input("📁 ZIP file path: ").strip()
                if not os.path.exists(zip_file):
                    self.print_error("File not found!")
                    continue
                
                output = input("📂 Output directory (optional): ").strip() or None
                threads = int(input("⚡ Threads [default=4]: ").strip() or "4")
                
                self.incremental_attack(zip_file, output, threads)
            
            elif choice == '6':
                zip_file = input("📁 ZIP file path: ").strip()
                if not os.path.exists(zip_file):
                    self.print_error("File not found!")
                    continue
                
                print(f"\n{Colors.CYAN}Mask Format:{Colors.RESET}")
                print("  ?l = lowercase letter")
                print("  ?u = uppercase letter")
                print("  ?d = digit")
                print("  ?s = special character")
                print("  ?a = all characters")
                print(f"{Colors.YELLOW}Example: ?l?l?l?d?d?d = abc123{Colors.RESET}")
                
                mask = input("\n🎭 Enter mask: ").strip()
                output = input("📂 Output directory (optional): ").strip() or None
                threads = int(input("⚡ Threads [default=4]: ").strip() or "4")
                
                self.mask_attack(zip_file, mask, output, threads)
            
            elif choice == '7':
                zip_file = input("📁 ZIP file path: ").strip()
                if os.path.exists(zip_file):
                    analysis = self.analyze_zip(zip_file)
                    print(f"\n{Colors.CYAN}ANALYSIS RESULTS:{Colors.RESET}")
                    for key, value in analysis.items():
                        if key not in ['files']:
                            print(f"  {key}: {value}")
                else:
                    self.print_error("File not found!")
            
            elif choice == '8':
                count = int(input("📊 Number of words to generate [default=1000]: ").strip() or "1000")
                words = self.generate_indonesian_wordlist()[:count]
                
                output = input("💾 Save to file (optional): ").strip()
                if output:
                    with open(output, 'w') as f:
                        for w in words:
                            f.write(w + '\n')
                    self.print_success(f"Saved {len(words)} words to {output}")
                else:
                    print(f"\n{Colors.CYAN}Sample words:{Colors.RESET}")
                    for w in words[:50]:
                        print(f"  {w}")
            
            elif choice == '9':
                self.print_stats()

# ==================== MAIN ====================
def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(
        description='ZIP-KRAKEN - Professional ZIP Password Cracker',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-z', '--zip', help='Target ZIP file')
    parser.add_argument('-o', '--output', help='Output directory for extracted files')
    parser.add_argument('-w', '--wordlist', help='Wordlist file')
    parser.add_argument('-m', '--mode', default='auto',
                       choices=['auto', 'dictionary', 'numeric', 'alpha', 'incremental', 'mask'],
                       help='Attack mode (default: auto)')
    parser.add_argument('--mask', help='Mask for mask attack (e.g., ?l?l?d?d)')
    parser.add_argument('-t', '--threads', type=int, default=4, help='Number of threads (default: 4)')
    parser.add_argument('--min-len', type=int, default=1, help='Minimum length for brute force')
    parser.add_argument('--max-len', type=int, default=8, help='Maximum length for brute force')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--analyze', action='store_true', help='Analyze ZIP only')
    
    args = parser.parse_args()
    
    kraken = ZIPKraken()
    
    # Interactive mode
    if args.interactive or len(sys.argv) == 1:
        kraken.run_interactive()
        return
    
    # Analyze only
    if args.analyze:
        if not args.zip:
            print("Error: ZIP file required")
            return
        analysis = kraken.analyze_zip(args.zip)
        print(f"\n{Colors.CYAN}ANALYSIS RESULTS:{Colors.RESET}")
        for key, value in analysis.items():
            if key not in ['files']:
                print(f"  {key}: {value}")
        return
    
    # Crack mode
    if args.zip:
        if not os.path.exists(args.zip):
            print(f"Error: File not found: {args.zip}")
            return
        
        kraken.crack_zip(
            zip_path=args.zip,
            output_path=args.output,
            wordlist_file=args.wordlist,
            mode=args.mode,
            threads=args.threads,
            mask=args.mask
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")