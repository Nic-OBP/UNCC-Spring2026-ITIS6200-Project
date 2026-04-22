import bt_common as bt
import time, json, sys, threading

class Peripheral:
    def __init__(self, mode="just_works"):
        self.id = "HEADPHONES_v1"
        self.mode = mode
        self.passkey = [0] * 6
        self.idx = 0
        self.bonded = False
        self.stk = None

    def input_loop(self):
        print(f"--- PERIPHERAL READY ({self.mode}) ---")
        print("Controls: [w] Increment Digit, [d] Next Digit/Confirm")
        while not self.bonded:
            cmd = sys.stdin.read(1)
            if cmd == 'w':
                self.passkey[self.idx] = (self.passkey[self.idx] + 1) % 10
                print(f"Entering Passkey: {self.passkey}")
            elif cmd == 'd':
                if self.idx < 5:
                    self.idx += 1
                    print(f"Moved to digit {self.idx + 1}")
                else:
                    self.stk = "".join(map(str, self.passkey))
                    print(f"STK Generated: {self.stk}. Sending for verification...")
                    bt.send_msg(self.id, "STK_VERIFY", {"stk": self.stk})

    def run(self):
        sock = bt.get_sock()
        threading.Thread(target=self.input_loop, daemon=True).start()
        
        while True:
            if not self.bonded:
                bt.send_msg(self.id, "ADVERTISE", {"mode": self.mode, "gatt": "HIF"})
                time.sleep(2)
            
            try:
                sock.settimeout(1)
                data, _ = sock.recvfrom(1024)
                msg = json.loads(data.decode())
                if msg['type'] == "PAIR_REQ" and msg['data']['target'] == self.id:
                    if self.mode == "just_works":
                        print("Just Works Pairing Success!")
                        self.bonded = True
                    else:
                        print("Waiting for manual Passkey entry...")
                elif msg['type'] == "AUTH_OK" and self.bonded == False:
                    print("Bonding Confirmed via Passkey!")
                    self.bonded = True
            except: continue

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "just_works"
    p = Peripheral(mode)
    p.run()
