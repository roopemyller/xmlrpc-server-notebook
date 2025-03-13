import xmlrpc.client

server = xmlrpc.client.ServerProxy("http://localhost:8000/")

def main ():
    while True:
        print("\nNotebook Client")
        print("1. Add note")
        print("2. Get notes")
        print("3. Search Wikipedia")
        print("0. Exit")

        choice = input("Choose an option: ")

        match choice:
            case "1":
                print("Add note!")
                topic = input("Enter topic: ")
                text = input("Enter note text: ")
                print(server.addNote(topic, text))
            case "2":
                print("Get notes!")
                topic = input("Enter topic: ")
                notes = server.getNotes(topic)
                if isinstance(notes, list):
                    for timestamp, text in notes:
                        print(f"{timestamp}: {text}")
                else:
                    print(notes)
            case "3":
                print("Search topic from Wikipedia!")
                topic = input("Enter topic: ")
                print(server.fetchWikipedia(topic))
            case "0":
                print("Exit program!")
                break
            case _:
                print("Wrong input, try again!")

    print("Thanks you for using this program!")

main()