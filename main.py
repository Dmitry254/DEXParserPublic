from datetime import datetime

from tg_bot import message, send_text_message
from base_func import get_data
from web3_trans import contract_address
from web3_trans import set_wss_web3, set_http_web3, get_contract
from contracts_dict import contract_stable, contracts_info


def get_summary():
    url = f"https://api.pancakeswap.info/api/v2/summary"
    data = get_data(url)
    print(data)


def parse_trans():
    compare_prices(pancake_last_prices, biswap_last_prices, apeswap_last_prices)
    block = web3.eth.getBlock(web3.eth.defaultBlock, full_transactions=True)
    for trans in block.transactions:
        if trans.to == "0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8":
            biswap_parse(trans)
        elif trans.to == "0x10ED43C718714eb63d5aA57B78B54704E256024E":
            pancake_parse(trans)
        if trans.to == "0xcF0feBd3f17CEf5b47b0cD257aCf6025c5BFf3b7":
            apeswap_parse(trans)


def compare_prices(pancake_last_prices, biswap_last_prices, apeswap_last_prices):
    global profit_list
    # print(pancake_last_prices)
    # print(biswap_last_prices)
    # print(apeswap_last_prices)
    for deal_type in ["buy", "sell"]:
        if deal_type == "buy":
            other_deal_type = "sell"
        else:
            other_deal_type = "buy"
        if pancake_last_prices[deal_type]:
            for token_contract in pancake_last_prices[deal_type].keys():
                buy_price = []
                sell_price = []
                compare_result = f"{token_contract}\n"
                try:
                    pancake_token_price = pancake_last_prices[deal_type][token_contract][0]
                    pancake_time_price = pancake_last_prices[deal_type][token_contract][1].strftime('%H:%M')
                    pancake_stable_token = pancake_last_prices[deal_type][token_contract][4]
                    if deal_type == "buy":
                        compare_result += f"Pancake - {'{:.5f}'.format(pancake_token_price)} в {pancake_time_price}\n"
                        buy_price.append([pancake_token_price, "pancake", pancake_stable_token])
                    else:
                        compare_result += f"Pancake - {'{:.5f}'.format(pancake_token_price)} ({'{:.5f}'.format(pancake_last_prices[deal_type][token_contract][2])}) в {pancake_time_price}\n"
                        sell_price.append([pancake_token_price, "pancake", pancake_stable_token])
                except KeyError:
                    pass
                try:
                    biswap_token_price = biswap_last_prices[other_deal_type][token_contract][0]
                    biswap_time_price = biswap_last_prices[other_deal_type][token_contract][1].strftime('%H:%M')
                    biswap_stable_token = biswap_last_prices[other_deal_type][token_contract][4]
                    if other_deal_type == "buy":
                        compare_result += f"Biswap - {'{:.5f}'.format(biswap_token_price)} в {biswap_time_price}\n"
                        buy_price.append([biswap_token_price, "biswap", biswap_stable_token])
                    else:
                        compare_result += f"Biswap - {'{:.5f}'.format(biswap_token_price)} ({'{:.5f}'.format(biswap_last_prices[other_deal_type][token_contract][2])}) в {biswap_time_price}\n"
                        sell_price.append([biswap_token_price, "biswap", biswap_stable_token])
                except KeyError:
                    pass
                try:
                    apeswap_token_price = apeswap_last_prices[other_deal_type][token_contract][0]
                    apeswap_time_price = apeswap_last_prices[other_deal_type][token_contract][1].strftime('%H:%M')
                    apeswap_stable_token = apeswap_last_prices[other_deal_type][token_contract][4]
                    if other_deal_type == "buy":
                        compare_result += f"Apeswap - {'{:.5f}'.format(apeswap_token_price)} в {apeswap_time_price}\n"
                        buy_price.append([apeswap_token_price, "apeswap", apeswap_stable_token])
                    else:
                        compare_result += f"Apeswap - {'{:.5f}'.format(apeswap_token_price)} ({'{:.5f}'.format(apeswap_last_prices[other_deal_type][token_contract][2])}) в {apeswap_time_price}\n"
                        sell_price.append([apeswap_token_price, "apeswap", apeswap_stable_token])
                except KeyError:
                    pass
                if buy_price and sell_price:
                    buy_price = (sorted(buy_price, key=lambda x:x[0]))[0]
                    sell_price = (sorted(sell_price, key=lambda x:x[0]))[-1]
                    profit = (sell_price[0] / buy_price[0] - 1) * 100
                    if 10 > profit > 1:
                        if profit not in profit_list:
                            dex_links = create_links(token_contract, buy_price[2], sell_price[2], buy_price[1], sell_price[1])
                            compare_result += f"Прибыль {'{:.4f}'.format(profit)}%\n"
                            compare_result += f"{dex_links}\n"
                            compare_result += f"{pancake_last_prices[deal_type][token_contract][3]}"
                            # symbol = get_contract_info(token_contract)
                            # compare_result.replace(token_contract, symbol)
                            profit_list.append(profit)
                            send_text_message(message, compare_result)


def pancake_parse(trans):
    global pancake_last_prices
    stable_token, other_token, token_price, sell_token_price, deal_type = trans_info_handling(trans)
    if token_price:
        if deal_type == "buy":
            pancake_last_prices['buy'].update({other_token: [token_price, datetime.now(), 0, trans.hash.hex(), stable_token]})
        else:
            pancake_last_prices['sell'].update({other_token: [token_price, datetime.now(), sell_token_price, trans.hash.hex(), stable_token]})


def biswap_parse(trans):
    global biswap_last_prices
    stable_token, other_token, token_price, sell_token_price, deal_type = trans_info_handling(trans)
    if token_price:
        if deal_type == "buy":
            biswap_last_prices['buy'].update({other_token: [token_price, datetime.now(), 0, trans.hash.hex(), stable_token]})
        else:
            biswap_last_prices['sell'].update({other_token: [token_price, datetime.now(), sell_token_price, trans.hash.hex(), stable_token]})


def apeswap_parse(trans):
    global apeswap_last_prices
    stable_token, other_token, token_price, sell_token_price, deal_type = trans_info_handling(trans)
    if token_price:
        if deal_type == "buy":
            apeswap_last_prices['buy'].update({other_token: [token_price, datetime.now(), 0, trans.hash.hex(), stable_token]})
        else:
            apeswap_last_prices['sell'].update({other_token: [token_price, datetime.now(), sell_token_price, trans.hash.hex(), stable_token]})


def trans_info_handling(trans):
    try:
        amountIn = amountOut = 1
        if "0x38ed1739" in trans.input:  # swapExactTokensForTokens
            func_obj, func_params = pancake_contract.decode_function_input(trans.input)
            logs = web3.eth.get_transaction_receipt(trans.hash).logs
            for log in logs:
                if log.topics[0].hex() == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef":
                    if log.topics[1].hex()[26:] == dict(trans)['from'].lower()[2:]:
                        amountIn = int(log.data[2:], 16)
                    if log.topics[2].hex()[26:] == dict(trans)['from'].lower()[2:]:
                        amountOut = int(log.data[2:], 16)
            if func_params['path'][0] in contract_stable:
                token_price = amountIn / amountOut
                stable_token = func_params['path'][0]
                other_token = func_params['path'][-1]
            elif func_params['path'][-1] in contract_stable:
                token_price = amountOut / amountIn
                stable_token = func_params['path'][-1]
                other_token = func_params['path'][0]
            else:
                return 0, 0, 0, 0, 0
            return stable_token, other_token, token_price, 0, "buy"
        if "0x8803dbee" in trans.input:  # swapTokensForExactTokens
            func_obj, func_params = pancake_contract.decode_function_input(trans.input)
            logs = web3.eth.get_transaction_receipt(trans.hash).logs
            for log in logs:
                if log.topics[0].hex() == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef":
                    if log.topics[1].hex()[26:] == dict(trans)['from'].lower()[2:]:
                        amountIn = int(log.data[2:], 16)
                    if log.topics[2].hex()[26:] == dict(trans)['from'].lower()[2:]:
                        amountOut = int(log.data[2:], 16)
            if func_params['path'][0] in contract_stable:
                token_price = amountIn / amountOut
                sell_token_price = func_params['amountOut'] / func_params['amountInMax']
                stable_token = func_params['path'][0]
                other_token = func_params['path'][-1]
            elif func_params['path'][-1] in contract_stable:
                token_price = amountOut / amountIn
                sell_token_price = func_params['amountInMax'] / func_params['amountOut']
                stable_token = func_params['path'][-1]
                other_token = func_params['path'][0]
            else:
                return 0, 0, 0, 0, 0
            return stable_token, other_token, token_price, sell_token_price, "sell"
        return 0, 0, 0, 0, 0
    except ZeroDivisionError:
        return 0, 0, 0, 0, 0


def create_links(token_contract, buy_contract, sell_contract, buy_dex, sell_dex):
    dex_links = "Покупка "
    if buy_dex == "pancake":
        url = f"https://pancakeswap.finance/swap?outputCurrency={token_contract}&inputCurrency={buy_contract}"
        dex_links += f"[pancake]({url}), продажа "
        if sell_dex == "biswap":
            url = f"https://exchange.biswap.org/#/swap?outputCurrency={sell_contract}&inputCurrency={token_contract}"
            dex_links += f"[biswap]({url})"
        elif sell_dex == "apeswap":
            url = f"https://apeswap.finance/swap?outputCurrency={sell_contract}&inputCurrency={token_contract}"
            dex_links += f"[apeswap]({url})"
    elif buy_dex == "biswap":
        url = f"https://exchange.biswap.org/#/swap?outputCurrency={token_contract}&inputCurrency={buy_contract}"
        dex_links += f"[biswap]({url}), продажа "
        if sell_dex == "pancake":
            url = f"https://pancakeswap.finance/swap?outputCurrency={sell_contract}&inputCurrency={token_contract}"
            dex_links += f"[pancake]({url})"
        elif sell_dex == "apeswap":
            url = f"https://apeswap.finance/swap?outputCurrency={sell_contract}&inputCurrency={token_contract}"
            dex_links += f"[apeswap]({url})"
    elif buy_dex == "apeswap":
        url = f"https://apeswap.finance/swap?outputCurrency={token_contract}&inputCurrency={buy_contract}"
        dex_links += f"[apeswap]({url}), продажа "
        if sell_dex == "pancake":
            url = f"https://pancakeswap.finance/swap?outputCurrency={sell_contract}&inputCurrency={token_contract}"
            dex_links += f"[pancake]({url})"
        elif sell_dex == "biswap":
            url = f"https://exchange.biswap.org/#/swap?outputCurrency={sell_contract}&inputCurrency={token_contract}"
            dex_links += f"[biswap]({url})"
    return dex_links


def get_contract_info(contract_address):
    contract_info = get_contract(web3, contract_address)
    # decimals = contract_info.functions.decimals().call()
    symbol = contract_info.functions.symbol().call()
    return symbol


def create_dict(dex_dicts):
    for dex_dict in dex_dicts:
        dex_dict.update({"buy": {}, "sell": {}})
    print(dex_dicts)
    return dex_dicts


if __name__ == "__main__":
    dex_dicts = [{}, {}, {}]
    pancake_last_prices, biswap_last_prices, apeswap_last_prices = create_dict(dex_dicts)
    profit_list = []
    pancake_contract_address = ""
    buy_contract = ""
    token_contract = ""
    web3 = set_http_web3()
    pancake_contract = get_contract(web3, pancake_contract_address)
    while True:
        parse_trans()
