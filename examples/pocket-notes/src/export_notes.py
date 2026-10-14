"""Pocket Notes JSON export — fictional demonstration application."""
import json

def export_notes(notes):
    if not isinstance(notes, list):
        raise ValueError("notes must be a list")
    output = []
    for note in notes:
        if not isinstance(note, dict) or not isinstance(note.get("title"), str) or not note["title"].strip():
            raise ValueError("each note needs a nonblank title")
        if not isinstance(note.get("body"), str):
            raise ValueError("each note needs a text body")
        output.append({"title": note["title"], "body": note["body"]})
    return json.dumps({"format": "pocket-notes-1", "notes": output}, ensure_ascii=False, indent=2) + "\n"

if __name__ == "__main__":
    print(export_notes([{"title": "Café", "body": "A fictional note."}]), end="")
