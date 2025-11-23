import time
import random

class MockEVMWallet:
    def __init__(self):
        self.block = 849201

    def send_usdc(self, to_address: str, amount_usdc: float = 1.0) -> dict:
        time.sleep(0.4 + random.random() * 0.6)
        gas = 0.00032 + random.random() * 0.00005
        print(f"⚡ [GAS] {gas:.5f} ETH burned")
        time.sleep(0.2 + random.random() * 0.3)
        tx_hash = "0x" + ("MOCK" + str(int(random.random() * 1e8))).ljust(64, "0")
        print(f"✅ [CONFIRMED] Block #{self.block}. Sent {amount_usdc} USDC.")
        return {
            "success": True,
            "tx_hash": tx_hash,
            "block": self.block,
            "amount_usdc": amount_usdc,
        }