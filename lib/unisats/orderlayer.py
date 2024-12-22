import base64
import random

from .bip341 import BIP341Taproot


def base36encoderequiredstr() -> str:
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    generated_characters = ''.join(random.choice(alphabet) for _ in range(10))
    return f"1.{generated_characters}"


class OrdzWallet(BIP341Taproot):
    def ordz_nonce(self, message) -> str:
        signature = self.okx_sign_message(message)
        return self._ordz_nonce_generation(self.address, self.hd_wallet.public_key(), message, signature)

    def _ordz_nonce_generation(self, import_addr: str, import_pubkey: str, message: str, signature: str,
                               wallet_type: str = "okx") -> str:
        _p = 'iVBORw0KGgoAAAANSUhEUAAAMnkl='
        _eka = f"{import_addr}-b-{message}-b-{signature}-b-{import_pubkey}-b-{wallet_type}-b-{_p}-b-{import_addr}"
        ac = base64.b64encode(_eka.encode()).decode()
        b = base36encoderequiredstr()[2:8]
        c = base36encoderequiredstr()[2:6]
        nonce_token = f"{ac[:8]}{b}{ac[8:13]}{c}{ac[13:]}"
        # print("> signature message")
        # print(message)
        # print("> generated nonce token")
        # print(nonce_token)
        # print("======================")
        # print(_eka.split("-b-"))
        return nonce_token
