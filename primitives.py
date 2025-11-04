from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class UUID:
    """Generator for unique identifier strings."""

    n_chars: int = 36

    def __post_init__(self):
        self.n_chars = min(self.n_chars, 36)

    def new(self) -> str:
        return str(uuid.uuid4())[: self.n_chars]


@dataclass
class Stamp:
    time: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=UUID(8).new)


@dataclass
class Batch:
    """A set of items purchased at the same price."""

    purchase_price: float
    quantity: int | float


@dataclass
class Item:
    """Represents an item in inventory."""

    name: str

    def __matmul__(self, price):
        """Set the price using @ operator."""
        return Order(self.name, price, 0)

    def __mul__(self, q):
        """Set the quantity using * operator."""
        return Order(self.name, 0, q)


@dataclass
class Order:
    """Represents a purshase or sales transaction."""

    name: str
    price: float
    quantity: int | float

    @property
    def worth(self):
        """Calculate total value of this sale."""
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

    def to_order(self) -> Order:
        """Convert to an Order object."""
        return Order(self.name, self.price, self.quantity)


@dataclass
class Expense:
    """Represents an expense incurred."""

    amount: float
    description: str
