
# Distributed Systems - Assignment 2 - Roope Myller

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
                note = input("Enter note title: ")
                text = input("Enter note text: ")
                if topic == "" or note == "" or text == "":
                    print("All fields are required!")
                else:
                    print(server.addNote(topic.lower(), note, text))
            case "2":
                print("Get notes!")
                topic = input("Enter topic: ")
                notes = server.getNotes(topic.lower())
                if isinstance(notes, list):
                    for timestamp, note, text in notes:
                        print(f"{timestamp} : {note} : {text}")
                else:
                    print(notes)
            case "3":
                print("Search topic from Wikipedia!")
                topic = input("Enter topic: ")
                if topic == "":
                    print("Topic is required!")
                else:
                    print(server.fetchWikipedia(topic))
            case "0":
                print("Exit program!")
                break
            case _:
                print("Wrong input, try again!")

    print("Thanks you for using this program!")

main()