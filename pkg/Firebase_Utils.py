import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
firebase_app = None

def initialize_firebase():
    global firebase_app
    if not firebase_app:
        # Load Firebase credentials from the JSON file
        firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
        cred_dict = json.loads(firebase_credentials)
        cred = credentials.Certificate(cred_dict) 
        firebase_app = firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully.")
    else:
        print("Firebase already initialized.")


# Fetch all existing order IDs from the specified Firebase collection
def fetch_existing_firebase_ids(collection_name):
    db = firestore.client()
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    return {doc.id: doc.to_dict() for doc in docs}


# Delete specific documents or the entire Firebase collection if document_ids is not specified
def delete_firebase_documents(collection_name, document_ids=None):
    db = firestore.client()
    collection_ref = db.collection(collection_name)
    
    if document_ids:
        # Delete specified documents
        for doc_id in document_ids:
            collection_ref.document(doc_id).delete()
            print(f"Order {doc_id} deleted from Firebase.")
    else:
        # Delete all documents in the collection
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()
        print(f"All documents deleted from collection: {collection_name}")



# Push data to Firestore
def push_to_firebase(collection_name, document_id, data):
    try:
        db = firestore.client()  # Get Firestore client
        doc_ref = db.collection(collection_name).document(document_id)  # Specify the collection and document
        doc_ref.set(data)  # Push the data to Firestore
        print(f"Data successfully written to {collection_name}/{document_id}")
    except Exception as e:
        print(f"Failed to write data to Firebase: {str(e)}")


