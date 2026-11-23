
from app.records import count_by, get_by_id, load_records, search


def show_menu():
    print("\n===== RationSahayak Menu =====")
    print("1. Show all records")
    print("2. Search records")
    print("3. Count records by category")
    print("4. Find record by ID")
    print("0. Exit")


def main():
    records = load_records()

    while True:
        show_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            for record in records:
                print("\n", record)

        elif choice == "2":
            keyword = input("Enter keyword: ")
            results = search(records, keyword)

            if results:
                for record in results:
                    print("\n", record)
            else:
                print("No records found.")

        elif choice == "3":
            category = input("Enter category (topic/card_type): ")
            results = count_by(records, category)

            for key, value in results.items():
                print(key, ":", value)

        elif choice == "4":
            try:
                record_id = int(input("Enter record ID: "))
                result = get_by_id(records, record_id)

                if result:
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


if __name__ == "__main__":
    main()