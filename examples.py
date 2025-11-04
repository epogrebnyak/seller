from seller import Seller, Item

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

i = Seller(cash=200)  # type: ignore
pen = i.register(
    "BIC Gel-ocity Retractable Quick Dry Gel Pen, Medium Point (0.7mm), Blue"
)
i.buy(pen @ 0.55 * 100)
i.buy(pen @ 0.65 * 100)
i.sell(pen @ 1.05 * 151)
i.pay(10, "fee")
print("        Cash:", f"{i.cash:6.2f}") 
print("   Inventory:", f"{i.hold.worth:6.2f}")
print("Total assets:", f"{i.cash + i.hold.worth:6.2f}")
print("Net earnings:", f"{i.earned:6.2f}")
print(i)
