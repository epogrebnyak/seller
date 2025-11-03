"""FIFO-based inventory tracking system.

    i = Inventory()
    pen = Item("Pen")
    i.buy(pen @ 0.55 * 100)
    i.buy(pen @ 0.65 * 100)
    i.sell(pen @ 1.05 * 150)
    print(i.earned) # 70 = (1.05-0.55) * 100 + (1.05-0.65) * 50
    print(i.hold)   # {'Pen': [Batch(purchase_price=0.65, quantity=50)]}

"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid
from collections import UserDict


@dataclass
class Batch:
    """A batch of items purchased at the same price."""
    purchase_price: float
    quantity: int | float


def issue_uuid(n_chars: int = 36):
    """Generate a unique identifier string."""
    n_chars = min(n_chars, 36)
    return str(uuid.uuid4())[:n_chars]


# not used
@dataclass
class Stamp:
    time: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: issue_uuid(8))


@dataclass
class Item:
    """Represents an item in inventory."""
    name: str

    def __matmul__(self, price):
        """Set the price using @ operator."""
        return Sale(self.name, price, 0)

    def __mul__(self, q):
        """Set the quantity using * operator."""
        return Sale(self.name, 0, q)


@dataclass
class Sale:
    """Represents a sale transaction."""
    name: str
    price: float
    quantity: int | float

    @property
    def revenue(self):
        """Calculate total revenue from this sale."""
        return self.price * self.quantity

    def __matmul__(self, price):
        """Set the price using @ operator."""
        self.price = price
        return self

    def __mul__(self, q):
        """Set the quantity using * operator."""
        self.quantity = q
        return self

    @property
    def batch(self):
        """Convert to a Batch object."""
        return Batch(self.price, self.quantity)


@dataclass
class Parcel:
    """A unit of fulfillment that keeps track of batches used."""

    name: str
    price: float
    batches: list[Batch] = field(default_factory=list)

    @property
    def cogs(self):
        """Calculate cost of goods sold for this parcel."""
        return sum(batch.purchase_price * batch.quantity for batch in self.batches)

    @property
    def quantity(self):
        """Total quantity in the parcel."""
        return sum(batch.quantity for batch in self.batches)

    @property
    def sale(self):
        """Convert to a Sale object."""
        return Sale(self.name, self.price, self.quantity)

    def append(self, b: Batch):
        """Add a batch to the parcel."""
        self.batches.append(b)
        return self


@dataclass
class Expense:
    """Represents an expense incurred."""
    amount: float
    description: str


class Catalog(UserDict):
    """A catalog to register and track items."""
    
    def issue_code(self, n_chars):
        """Generate a unique code for catalog items."""
        code = issue_uuid(n_chars)
        while code in self.data:
            code = issue_uuid(n_chars)
            # raise error if not found after 10 attempts
        return code

    def register(self, description, code=None, n_chars=4) -> Item:
        """Register a new item in the catalog."""
        if not code or code in self.data:
            code = self.issue_code(n_chars)
        self.data[code] = description
        return Item(code)


@dataclass
class Inventory:
    """Manages inventory using FIFO method."""
    hold: dict[str, list[Batch]] = field(default_factory=dict)
    fulfilled: list[Parcel] = field(default_factory=list)
    spent: list[Expense] = field(default_factory=list)
    catalog: Catalog = field(default_factory=Catalog)

    @property
    def sales(self):
        """Get all sales transactions."""
        return [parcel.sale for parcel in self.fulfilled]

    @property
    def revenue(self):
        """Calculate total revenue from all sales."""
        return sum(s.revenue for s in self.sales)

    @property
    def cogs(self):
        """Calculate total cost of goods sold."""
        return sum(parcel.cogs for parcel in self.fulfilled)

    @property
    def gross_margin(self):
        """Calculate gross margin (revenue minus COGS)."""
        return self.revenue - self.cogs

    @property
    def expenses(self):
        """Calculate total expenses."""
        return sum(e.amount for e in self.spent)

    @property
    def earned(self):
        """Calculate net earnings (gross margin - expenses)."""
        return self.gross_margin - self.expenses

    def pay(self, amount, text):
        """Record an expense."""
        self.spent.append(Expense(amount, text))
        return self

    def buy(self, item: Item) -> "Inventory":
        """Purchase items to add to inventory."""
        if item.name not in self.hold:
            self.hold[item.name] = []
        self.hold[item.name].append(item.batch)
        return self

    def total(self, name: str) -> float:
        """Get total quantity of an item in inventory."""
        if name not in self.hold or not self.hold[name]:
            return 0
        return sum(batch.quantity for batch in self.hold[name])

    def sell(self, order: Sale):
        """Sell items using FIFO method."""
        name = order.name
        if name not in self.hold or not self.hold[name]:
            return self
        if self.total(name) < order.quantity:
            return self
        remaining_quantity = order.quantity
        fulfillment = Parcel(order.name, order.price)
        while remaining_quantity > 0 and self.hold[name]:
            current_batch = self.hold[name][0]
            if current_batch.quantity <= remaining_quantity:
                fulfillment.append(current_batch)
                remaining_quantity -= current_batch.quantity
                self.hold[name].pop(0)
            else:
                partial_batch = Batch(current_batch.purchase_price, remaining_quantity)
                fulfillment.append(partial_batch)
                current_batch.quantity -= remaining_quantity
                break
        self.fulfilled.append(fulfillment)
        return self
