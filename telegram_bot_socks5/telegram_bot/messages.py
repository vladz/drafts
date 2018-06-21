from decimal import Decimal

from dataclasses import dataclass


@dataclass
class OpenOrderMsg:
    order: int
    pair: str
    volume: str
    open_price: Decimal

    def __str__(self):
        return (f'Opened order {self.order}\n'
                f'Trading pair: {self.pair}\n'
                f'Order volume: {self.volume}\n'
                f'Open price: {self.open_price}')


@dataclass
class CloseOrderMsg:
    order: int
    pair: str
    volume: str
    open_price: Decimal
    close_price: Decimal
    pl: Decimal

    def __str__(self):
        return (f'Closed order {self.order}'
                f'Trading pair: {self.pair}'
                f'Order volume: {self.volume}'
                f'Open price: {self.open_price}'
                f'Close price: {self.close_price}'
                f'P/L: {self.pl}')


@dataclass
class TakeProfitMsg:
    order: int
    pair: str
    open_price: Decimal
    tp_price: Decimal
    pl: Decimal

    def __str__(self):
        return (f'Closed order {self.order}'
                f'Trading pair: {self.pair}'
                f'Open price: {self.open_price}'
                f'Close price: {self.tp_price}'
                f'P/L: {self.pl}')


msg_map = {
    'open_order': OpenOrderMsg,
    'close_order': CloseOrderMsg,
    'take_profit': TakeProfitMsg
}
