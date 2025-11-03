"""FIFO-based inventory tracking system.

    i = Inventory()
    pen = Item("Pen")
    i.buy(pen @ 0.55 * 100)
    i.buy(pen @ 0.65 * 100)
    i.sell(pen @ 1.05 * 150)
    print(i.earned) # 70 = (1.05-0.55) * 100 + (1.05-0.65) * 50
    print(i.hold)   # {'Pen': [Batch(purchase_price=0.65, quantity=50)]}

Usage ideas:
- OOP concepts in Python (eg operator overloading)
- learn-as-you-code in the financial accounting doamin
- generate quizes for accounting and financial management  
- proofs and demos for policies (eg. FIFO vs LIFO vs. WA, amortization schedules)
- inventory optimisation / margin strategies demos (eg ABC)
- simulation and agents (eg can a LLM run the shop)
- generate synthetic data to match company reports (Tesco, Walmart, Amazon)
- apply as transactions ledger for equity trading
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


# Usage examples
if __name__ == "__main__":
    i = Inventory()
    t1 = Item("Popcorn")
    t2 = Item("Soda 330 ml")
    # Wholesale purchases
    i.buy(t1 @ 0.90 * 25)  # Premium popcorn
    i.buy(t1 @ 0.75 * 50)  # Bulk kernels
    i.buy(t2 @ 0.65 * 100)  # Wholesale soda
    assert i == Inventory(
        hold={
            "Popcorn": [
                Batch(purchase_price=0.9, quantity=25),
                Batch(purchase_price=0.75, quantity=50),
            ],
            "Soda 330 ml": [Batch(purchase_price=0.65, quantity=100)],
        },
        fulfilled=[],
    )
    # Retail sales
    i.sell(t1 @ 2.50 * 35)  # Movie-theater retail price
    i.sell(t2 @ 1.25 * 50)  # Off-the-shelf soda

    # Assert for revenue method
    expected_revenue = (35 * 2.50) + (50 * 1.25)
    assert abs(i.revenue - expected_revenue) < 0.001

    # Assert for cogs method
    # For t1: 25 units @ 0.90 + 10 units @ 0.75 = 22.5 + 7.5 = 30.0
    # For t2: 50 units @ 0.65 = 32.5
    expected_cogs = (25 * 0.90 + 10 * 0.75) + (50 * 0.65)
    assert abs(i.cogs - expected_cogs) < 0.001
    print(i.hold)
    print(i.sales)
    print(i.gross_margin)
    assert 87.5 == i.gross_margin

    # Amazon sample
    items = [
        Item(name) @ price
        for name, price in [
            ("Mug", 15.60),
            ("Brush", 8.16),
            ("Lexibook", 33.70),
            ("Xbox X 1TB", 648.00),
            ("Casio F-91W-1", 19.61),
        ]
    ]

    i = Inventory()
    pen = i.catalog.register(
        "BIC Gel-ocity Retractable Quick Dry Gel Pen, Medium Point (0.7mm), Blue"
    )
    i.buy(pen @ 0.55 * 100)
    i.buy(pen @ 0.65 * 80)
    i.buy(pen @ 0.50 * 20)
    i.sell(pen @ 1.05 * 150)
    i.pay(20, "selling expenses")
    i.pay(15, "overhead")
    print("Earned:", i.earned)
    # 35 = (1.05-0.55) * 100 + (1.05-0.65) * 50 - 20 - 15
    print("Inventory:", i.hold)
    # {'98fb': [Batch(purchase_price=0.65, quantity=30), Batch(purchase_price=0.5, quantity=20)]}
    print("Catalog:", i.catalog)
    # {'98fb': 'BIC Gel-ocity Retractable Quick Dry Gel Pen, Medium Point (0.7mm), Blue'}
