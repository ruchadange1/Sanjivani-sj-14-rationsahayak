while True:

    print("\n========== RATIONSAHAYAK MENU ==========")
    print("1. About RationSahayak")
    print("2. Sample Questions")
    print("3. Check Ration Entitlement")
    print("0. Exit")
    print("========================================")

    choice = input("\nEnter your choice (0-3): ").strip()

    if choice == "1":

        print("\n--- About RationSahayak ---")
        print("RationSahayak is an AI-powered citizen")
        print("assistance system for Maharashtra.")
        print("It helps people understand ration card")
        print("benefits, grain entitlement and portability.")

    elif choice == "2":

        print("\n--- Sample Questions ---")
        print("1. How much grain does an AAY card get?")
        print("2. Can I use my Beed ration card in Kopargaon?")
        print("3. What is the PHH grain entitlement?")
        print("4. Where can I complain about less ration?")

    elif choice == "3":

        print("\n--- Ration Entitlement Checker ---")

        card_type = input(
            "Enter card type (AAY/PHH): "
        ).strip().upper()

        if card_type == "AAY":

            quantity = 35
            print("\nAAY Entitlement: 35 kg per household")

        elif card_type == "PHH":

            members_input = input(
                "Enter number of family members: "
            ).strip()

            if members_input.isdigit() and int(members_input) > 0:

                members = int(members_input)
                quantity = members * 5

                print(f"\nFamily Members: {members}")
                print(f"PHH Entitlement: {quantity} kg per month")

            else:
                print("Invalid family member count.")

        else:
            print("Invalid card type. Please enter AAY or PHH.")

    elif choice == "0":

        print("\nThank you for using RationSahayak!")
        print("Exiting application...")
        break

    else:

        print("\nInvalid choice!")
        print("Please enter 1, 2, 3 or 0.")
