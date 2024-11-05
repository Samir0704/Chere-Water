import secrets

def generate_order_number():
    numbers = "0123456789"
    new_num = [secrets.choice(numbers) for _ in range(8)]
    return f"#{''.join(new_num)}"