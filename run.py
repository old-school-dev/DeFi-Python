from web3.providers import rpc
from defi_sdk import DeFiSDK
sdk = DeFiSDK(rpc_url='https://bsc-dataseed.binance.org/',
              wallet_addr='',
              private_key='')
#Get price form Dex
price = sdk.getPrice('Twindex', 'DOP/BUSD')
print(price)

#Buy Order
buy_hsh = sdk.buy('Twindex', 'DOP/BUSD', 5)  # 5 is BUSD 
print(buy_hsh)

#Sell Order
sell_hsh = sdk.sell('Twindex', 'DOP/BUSD', 5) # 5 is DOP 
print(sell_hsh)
#Get Token Balance
tokenBalance = sdk.getBalance('DOP')
print("DOP: ",tokenBalance)


print(sdk.getBNBBalance())
