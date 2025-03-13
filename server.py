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
        except (ET.ParseError, FileNotFoundError):
            self.root = ET.Element("data")
            self.tree = ET.ElementTree(self.root)
            self.saveXml()

    def saveXml(self):
        # Function to save the xml file
        self.tree.write(DB, encoding="utf-8", xml_declaration=True)

    def addNote(self, topic, text):
        '''
            function for adding notes to the mock db
            takes in parameters self (the notebookserver), topic (topic name) and text (topic text)

            Lookups the db for the topic, if not found creates a new one
            adds the text with a new timestamp to the topic
        '''
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

        topicElement = None
        for t in self.root.findall("topic"):
            if t.get("name") == topic:
                topicElement = t
                break
        
        if topicElement is None:
            topicElement = ET.SubElement(self.root, "topic", name=topic)
        
        noteElement = ET.SubElement(topicElement, "note", name=topic)
        textElement = ET.SubElement(noteElement, "text")
        timestampElement = ET.SubElement(noteElement, "timestamp")
        textElement.text = text
        timestampElement.text = timestamp

        self.saveXml()
        return f"Note '{text}' added to topic '{topic}'."
    
    def getNotes(self, topic):
        '''
            function for getting notes from the mock db
            takes in parameters self and topic (topic name)

            Finds all (if any) notes and prints them out to the user
        '''
        for t in self.root.findall("topic"):
            if t.get("name") == topic:
                notes = []
                for note in t.findall("note"):
                    note_text = note.find("text").text.strip() if note.find("text") is not None else "No text"
                    timestamp = note.find("timestamp").text.strip() if note.find("timestamp") is not None else "No timestamp"
                    notes.append((timestamp, note_text))
                return notes if notes else f"No notes found under topic '{topic}'."
        return f"Topic '{topic}' not found." 
    
    def fetchWikipedia(self, topic):
        '''
            function for fetching topics from wikipedia
            takes in parameters self and topic (topic name)

            makes a api request to fetch the first hit and the intro part from that wikipedia page. Then it adds it to the mock db and returns the found text to the user.

            https://www.mediawiki.org/wiki/API:Opensearch
            https://www.mediawiki.org/wiki/Extension:TextExtracts
        '''

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

            self.addNote(pageTitle, pageText)

            return f"Found page {pageTitle} with text:\n{pageText}\nAdding text to database!"

        return "No Wikipedia article found"

server = SimpleXMLRPCServer(("localhost", 8000), requestHandler=SimpleXMLRPCRequestHandler)
notebookServer = NoteBookServer()

server.register_function(notebookServer.addNote, "addNote")
server.register_function(notebookServer.getNotes, "getNotes")
server.register_function(notebookServer.fetchWikipedia, "fetchWikipedia")

print("Server is running on port 8000")
server.serve_forever()