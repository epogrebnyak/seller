"""FIFO-based inventory tracking system.

from seller import Seller

i = Seller(cash=200)
pen = i.register("Pen")
i.buy(pen @ 0.55 * 100)
i.buy(pen @ 0.65 * 100)
i.sell(pen @ 1.05 * 151)
print(i.cash)
print(i.earned)
"""

from dataclasses import dataclass, field
from collections import UserDict
from abc import ABC, abstractmethod

from primitives import UUID, Item, Order, Parcel, Expense, Batch


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


class NoFunds(SellerException):
    """Raised when attempting to spend more cash than available."""


@dataclass
class Inventory(ABC):
    """Abstract base class for inventory management."""

    data: dict[str, list[Batch]] = field(default_factory=dict)

    def __getitem__(self, item: str | Item) -> list[Batch]:
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
            self.data[name] = []
        self.data[name].append(batch)
        return self

    def assert_available(self, order: Order) -> None:
        """Check if items are available for sale."""
        name = order.name
        if name not in self.data:
            raise NotInStock(f"Item not in stock: {name}")
        if sum(b.quantity for b in self.data[name]) < order.quantity:
            raise InsufficientStock(f"Insufficient stock for item: {name}")


    @abstractmethod
    def pop(self, order: Order) -> Parcel:
        """Move items."""

    def _pop(self, order: Order, method):
        """Move items using FIFO method."""
        self.assert_available(order)
        self.data[order.name], out = method(self.data[order.name], order.quantity)
        p = Parcel(order.name, order.price)
        p.batches.extend(out)
        return p

    @property
    def worth(self):
        """Calculate total worth of inventory."""
        return sum(
            batch.purchase_price * batch.quantity
            for batches in self.data.values()
            for batch in batches
        )


class InventoryFIFO(Inventory):
    """Manages inventory using FIFO method."""

    def pop(self, order: Order):
        """Move items using FIFO method."""
        return self._pop(order, take_fifo)


class InventoryLIFO(Inventory):
    """Manages inventory using FIFO method."""

    def pop(self, order: Order):
        """Move items using FIFO method."""
        return self._pop(order, take_lifo)
    
class InventoryWA(Inventory):
    """Manages inventory using weighted average method."""

    def pop(self, order: Order):
        """Move items using FIFO method."""
        return self._pop(order, take_fifo)


    def add(self, name, batch: Batch):
        """Purchase items to add to inventory."""
        self._add(name, batch)
        equalize_prices(self.data[name])
        return self

def equalize_prices(batches):
    """Set all batches purchase price to the same averaged price."""
    total_quantity = sum(batch.quantity for batch in batches)
    if total_quantity == 0:
        return batches
    total_worth = sum(batch.purchase_price * batch.quantity for batch in batches)
    average_price = total_worth / total_quantity
    for batch in batches:
        batch.purchase_price = average_price
    return batches

def take_lifo(
    batches: list[Batch],
    quantity: int | float,
) -> tuple[list[Batch], list[Batch]]:
    out, taken = take_fifo(list(reversed(batches)), quantity)
    return list(reversed(out)), taken

def take_fifo(
    batches: list[Batch],
    quantity: int | float,
) -> tuple[list[Batch], list[Batch]]:
    """Take batches of items from the inventory."""
    taken = []
    while quantity > 0 and batches:
        current_batch = batches[0]
        if current_batch.quantity <= quantity:
            taken.append(current_batch)
            quantity -= current_batch.quantity
            batches.pop(0)
        else:
            partial_batch = Batch(current_batch.purchase_price, quantity)
            taken.append(partial_batch)
            current_batch.quantity -= quantity
            break
    return batches, taken


@dataclass
class Seller:
    """Manage buy and sell operations."""

    cash: float = 0.0
    inventory: Inventory = field(default_factory=InventoryFIFO)
    fulfilled: list[Parcel] = field(default_factory=list)
    paid: list[Expense] = field(default_factory=list)
    catalog: Catalog = field(default_factory=Catalog)

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
        return self.catalog.register(description, code, n_chars)

    def _deduct_cash(self, amount: float):
        """Deduct cash from the seller's balance."""
        if amount > self.cash:
            raise NoFunds("Insufficient cash to complete transaction.")
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
        self.inventory.add(order.name, order.batch)
        return self

    def sell(self, order: Order):
        """Sell items from inventory."""
        parcel = self.inventory.pop(order)
        self.fulfilled.append(parcel)
        self.cash += order.worth
        return self
