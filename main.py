import time
import random
from data import *
from config import *
from web3 import Web3
from web3.middleware import geth_poa_middleware
from termcolor import cprint

if network in chains:
    network_settings = chains[network]
    rpc = network_settings.get("rpc")
    chain_id = network_settings.get("chain_id")
    native = network_settings.get("native")
    tx_type = network_settings.get("tx_type")

def read_private_keys():
    with open("wallets/keys.txt", "r") as file:
        private_keys = [line.strip() for line in file if line.strip()]
    return private_keys


def read_recipients():
    with open("wallets/recipients.txt", "r") as file:
        recipients = [line.strip() for line in file if line.strip()]
    return recipients

private_keys = read_private_keys()
recipients = read_recipients()

numbered_private_keys = list(enumerate(private_keys, start=1))
original_private_keys = numbered_private_keys.copy()

wallet_pair = dict(zip(private_keys, recipients))

for private_key in private_keys:
    recipient = wallet_pair[private_key]


def transfer(private_key, wallet_index, recipient, value=None):
    w3 = Web3(Web3.HTTPProvider(rpc))

    if network == "Ethereum":
        current_gas_price = w3.to_wei(max_gwei, "gwei")
        gas_check_attempts = 0

        while w3.eth.gas_price > current_gas_price:
            gas_check_attempts += 1
            if gas_check_attempts > max_gas_check_attempts:
                print(f"Достигнуто максимальное количество попыток({max_gas_check_attempts}). Завершаю работу...")
                return
            print(f"Попытка {gas_check_attempts}: Gwei ({w3.from_wei(w3.eth.gas_price, 'gwei')}) Выше чем максимально допустимый ({max_gwei} gwei). Сплю 10 секунд...")
            time.sleep(10)

    account = w3.eth.account.from_key(private_key)
    sender = w3.to_checksum_address(account.address)
    recipient = w3.to_checksum_address(recipient)

    balance = w3.eth.get_balance(account.address)
    balance_native = w3.from_wei(balance, "ether")

    tx = {
    'chainId': chain_id,
    'from': sender,
    'to': recipient,
    'nonce': w3.eth.get_transaction_count(sender),
    }

    if tx_type == "legacy":
        tx['gas'] = 21000
        tx['gasPrice'] = w3.eth.gas_price
    elif tx_type == "eip1559":
        if network == "Arbitrum":
            baseFee = w3.to_wei(0.1, 'gwei')
            tx['maxFeePerGas'] = w3.to_wei(0.135, "gwei")
            tx['maxPriorityFeePerGas'] = w3.to_wei(0, "ether")
            gas_limit = w3.eth.estimate_gas(tx) * 1.35
            tx['gas'] = int(gas_limit)
        elif network == "Ethereum":
            tx['gas'] = 21000
            current_gas_price = w3.eth.gas_price
            tx['maxFeePerGas'] = current_gas_price + w3.to_wei(8, "gwei")
            tx['maxPriorityFeePerGas'] = w3.to_wei(0.1, "gwei")
        elif network == "Avalanche":
            tx['gas'] = 21000
            current_gas_price = w3.eth.gas_price
            tx['maxFeePerGas'] = current_gas_price + w3.to_wei(8, "gwei")
            tx['maxPriorityFeePerGas'] = w3.to_wei(1.5, "gwei")
        elif network == "Optimism":
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            last_block = (w3.eth.get_block('latest'))
            base_fee_per_gas = int(last_block['baseFeePerGas'] * 1.02)
            max_priority_fee_per_gas = int(w3.eth.max_priority_fee)
            max_fee_per_gas =  int(base_fee_per_gas + max_priority_fee_per_gas)
            tx['maxFeePerGas'] = max_fee_per_gas
            tx['maxPriorityFeePerGas'] = max_priority_fee_per_gas
    
    if mode == "direct":
        native_amount = round(random.uniform(native_from, native_to), decimals)
    elif mode == "remain":
        native_amount = round(float(balance_native) - (random.uniform(native_remain_from, native_remain_to)), decimals)
    elif mode == "full_balance":
        if network == "Ethereum" or network == "Avalanche" or network == "Polygon" or network == "BSC":
            native_amount = round(float(balance_native) - float(w3.from_wei(21000 * w3.eth.gas_price, "ether")) * 1.99, decimals)
        elif network == "Arbitrum":
            native_amount = round(float(balance_native) - float(w3.from_wei(gas_limit * baseFee, "ether")) * 1.05, decimals)
        elif network == "Optimism":
            native_amount = round(float(balance_native) - float(w3.from_wei(random.uniform(0.000065, 0.000075), "ether")), decimals) 
    else:
        cprint('Не выбран режим работы "mode". Завершаю работу...', "red")
        return

    if value is None:
        value = native_amount
    tx['value'] = w3.to_wei((value),  "ether")
    
    if mode == "remain" or mode == "full_balance":
        if value < min_amount_to_send:
            print(f">>>[{wallet_index}] {account.address} Количество эфира {value} для отправки превышает ({min_amount_to_send} {native}). Транзакция не будет отправлена.")
            return   

    if network == "Arbitrum":
        total_cost = float(value) + float(w3.from_wei((gas_limit * w3.to_wei(0.1, "gwei")), "ether"))
    elif network == "Optimism":
        total_cost = float(value) + float(w3.from_wei(random.uniform(0.000065, 0.00007), "ether"))
    elif network in ["Ethereum", "Avalanche"] or (network in chains and chains[network].get("tx_type") == "legacy"):
        total_cost = float(value) + float(w3.from_wei(21000 * w3.eth.gas_price, "ether"))

    if total_cost > balance_native:
        cprint(f"Баланс {wallet_index} кошелька меньше чем {total_cost} ETH (с учетом комиссии за газ). Перехожу к следующему кошельку.", "red")
        return
    else:
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)

        try:
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
            if receipt["status"] == 1:
                cprint(f">>>[{wallet_index}] {account.address} {native_amount} {native} отправлен успешно на {recipient}", "green")
                return receipt
            else:
                cprint(f">>>[{wallet_index}] {account.address} Transaction Failed (статус: {receipt['status']})", "red")
                return None
        except Exception as e:
            cprint(f">>>[{wallet_index}] {account.address} Произошла ошибка при отправке {native_amount} {native}: {str(e)}", "red")
            return None

def main():
    cprint(belomordao, "cyan")
    cprint('Native-Sender запущен...', "magenta")
    print(f'\nСеть: {network}')
    print(f'Mode: {mode}')
    print(f'Shuffle: {shuffle}\n')
    time.sleep(5)

    if not private_keys:
        cprint("Отсутствуют приватные ключи. Завершаю работу.", "red")
        return

    if shuffle:
        random.shuffle(numbered_private_keys)

    for _, private_key in numbered_private_keys:
        recipient = wallet_pair[private_key]
        wallet_index = next(index for index, (_, key) in enumerate(original_private_keys, start=1) if key == private_key)

        try:
            transfer(private_key, wallet_index, recipient)
        except Exception as e:
            cprint(f">>>[{wallet_index}] Произошла ошибка: {str(e)}", "red")

        delay = random.randint(min_delay, max_delay)
        cprint(f"Ожидание {delay} секунд перед следующим кошельком...", "yellow")
        time.sleep(delay)

    cprint("\nNative-Sender завершен.\n", "magenta")

if __name__ == "__main__":
    if len(recipients) != len(private_keys):
        cprint("Количество адресов не соответствует количеству приватных ключей. Завершаю работу...", "red")
    main()