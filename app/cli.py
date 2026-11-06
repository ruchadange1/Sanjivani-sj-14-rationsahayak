from app.records import load_records, search, count_by, get_by_id


# loading all records
records = load_records()


while True:
    print("\n===== RationSahayak Menu =====")
    print("1. Show all records")
    print("2. Search records")
    print("3. Count records by category")
    print("4. Find record by ID")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        for record in records:
            print("\n", record)

    elif choice == "2":
        keyword = input("Enter keyword to search: ")
        result = search(records, keyword)

        if len(result) > 0:
            for record in result:
                print("\n", record)
        else:
            print("No records found.")

    elif choice == "3":
        category = input("Enter category (topic/card_type): ")
        result = count_by(records, category)

        for key, value in result.items():
            print(key, ":", value)

    elif choice == "4":
        record_id = input("Enter record ID: ")

        try:
            result = get_by_id(records, int(record_id))

            if result is not None:
                print("\nRecord found:")
                print(result)
            else:
                print("Record not found.")

        except ValueError:
            print("Please enter a valid number.")

    elif choice == "0":
        print("Thank you for using RationSahayak!")
        break

    else:
        print("Invalid choice. Please try again.")