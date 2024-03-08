from flask import Blueprint, jsonify, request, session

note_router = Blueprint('note', __name__)

# Retrieve notes
@note_router.route('/note')
def get_notes():
    if session.get('logged_in'):
        return jsonify(session.get('notes', []))
    else:
        return "Unauthorized", 401

# Add note
@note_router.route('/note', methods=['POST'])
def add_note():
    note = request.form.get('note')
    if note:
        session['notes'].append(note)
        return "OK"
    else:
        return "Invalid request"
