import bt_common as bt
import json, random

print("--- COMPUTER (CENTRAL) SEARCHING ---")
sock = bt.get_sock()
current_passkey = str(random.randint(100000, 999999))
bonded_device = None

while True:
    data, _ = sock.recvfrom(1024)
    msg = json.loads(data.decode())

    if msg['type'] == "ADVERTISE":
        dev_id = msg['from']
        mode = msg['data']['mode']
        print(f"Found Device: {dev_id} (Mode: {mode})")
        
        if mode == "just_works":
            print(f"Pairing with {dev_id} automatically...")
            bt.send_msg("COMPUTER", "PAIR_REQ", {"target": dev_id})
            bonded_device = dev_id
        else:
            print(f"*** PASSKEY REQUIRED: {current_passkey} ***")
            print(f"Enter this on the {dev_id} using buttons.")
            bt.send_msg("COMPUTER", "PAIR_REQ", {"target": dev_id})

    if msg['type'] == "STK_VERIFY":
        if msg['data']['stk'] == current_passkey:
            print("Passkey Match! Device Bonded Safely.")
            bt.send_msg("COMPUTER", "AUTH_OK", {})
            bonded_device = msg['from']
        else:
            print(f"SECURITY ALERT: Incorrect Passkey from {msg['from']}!")

    if bonded_device and msg['from'] == bonded_device and msg['type'] == "DATA":
        print(f"Received from {msg['from']} [{msg['data']['gatt']}]: {msg['data']['val']}")
    