#!/usr/bin/python
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
import re

from typing import Optional, Dict, List, TypeVar


class Product:
    def __init__(self,name: str, price: float) -> None:
        """Inicjalizacja nazwa produktu name typu str i ceny produktu price float ."""
        pattern:str=r'^[a-zA-Z]+[0-9]+$'
        if re.fullmatch(pattern, name) is not None:
            self.name: str = name
            self.price: float = price
        else:
            raise ValueError
    def __eq__(self, other):
        return (self.price == other.price and self.name == other.name)

    def __hash__(self):
        return hash((self.name, self.price))

class ServerError(Exception):
    def __init__(self, msg:str = None):
        if msg is None: msg = 'Error occured with server'
        super().__init__(msg)

class TooManyProductsFoundError(ServerError):
    # Reprezentuje wyjątek związany ze znalezieniem zbyt dużej liczby produktów.
    def __init__(self):
        super().__init__(msg='Too many products found')

class Server(ABC):
    n_max_returned_entries: int = 3
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
    
    def get_entries(self, n_letters: int = 1) -> List[Product]:
        all_products: List[Product] = self.get_all_products()
        patt: str = '^[a-zA-Z]{' + str(n_letters) + '}\d{2,3}$'
        matched_products: List[Product] = [p for p in all_products if re.match(patt, p.name)]
        if len(matched_products) > Server.n_max_returned_entries:
            raise TooManyProductsFoundError
        return sorted(matched_products, key=lambda entry: entry.price)

    @abstractmethod
    def get_all_products():
        raise NotImplementedError

class ListServer(Server):
    def __init__(self, product: List[Product], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.product: List[Product] = product

    def get_all_products(self) -> List[Product]:
        return self.product


class MapServer(Server):
    def __init__(self, product: List[Product], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.product: Dict[str, Product] = {prod.name: prod for prod in product}

    def get_all_products(self) -> List[Product]:
        return list(self.product.values())


ServerType = TypeVar('ServerType', bound=Server)

class Client:
    def __init__(self, server: ServerType):
        self.server: ServerType = server

    def get_total_price(self, n_letters: Optional[int]) -> Optional[float]:
        try:
            products = self.server.get_entries(n_letters)
            if products: return sum(prod.price for prod in products)
            else: return None
        except TooManyProductsFoundError: return None
