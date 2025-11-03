from seller import Inventory , Item, Batch

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
