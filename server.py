
# Distributed Systems - Assignment 2 - Roope Myller

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xml.etree.ElementTree as ET
import datetime
import requests

DB = "notes.xml"

class NoteBookServer:
    '''
        NoteBookServer

        Has a mock XML database for topics/notes

        Has functions such as loadOrCreateXML, saveXML, addNote, getNotes to manipulate data inside the db
    '''
    def __init__(self):
        self.loadOrCreateXML()

    def loadOrCreateXML(self):
        # Function to load / create the XML mock db
        try:
            self.tree = ET.parse(DB)
            self.root = self.tree.getroot()
            print(f"Loaded XML file {DB}")
        except (ET.ParseError, FileNotFoundError):
            try:
                self.root = ET.Element("data")
                self.tree = ET.ElementTree(self.root)
                self.saveXml()
                print(f"Created new XML file {DB}")
            except Exception as e:
                print(f"Error creating new XML file: {e}")

    def saveXml(self):
        # Function to save the xml file
        try:
            self.tree.write(DB, encoding="utf-8", xml_declaration=True)
            print(f"Saved XML file {DB}")
        except Exception as e:
            print(f"Error saving XML file: {e}")

    def addNote(self, topic, note, text, url=None):
        '''
            function for adding notes to the mock db
            takes in parameters self (the notebookserver), topic (topic name), text (topic text) and optional url (url to the wikipedia topic)

            Lookups the db for the topic, if not found creates a new one
            adds the text with a new timestamp to the topic
        '''
        try:
            timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

            topicElement = None
            for t in self.root.findall("topic"):
                if t.get("name") == topic.lower():
                    topicElement = t
                    break
            
            if topicElement is None:
                topicElement = ET.SubElement(self.root, "topic", name=topic.lower())
            
            noteElement = ET.SubElement(topicElement, "note", name=note.lower())
            textElement = ET.SubElement(noteElement, "text")
            timestampElement = ET.SubElement(noteElement, "timestamp")

            if text is None or text == "":
                text = "No text"

            if url is not None:
                text = url + "\n" + text

            textElement.text = text
            timestampElement.text = timestamp

            self.saveXml()
            print("Added note to topic")
            return f"Note '{text}' added to topic '{topic}'."
        except Exception as e:
            print("Error adding note")
            return f"Error adding note: {e}"

    def getNotes(self, topic):
        '''
            function for getting notes from the mock db
            takes in parameters self and topic (topic name)

            Finds all (if any) notes and returns them to client (printed out in client side)
        '''
        try:
            for t in self.root.findall("topic"):
                if t.get("name") == topic.lower():
                    notes = []
                    for note in t.findall("note"):
                        note_title = note.get("name")
                        if note.find("text") is not None or note.find("text") == "":
                            note_text = note.find("text").text.strip()
                        else:
                            note_text = "No text"
                        
                        if note.find("timestamp") is not None:
                            timestamp = note.find("timestamp").text.strip()
                        else:
                            timestamp = "No timestamp"
                        notes.append((timestamp,note_title, note_text))
                    print(f"Found notes under topic '{topic}'")
                    return notes if notes else f"No notes found under topic '{topic}'."
            print("Topic not found")
            return f"Topic '{topic}' not found." 
        except Exception as e:
            print("Error getting notes")
            return f"Error getting notes {e}"

    def fetchWikipedia(self, topic):
        '''
            function for fetching topics from wikipedia
            takes in parameters self and topic (topic name)

            makes a api request to fetch the first hit and the intro part from that wikipedia page. Then it adds it to the mock db and returns the found text to the user.

            https://www.mediawiki.org/wiki/API:Opensearch
            https://www.mediawiki.org/wiki/Extension:TextExtracts
        '''
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "titles": topic,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True
            }

            response = requests.get(url, params=params)
            if(response.status_code == 200):
                data  = response.json()

                pages = data["query"]["pages"]
                page = next(iter(pages.values()))

                pageTitle = page["title"]
                pageText = page["extract"]
                pageId = page["pageid"]
                pageUrl = f"https://en.wikipedia.org/?curid={pageId}"

                self.addNote(topic, pageTitle, pageText, pageUrl)
                if pageText is None:
                    pageText = "No text"

                print("Found Wikipedia article")
                return f"Found page {pageTitle} with url: {pageUrl}\nText:{pageText}\n\nAdded note to database!"
            print("No Wikipedia article found")
            return "No Wikipedia article found"
        except Exception as e:
            print("Error fetching Wikipedia")
            return f"Error fetching Wikipedia: {e}"


def main ():
    server = SimpleXMLRPCServer(("localhost", 8000), requestHandler=SimpleXMLRPCRequestHandler)
    notebookServer = NoteBookServer()

    server.register_function(notebookServer.addNote, "addNote")
    server.register_function(notebookServer.getNotes, "getNotes")
    server.register_function(notebookServer.fetchWikipedia, "fetchWikipedia")

    print("Server is running on port 8000")
    server.serve_forever()

main()