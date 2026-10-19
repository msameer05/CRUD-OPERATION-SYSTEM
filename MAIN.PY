from pathlib import Path


def get_path(file_name):
    return Path(__file__).resolve().parent / file_name


def read_int(prompt):
    return int(input(prompt).strip().lstrip("\ufeff"))


def createfile():
    try:
        name = input("Please enter your file name: ").strip()
        if not name:
            print("File name cannot be empty.")
            return

        file_path = get_path(name)
        if file_path.exists():
            print("Error: file name already exists.")
            return

        data = input("What do you want to write? ")
        with file_path.open("w", encoding="utf-8") as file:
            file.write(data)
        print("File created successfully.")
    except Exception as err:
        print(f"An error occurred: {err}")


def readfile():
    try:
        name = input("Please enter your file name: ").strip()
        file_path = get_path(name)
        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as file:
                content = file.read()
            print(f"Your file content is:\n{content}")
        else:
            print("Error: no such file exists.")
    except Exception as err:
        print(f"An error occurred: {err}")


def updatefile():
    try:
        name = input("Please enter your file name: ").strip()
        file_path = get_path(name)

        if not file_path.exists():
            print("Error: no such file exists.")
            return

        print("Operations:")
        print("1. Renaming the file")
        print("2. Appending the content")
        print("3. Overwriting the file")

        choice = read_int("Enter your choice: ")

        if choice == 1:
            new_name = input("Tell your new file name: ").strip()
            if not new_name:
                print("File name cannot be empty.")
                return

            new_path = get_path(new_name)
            if new_path.exists():
                print("Error: file already exists.")
                return

            file_path.rename(new_path)
            print("Rename successful.")

        elif choice == 2:
            data = input("What do you want to append? ")
            with file_path.open("a", encoding="utf-8") as file:
                file.write("\n" + data)
            print("Successfully appended.")

        elif choice == 3:
            data = input("What do you want to overwrite? ")
            with file_path.open("w", encoding="utf-8") as file:
                file.write(data)
            print("Successfully overwritten.")
        else:
            print("Invalid option selected.")
    except ValueError:
        print("Please enter a valid number.")
    except Exception as err:
        print(f"An error occurred: {err}")


def deletefile():
    try:
        name = input("Please enter your file name: ").strip()
        file_path = get_path(name)
        if file_path.exists():
            file_path.unlink()
            print("File deleted successfully.")
        else:
            print("Error: no such file exists.")
    except Exception as err:
        print(f"An error occurred: {err}")


while True:
    print("\nPress 1 to create a file.")
    print("Press 2 to read a file.")
    print("Press 3 to update a file.")
    print("Press 4 to delete a file.")
    print("Press 5 to exit.")

    try:
        a = read_int("\nEnter your choice: ")
    except ValueError:
        print("Please enter a valid number.")
        continue

    if a == 1:
        createfile()
    elif a == 2:
        readfile()
    elif a == 3:
        updatefile()
    elif a == 4:
        deletefile()
    elif a == 5:
        print("Goodbye!")
        break
    else:
        print("You entered an invalid option. Please try again.")