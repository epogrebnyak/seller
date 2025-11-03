# seller
FIFO inventory tracking system in Python

## Short example

```python 
from seller import Inventory

i = Inventory()
pen = Item("Pen")
i.buy(pen @ 0.55 * 100)
i.buy(pen @ 0.65 * 100)
i.sell(pen @ 1.05 * 150)
print(i.earned) # 70 = (1.05-0.55) * 100 + (1.05-0.65) * 50
print(i.hold)   # {'Pen': [Batch(purchase_price=0.65, quantity=50)]}
```

## Usage ideas

- OOP concepts in Python (eg operator overloading)
- learn-as-you-code in the financial accounting doamin
- generate quizes for accounting and financial management  
- proofs or scenarios for policies (eg. FIFO vs LIFO vs. WA, amortization schedules)
- inventory optimisation / margin strategies demos (eg ABC)
- simulation and agents (eg can a LLM run the shop)
- generate synthetic data to match company reports (Tesco, Walmart, Amazon)
- transactions ledger for equity trading
