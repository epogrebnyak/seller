from dataclasses import dataclass, field

from collections import deque
from primitives import Batch


@dataclass
class Stack:
    """Represent a stack of items."""

    batches: deque[Batch] = field(default_factory=deque)

    def __getitem__(self, index: int) -> Batch:
        """Get a batch by index."""
        return self.batches[index]

    def add(self, p: float, q: int | float):
        """Add a batch to the stack."""
        self.batches.append(Batch(p, q))
        return self

    def append(self, batch: Batch):
        """Add a batch to the stack."""
        self.batches.append(batch)
        return self

    def extend(self, batches: list[Batch]):
        """Add multiple batches to the stack."""
        self.batches.extend(batches)
        return self

    def _take(
        self, quantity: int | float, index: int, remove_method: str
    ) -> list[Batch]:
        """Take batches of items from the stack."""
        taken = []
        while quantity > 0 and self.batches:
            current_batch = self.batches[index]
            if current_batch.quantity <= quantity:
                taken.append(current_batch)
                quantity -= current_batch.quantity
                getattr(self.batches, remove_method)()
            else:
                partial_batch = Batch(current_batch.purchase_price, quantity)
                taken.append(partial_batch)
                current_batch.quantity -= quantity
                break
        return taken

    def take_first(self, quantity: int | float) -> list[Batch]:
        """Take batches of items from the stack in FIFO order."""
        return self._take(quantity, index=0, remove_method="popleft")

    def take_last(self, quantity: int | float) -> list[Batch]:
        """Take batches of items from the stack in LIFO order."""
        return self._take(quantity, index=-1, remove_method="pop")

    @property
    def quantity(self):
        """Return the total quantity of items in the stack."""
        return sum(batch.quantity for batch in self.batches)

    @property
    def worth(self):
        """Calculate the total value of batches in the stack."""
        return sum(batch.purchase_price * batch.quantity for batch in self.batches)

    @property
    def average_price(self):
        """Calculate the average purchase price of items in the stack."""
        if self.quantity == 0:
            return 0
        return self.worth / self.quantity

    def equalize_prices(self):
        """Set all batches purchase price to the same averaged price."""
        price = self.average_price
        for batch in self.batches:
            batch.purchase_price = price
        return self
