import json

from web3.providers import rpc
from contracts.bsc import Contracts
from web3 import Web3
import time

abi_erc_20 = "./abis/erc-20.json"
abi_factory = "./abis/factory.json"
abi_pair = "./abis/pair.json"
abi_router = "./abis/router.json"
def loadJsonFile(filename):
    with open(filename, 'r') as abi:
	    return json.load(abi)
ABI = {
    'ERC_20':loadJsonFile(abi_erc_20),
    'FACTORY':loadJsonFile(abi_factory),
    'PAIR':loadJsonFile(abi_pair),
    'ROUTER':loadJsonFile(abi_router)
}

class DeFiSDK:

	def __init__(self,rpc_url,wallet_addr,private_key):
		self.setRPC(rpc_url)
		self.setWallet(wallet_addr,private_key)


	def setRPC(self,rpc_url):
		self.web3 = Web3(Web3.HTTPProvider(rpc_url))

	def setTransaction(self,gas,gas_limit):
		self.gas = str(gas)
		self.gas_limit = gas_limit

	def setWallet(self,wallet_addr,wallet_key):
		self.senderAddress = wallet_addr
		self.private_key = wallet_key


	def getPrice(self,factory,pair):
		factoryAddress = self.web3.toChecksumAddress(Contracts['AMM'][factory]['Factory'])
		tokenA, tokenB = [self.web3.toChecksumAddress(Contracts['Tokens'][i]) for i in pair.split('/')]
		
		contract = self.web3.eth.contract(address=factoryAddress, abi=ABI['FACTORY'])
		pair_address = contract.functions.getPair(tokenA, tokenB).call()
		tokensPair = self.web3.eth.contract(abi=ABI['PAIR'], address=pair_address)

		reserves = tokensPair.functions.getReserves().call()
		price = reserves[1] / reserves[0]
		return float(price)

	def swap(self, factory, tokenA, tokenB, amountIn, amountOutMin):
		factoryAddress = self.web3.toChecksumAddress(
		    Contracts['AMM'][factory]['Router'])

		contract = self.web3.eth.contract(address=factoryAddress, abi=ABI['ROUTER'])
		nonce = self.web3.eth.get_transaction_count(self.senderAddress)
		
		txn = contract.functions.swapExactTokensForTokens(
                    amountIn,
					amountOutMin,
                    [tokenB, tokenA],
                    self.senderAddress,
                    (int(time.time()) + 10000)
                ).buildTransaction({
                    "from": self.senderAddress,
                    "gas": self.gas_limit,
                    "gasPrice": self.web3.toWei(self.gas, "gwei"),
                  	"value": 0,
                    "nonce": nonce,
                })
		signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=self.private_key)
		tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
		return self.web3.toHex(tx_token)


	def buy(self,factory,pair,value):
		tokenA, tokenB = [self.web3.toChecksumAddress(Contracts['Tokens'][i]) for i in pair.split('/')]
		factoryAddress = self.web3.toChecksumAddress(
		    Contracts['AMM'][factory]['Router'])
		contract = self.web3.eth.contract(address=factoryAddress, abi=ABI['ROUTER'])
		amountOut = self.web3.toWei(value, 'ether')
		amountOutMin = int(amountOut * 0.99)
		amountIn = contract.functions.getAmountsIn(amountOut, [tokenB, tokenA]).call()
		amountIn = int(amountIn[0])

		return self.swap(factory,tokenA,tokenB,amountIn,amountOutMin)


	def sell(self, factory, pair, value):
		tokenB, tokenA = [self.web3.toChecksumAddress(
		    Contracts['Tokens'][i]) for i in pair.split('/')]
		factoryAddress = self.web3.toChecksumAddress(
		    Contracts['AMM'][factory]['Router'])

		contract = self.web3.eth.contract(address=factoryAddress, abi=ABI['ROUTER'])

		amountIn = self.web3.toWei(value, 'ether')
		amountOut = contract.functions.getAmountsOut(
		    amountIn, [tokenB, tokenA]).call()
		amountOutMin = int(amountOut[1] * 0.99)

		return self.swap(factory, tokenA, tokenB, amountIn, amountOutMin)


	def getBalance(self,token):
		token_address = self.web3.toChecksumAddress(Contracts['Tokens'][token])
		contract = self.web3.eth.contract(address = token_address,abi=ABI['ERC_20'])

		address = self.web3.toChecksumAddress(self.senderAddress)
		balance = contract.functions.balanceOf(address).call()
		data = self.web3.fromWei(balance,"ether")
		return float(data)

	
	def getWalletBalance(self):
		balance = self.web3.eth.get_balance(self.senderAddress)
		result = self.web3.fromWei(balance, 'ether')
		return float(result)

