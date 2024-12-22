from lib.unisats.orderlayer import OrdzWallet
from lib.unisats.common import RequestConnection, UNISAT_WALLET_PRC


class UnisatsErr(Exception):
    pass


class WALLETCONNECT_STATUS_CHANGED(Exception):
    pass


class Unisats(RequestConnection, OrdzWallet):
    def __init__(self):
        self.unsats__init__uni()
        super().__init__(url=UNISAT_WALLET_PRC)

    def getWalletConfig(self) -> dict:
        return self._q('default/config')

    def getAddressBalance(self, address: str):
        return self._q('address/balance', data={"address": address})

    def getMultiAddressAssets(self, address: str):
        return self._q('address/multi-assets', data={"address": address})

    def findGroupAssets(self, group: str):
        """
        group = {type, address_arr}
        :param group:
        :return:
        """
        return self._q('address/find-group-assets', method='POST', data=group)

    def getAddressUtxo(self, address: str):
        return self._q('address/btc-utxo', data={"address": address})

    def getInscriptionUtxo(self, address: str):
        return self._q('inscription/utxo', data={"address": address})

    def getInscriptionUtxoDetail(self, inscriptionId: str):
        return self._q('inscription/utxo-detail', data={"inscriptionId": inscriptionId})

    def getInscriptionUtxos(self, inscriptionId: str):
        return self._q('inscription/utxos', data={"inscriptionId": inscriptionId})

    def getAddressInscriptions(self, address: str, cursor: int, size: int):
        return self._q('inscription/btc-utxo', data={
            "address": address,
            "cursor": cursor,
            "size": size,
        })

    def getAddressRecentHistory(self, address: str):
        return self._q('address/recent-history', data={
            "address": address,
        })

    def getInscriptionSummary(self):
        return self._q('default/inscription-summary')

    def getAppSummary(self):
        return self._q('default/app-summary-v2')

    def pushTx(self, tx: str):
        return self._q('tx/broadcast', method='POST', data={"rawtx": tx})

    def getFeeSummary(self):
        return self._q('default/fee-summary')

    def getDomainInfo(self, domain: str):
        return self._q('address/search', data={"domain": domain})

    def inscribeBRC20Transfer(self, addr: str, tick: str, amount: str, feeRate: int):
        return self._q(
            'brc20/inscribe-transfer',
            method='POST',
            data={'address': addr, 'tick': tick, 'amount': amount, 'feeRate': feeRate}
        )

    def getInscribeResult(self, orderId: str):
        return self._q(
            'brc20/order-result',
            data={"orderId": orderId}
        )

    def getAddressTokenBalances(self, address: str, cursor: int, size: int):
        return self._q(
            'brc20/tokens',
            data={'address': address, 'cursor': cursor, 'size': size}
        )

    def getAddressTokenSummary(self, address: str, ticker: str):
        return self._q(
            'brc20/token-summary',
            data={'address': address, 'ticker': ticker}
        )

    def getTokenTransferableList(self, address: str, ticker: str, cursor: int, size: int):
        return self._q(
            'brc20/transferable-list',
            data={'address': address, 'ticker': ticker, 'cursor': cursor, 'size': size}
        )

    def decodePsbt(self, psbtHex: str):
        return self._q(
            'tx/decode',
            data={'psbtHex': psbtHex}
        )

    def createMoonpayUrl(self, address: str):
        return self._q(
            'moonpay/create',
            data={'address': address}
        )

    def checkWebsite(self, website: str):
        return self._q(
            'default/check-website',
            data={'website': website}
        )
