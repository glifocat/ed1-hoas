import serial
import re
import requests
import time
import sys
import threading

# Configuration
SERIAL_PORT = "/dev/cu.SLAB_USBtoUART"  # Your ED1 port
BAUD_RATE = 115200
GITHUB_API_URL = "https://api.github.com/search/code"
REPO = "logickworkshop/Flipper-IRDB"  # Huge database of IR codes

def search_flipper_db(protocol, address, command):
    """Searches the Flipper Zero IRDB for the captured code."""
    
    # Flipper format usually looks like:
    # protocol: NEC
    # address: 00 FF 00 00
    # command: 14 EB 00 00
    
    # We need to be flexible with search terms because formats vary
    # Let's search for the command first as it's most unique
    
    # Convert 0xEB14 to "14 EB" (Little Endian often used in .ir files)
    cmd_hex = f"{command:04X}"
    addr_hex = f"{address:04X}"
    
    # Simple query: just the command hex
    query = f"{cmd_hex} repo:{REPO}"
    
    print(f"\n[🔍] Searching database for Protocol: {protocol}, Addr: {addr_hex}, Cmd: {cmd_hex}...")
    
    try:
        # GitHub Code Search API
        response = requests.get(
            GITHUB_API_URL,
            params={"q": query},
            headers={"Accept": "application/vnd.github.v3+json"}
        )
        
        data = response.json()
        
        if "items" in data and len(data["items"]) > 0:
            print(f"[✅] Found {len(data['items'])} potential matches!")
            for item in data["items"][:5]: # Show top 5
                print(f"   📄 File: {item['path']}")
                print(f"      🔗 Link: {item['html_url']}")
        else:
            print("[❌] No exact matches found in Flipper DB.")
            
    except Exception as e:
        print(f"[!] API Error: {e}")

def parse_line(line):
    """Parses ESPHome logs for IR codes."""
    # Regex for ESPHome logs: "Received NEC: address=0xFF00, command=0xEB14"
    nec_match = re.search(r"Received NEC: address=0x([0-9A-Fa-f]+), command=0x([0-9A-Fa-f]+)", line)
    if nec_match:
        addr = int(nec_match.group(1), 16)
        cmd = int(nec_match.group(2), 16)
        print(f"\n[⚡] CAPTURED NEC SIGNAL!")
        print(f"    Address: 0x{addr:04X}")
        print(f"    Command: 0x{cmd:04X}")
        
        # Launch search in a separate thread to not block serial
        threading.Thread(target=search_flipper_db, args=("NEC", addr, cmd)).start()
        return

    # Regex for LG: "Received LG: data=0x00FF28D7"
    lg_match = re.search(r"Received LG: data=0x([0-9A-Fa-f]+)", line)
    if lg_match:
        data = int(lg_match.group(1), 16)
        # LG is often 32 bits. Split into addr/cmd roughly for logging
        print(f"\n[⚡] CAPTURED LG SIGNAL!")
        print(f"    Data: 0x{data:08X}")
        # Search for the last 4 chars (often the command)
        cmd_part = data & 0xFFFF
        threading.Thread(target=search_flipper_db, args=("LG", 0, cmd_part)).start()

def main():
    print("------------------------------------------------")
    print("       📡 ED1 IR SHAZAM (IDENTIFIER) 📡        ")
    print("------------------------------------------------")
    print(f"Connecting to {SERIAL_PORT}...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("[✅] Connected! Point your remote at the ED1 and press a button.")
        
        while True:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    # Filter only relevant lines to reduce noise
                    if "Received" in line:
                        parse_line(line)
            except SerialException:
                pass
                
    except KeyboardInterrupt:
        print("\n[👋] Exiting...")
    except Exception as e:
        print(f"\n[❌] Connection Error: {e}")
        print("Make sure the ED1 is connected and ESPHome logs are NOT running in another terminal.")

if __name__ == "__main__":
    main()
