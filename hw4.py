from typing import List, Set, Dict, Optional


class Transaction:
    def __init__(self, buyer_id: str, seller_id: str, amount: int, price: int):
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.amount = amount
        self.price = price


class Order:
    def __init__(self, trader_id: str, amount: int, price: int):
        self.trader_id = trader_id
        self.amount = amount
        self.price = price


class Stock:
    def __init__(self) -> None:
        self.history: List[Transaction] = []
        self.buyers: List[Order] = []
        self.sellers: List[Order] = []


StockExchange = Dict[str, Stock]


def add_new_stock(stock_exchange: StockExchange, ticker_symbol: str) -> bool:
    if ticker_symbol not in stock_exchange:
        data = Stock()
        stock_exchange[ticker_symbol] = data
        return True
    return False


def add_new_orders(new_order: Order, traders: List[Order], buy: bool) -> None:
    mode = 1 if buy else -1
    if not traders:
        traders.append(new_order)
        return
    for index, order in enumerate(traders):
        if order.price * mode >= new_order.price * mode:
            traders.insert(index, new_order)
            return
    traders.append(new_order)


def trade(new_order: Order, last: Order, sellers: List[Order],
          history: List[Transaction]) -> None:
    difference = new_order.amount - last.amount
    minimum = min(new_order.amount, last.amount)

    if difference < 0:
        last.amount = abs(difference)
        sellers.append(last)
        new_order.amount = 0
    elif difference >= 0:
        new_order.amount = difference
    history.append(Transaction(buyer_id=new_order.trader_id,
                               seller_id=last.trader_id,
                               amount=minimum, price=last.price))


def settle_buy_order(new_order: Order, buyers: List[Order],
                     sellers: List[Order],
                     history: List[Transaction], buy: bool) -> None:
    mode = 1 if buy else -1
    last = sellers[-1]
    while new_order.amount > 0 and last.price * mode <= new_order.price * mode:
        last = sellers.pop()
        trade(new_order, last, sellers, history)
        if len(sellers) == 0:
            break
        last = sellers[-1]

    if new_order.amount > 0:
        add_new_orders(new_order, buyers, buy)
    return


def place_buy_order(stock_exchange: StockExchange, ticker_symbol: str,
                    trader_id: str, amount: int, price: int,
                    buy: bool = True) -> None:
    stock = stock_exchange[ticker_symbol]
    new_order = Order(trader_id, amount, price)

    if buy:
        if len(stock.sellers) == 0:
            add_new_orders(new_order, stock.buyers, buy=True)
        else:
            settle_buy_order(new_order, stock.buyers,
                             stock.sellers, stock.history, buy=True)
    else:
        if len(stock.buyers) == 0:
            add_new_orders(new_order, stock.sellers, buy=False)
        else:
            settle_buy_order(new_order, stock.sellers,
                             stock.buyers, stock.history, buy=False)


def place_sell_order(stock_exchange: StockExchange, ticker_symbol: str,
                     trader_id: str, amount: int, price: int) -> None:
    place_buy_order(stock_exchange, ticker_symbol,
                    trader_id, amount, price, buy=False)


def stock_owned(stock_exchange: StockExchange, trader_id: str) \
        -> Dict[str, int]:
    pass  # TODO


def all_traders(stock_exchange: StockExchange) -> Set[str]:
    pass  # TODO


def transactions_by_amount(stock_exchange: StockExchange,
                           ticker_symbol: str) -> List[Transaction]:
    pass  # TODO


def process_batch_commands(stock_exchange: StockExchange,
                           commands: List[str]) -> Optional[int]:
    pass  # TODO


def print_stock(stock_exchange: StockExchange, ticker_symbol: str) -> None:
    assert ticker_symbol in stock_exchange

    stock = stock_exchange[ticker_symbol]
    print(f"=== {ticker_symbol} ===")
    print("     price amount  trader")
    print("  -------------------------------------------------------------")

    for order in stock.sellers:
        print(f"    {order.price:6d} {order.amount:6d} ({order.trader_id})")
    print("  -------------------------------------------------------------")

    for order in reversed(stock.buyers):
        print(f"    {order.price:6d} {order.amount:6d} ({order.trader_id})")
    print("  -------------------------------------------------------------")

    for transaction in stock.history:
        print(f"    {transaction.seller_id} -> {transaction.buyer_id}: "
              f"{transaction.amount} at {transaction.price}")


def check_order(order: Order, trader_id: str, amount: int, price: int) -> None:
    assert order.trader_id == trader_id
    assert order.amount == amount
    assert order.price == price


def check_transaction(transaction: Transaction, buyer_id: str, seller_id: str,
                      amount: int, price: int) -> None:
    assert transaction.buyer_id == buyer_id
    assert transaction.seller_id == seller_id
    assert transaction.amount == amount
    assert transaction.price == price


def test_scenario1() -> None:
    duckburg_se: StockExchange = {}
    add_new_stock(duckburg_se, 'ACME')

    place_sell_order(duckburg_se, 'ACME', 'Strýček Skrblík', 50, 120)
    place_buy_order(duckburg_se, 'ACME', 'Rampa McKvák', 100, 90)
    place_sell_order(duckburg_se, 'ACME', 'Hamoun Držgrešle', 70, 110)
    place_sell_order(duckburg_se, 'ACME', 'Kačer Donald', 20, 120)

    acme = duckburg_se['ACME']
    assert acme.history == []

    assert len(acme.buyers) == 1
    check_order(acme.buyers[0], 'Rampa McKvák', 100, 90)
    print_stock(duckburg_se, 'ACME')
    assert len(acme.sellers) == 3
    check_order(acme.sellers[0], 'Kačer Donald', 20, 120)
    check_order(acme.sellers[1], 'Strýček Skrblík', 50, 120)
    check_order(acme.sellers[2], 'Hamoun Držgrešle', 70, 110)

    place_buy_order(duckburg_se, 'ACME', 'Paní Čvachtová', 90, 110)

    assert len(acme.history) == 1
    check_transaction(acme.history[0], 'Paní Čvachtová', 'Hamoun Držgrešle',
                      70, 110)
    print_stock(duckburg_se, 'ACME')
    assert len(acme.buyers) == 2
    check_order(acme.buyers[0], 'Rampa McKvák', 100, 90)
    check_order(acme.buyers[1], 'Paní Čvachtová', 20, 110)

    assert len(acme.sellers) == 2
    check_order(acme.sellers[0], 'Kačer Donald', 20, 120)
    check_order(acme.sellers[1], 'Strýček Skrblík', 50, 120)

    place_buy_order(duckburg_se, 'ACME', 'Magika von Čáry', 60, 130)

    assert len(acme.history) == 3
    check_transaction(acme.history[0], 'Paní Čvachtová', 'Hamoun Držgrešle',
                      70, 110)
    check_transaction(acme.history[1], 'Magika von Čáry', 'Strýček Skrblík',
                      50, 120)
    check_transaction(acme.history[2], 'Magika von Čáry', 'Kačer Donald',
                      10, 120)

    assert len(acme.buyers) == 2
    check_order(acme.buyers[0], 'Rampa McKvák', 100, 90)
    check_order(acme.buyers[1], 'Paní Čvachtová', 20, 110)

    assert len(acme.sellers) == 1
    check_order(acme.sellers[0], 'Kačer Donald', 10, 120)

    for name, amount in [
            ('Kačer Donald', -10),
            ('Strýček Skrblík', -50),
            ('Hamoun Držgrešle', -70),
            ('Paní Čvachtová', 70),
            ('Magika von Čáry', 60),
    ]:
        assert stock_owned(duckburg_se, name) == {'ACME': amount}

        assert stock_owned(duckburg_se, 'Rampa McKvák') == {}
        assert stock_owned(duckburg_se, 'Šikula') == {}

        assert all_traders(duckburg_se) == {
            'Kačer Donald',
            'Strýček Skrblík',
            'Hamoun Držgrešle',
            'Paní Čvachtová',
            'Magika von Čáry',
            'Rampa McKvák',
        }

        all_transactions = transactions_by_amount(duckburg_se, 'ACME')
        check_transaction(all_transactions[0],
                          'Paní Čvachtová', 'Hamoun Držgrešle',
                          70, 110)
        check_transaction(all_transactions[1],
                          'Magika von Čáry', 'Strýček Skrblík',
                          50, 120)
        check_transaction(all_transactions[2],
                          'Magika von Čáry', 'Kačer Donald',
                          10, 120)


def test_scenario2() -> None:
    duckburg_se: StockExchange = {}
    result = process_batch_commands(duckburg_se, [
        "ADD ACME",
        "Uncle Scrooge: SELL 50 ACME AT 120",
        "Launchpad McQuack: BUY 100 ACME AT 90",
        "Flintheart Glomgold: SELL 70 ACME AT 110",
        "Donald Duck: SELL 20 ACME AT 120",
        "Mrs. Beakley: BUY 90 ACME AT 110",
        "Magica De Spell: BUY 60 ACME AT 130",
    ])
    assert result is None
    assert 'ACME' in duckburg_se
    acme = duckburg_se['ACME']

    assert len(acme.history) == 3
    check_transaction(acme.history[0], 'Mrs. Beakley', 'Flintheart Glomgold',
                      70, 110)
    check_transaction(acme.history[1], 'Magica De Spell', 'Uncle Scrooge',
                      50, 120)
    check_transaction(acme.history[2], 'Magica De Spell', 'Donald Duck',
                      10, 120)

    assert len(acme.buyers) == 2
    check_order(acme.buyers[0], 'Launchpad McQuack', 100, 90)
    check_order(acme.buyers[1], 'Mrs. Beakley', 20, 110)

    assert len(acme.sellers) == 1
    check_order(acme.sellers[0], 'Donald Duck', 10, 120)


def test_scenario3() -> None:
    nnyse: StockExchange = {}
    result = process_batch_commands(nnyse, [
        "ADD Momcorp",
        "Mom: SELL 1000 Momcorp AT 5000",
        "Walt: BUY 10 Momcorp AT 5600",
        "Larry: BUY 7 Momcorp AT 5000",
        "Igner: BUY 1 Momcorp AT 4000",
        "ADD PlanetExpress",
        "Mom: BUY 1000 PlanetExpress AT 100",
        "Zoidberg: BUY 1000 PlanetExpress AT 199",
        "Professor Farnsworth: SELL 1020 PlanetExpress AT 100",
        "Bender B. Rodriguez: BUY 20 Momcorp AT 100",
        "Fry: INVALID COMMAND",
        "Leela: BUY 500 PlanetExpress AT 150",
    ])

    assert result == 10

    assert set(nnyse) == {'Momcorp', 'PlanetExpress'}

    momcorp = nnyse['Momcorp']
    pe = nnyse['PlanetExpress']

    assert len(momcorp.history) == 2
    check_transaction(momcorp.history[0], 'Walt', 'Mom', 10, 5000)
    check_transaction(momcorp.history[1], 'Larry', 'Mom', 7, 5000)

    assert len(momcorp.sellers) == 1
    check_order(momcorp.sellers[0], 'Mom', 983, 5000)

    assert len(momcorp.buyers) == 2
    check_order(momcorp.buyers[0], 'Bender B. Rodriguez', 20, 100)
    check_order(momcorp.buyers[1], 'Igner', 1, 4000)

    assert len(pe.history) == 2
    check_transaction(pe.history[0], 'Zoidberg', 'Professor Farnsworth',
                      1000, 199)
    check_transaction(pe.history[1], 'Mom', 'Professor Farnsworth',
                      20, 100)

    assert pe.sellers == []
    assert len(pe.buyers) == 1
    check_order(pe.buyers[0], 'Mom', 980, 100)


if __name__ == '__main__':
    test_scenario1()
    test_scenario2()
    test_scenario3()
