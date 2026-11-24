def find_eligible_customers(appointment, customers, max_discount=10):
    eligible = []

    for customer in customers:

        service_match = customer["service"] == appointment["service"]

        time_match = customer["available"] == appointment["time"]

        duration_match = customer["duration"] >= appointment["duration"]

        affordable = customer["budget"] >= appointment["price"] - max_discount

        if service_match and time_match and duration_match and affordable:
            eligible.append(customer)

    return eligible

if __name__ == "__main__":
    from data import appointments, customers

    matches = find_eligible_customers(
        appointments[1], customers
    )

    for customer in matches:
        print(customer["name"])    