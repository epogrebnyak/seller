"""FIFO-based inventory tracking system.

from seller import Seller

i = Seller()
pen = i.register("Pen")
i.buy(pen @ 0.55 * 100)
i.buy(pen @ 0.65 * 100)
i.sell(pen @ 1.05 * 151)
print(i.earned)               # 70.4 = (1.05-0.55) * 100 + (1.05-0.65) * 51
print(i.hold[pen].quantity)   # 50
"""

from dataclasses import dataclass, field
from collections import UserDict, deque
from abc import ABC

from primitives import UUID, Item, Order, Parcel, Expense
from stack import Batch, Stack


class Catalog(UserDict):
    """A catalog to register and track items."""

    def issue_code(self, n_chars):
        """Generate a unique code for catalog items."""
        code = UUID(n_chars).new()
        while code in self.data:  # will exhaust on small n_chars
            code = UUID(n_chars).new()
        return code

    def register(self, description, code=None, n_chars=4) -> Item:
        """Register a new item in the catalog."""
        if not code or code in self.data:
            code = self.issue_code(n_chars)
        self.data[code] = description
        return Item(code)


class SellerException(Exception):
    """Base exception for Seller-related errors."""


class NotInStock(SellerException):
    """Raised when attempting to sell an item not in stock."""


class InsufficientStock(SellerException):
    """Raised when attempting to sell more items than are in stock."""


class InsufficientFunds(SellerException):
    """Raised when attempting to spend more cash than available."""


@dataclass
class Inventory(ABC):
    """Abstract base class for inventory management."""

    data: dict[str, deque[Batch]] = field(default_factory=dict)

    def __getitem__(self, item: str | Item) -> deque[Batch]:
        """Get the stack of batches for an item."""
        if isinstance(item, Item):
            item = item.name
        return self.data[item]

    def add(self, name, batch: Batch):
        """Purchase items to add to inventory."""
        return self._add(name, batch)

    def _add(self, name, batch: Batch):
        """Helper method to add a batch to inventory."""
        if name not in self.data:
            self.data[name] = deque()
        self.data[name].append(batch)
        return self

    def assert_available(self, order: Order) -> None:
        """Check if items are available for sale."""
        name = order.name
        if name not in self.data:
            raise NotInStock(f"Item not in stock: {name}")
        if Stack(self.data[name]).quantity < order.quantity:
            raise InsufficientStock(f"Insufficient stock for item: {name}")

    def to_parcel(self, order: Order, batches: list[Batch]) -> Parcel:
        """Convert a Order order and its batches to a Parcel."""
        p = Parcel(order.name, order.price)
        p.batches.extend(batches)
        return p

    def pop(self, order: Order):
        """Move items using FIFO method."""
        self.assert_available(order)
        stack = Stack(self.data[order.name])
        result = stack.take_first(order.quantity)
        self.data[order.name] = stack.batches
        return self.to_parcel(order, result)

    @property
    def worth(self):
        """Calculate total worth of inventory."""
        return sum(Stack(self.data[key]).worth for key in self.data.keys())


class InventoryFIFO(Inventory):
    """Manages inventory using FIFO method."""


class InventoryLIFO(Inventory):
    """Manages inventory using FIFO method."""

    def pop(self, order: Order):
        """Move items using LIFO method."""
        self.assert_available(order)
        stack = Stack(self.data[order.name])
        result = stack.take_last(order.quantity)
        self.data[order.name] = stack.batches
        return self.to_parcel(order, result)


class InventoryWA(Inventory):
    """Manages inventory using weighted average method."""

    def add(self, name, batch: Batch):
        """Purchase items to add to inventory."""
        self._add(name, batch)
        s = Stack(self.data[name]).equalize_prices()
        self.data[name] = s.batches
        return self


@dataclass
class Seller:
    """Manage buy and sell operations."""

    cash: float = 0.0
    hold: Inventory = field(default_factory=InventoryFIFO)
    fulfilled: list[Parcel] = field(default_factory=list)
    paid: list[Expense] = field(default_factory=list)
    _catalog: Catalog = field(default_factory=Catalog)

    @property
    def sales(self) -> list[Order]:
        """Get all sales transactions."""
        return [parcel.to_order() for parcel in self.fulfilled]

    @property
    def revenue(self):
        """Calculate total revenue."""
        return sum(s.worth for s in self.sales)

    @property
    def cogs(self):
        """Calculate total cost of items sold."""
        return sum(parcel.cogs for parcel in self.fulfilled)

    @property
    def gross_margin(self):
        """Calculate gross margin (revenue minus COGS)."""
        return self.revenue - self.cogs

    @property
    def expenses(self):
        """Calculate total expenses."""
        return sum(e.amount for e in self.paid)

    @property
    def earned(self):
        """Calculate net earnings (gross margin - expenses)."""
        return self.gross_margin - self.expenses

    def register(self, description, code=None, n_chars=4) -> Item:
        """Register a new item in the catalog."""
        return self._catalog.register(description, code, n_chars)

    def _deduct_cash(self, amount: float):
        """Deduct cash from the seller's balance."""
        if amount > self.cash:
            raise InsufficientFunds("Insufficient cash to complete transaction.")
        self.cash -= amount
        return self

    def pay(self, amount, text):
        """Record an expense."""
        self._deduct_cash(amount)
        self.paid.append(Expense(amount, text))
        return self

    def buy(self, order: Order):
        """Purchase items to add to inventory."""
        self._deduct_cash(order.worth)
        self.hold.add(order.name, order.batch)
        return self

    def sell(self, order: Order):
        """Sell items from inventory."""
        parcel = self.hold.pop(order)
        self.fulfilled.append(parcel)
        self.cash += order.worth
        return self
