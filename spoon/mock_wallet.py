import time
import random

class MockEVMWallet:
    def __init__(self):
        self.block = 849201
        self.total_sent = 0.0
        self.balances = {}

    def send_usdc(self, to_address: str, amount_usdc: float = 1.0) -> dict:
        time.sleep(0.4 + random.random() * 0.6)
        gas = 0.00032 + random.random() * 0.00005
        print(f"⚡ [GAS] {gas:.5f} ETH burned")
        time.sleep(0.2 + random.random() * 0.3)
        tx_hash = "0x" + ("MOCK" + str(int(random.random() * 1e8))).ljust(64, "0")
        self.total_sent += float(amount_usdc)
        self.balances[to_address] = self.balances.get(to_address, 0.0) + float(amount_usdc)
        print(f"✅ [CONFIRMED] Block #{self.block}. Sent {amount_usdc} USDC.")
        print(f"🏦 [USDC] Balance for {to_address}: {self.balances[to_address]:.2f} · Total sent: {self.total_sent:.2f}")
        return {
            "success": True,
            "tx_hash": tx_hash,
            "block": self.block,
            "amount_usdc": amount_usdc,
            "balance": self.balances[to_address],
            "total_sent": self.total_sent,
        }