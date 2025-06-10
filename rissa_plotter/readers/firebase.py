import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from pathlib import Path


@st.cache_resource
def initialize_firebase(path: str | Path) -> firestore.client:
    """
    Initialize the Firebase Admin SDK to connect to the Firestore database.

    Authenticates using a service account key file, which contains private credentials
    that grant access to the Firebase project.

    Parameters
    ----------
    path : str
        Path to the Firebase service account key file.

    Returns
    -------
    firestore.client
        A configured Firestore client for database operations.
    """

    try:
        app = firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(path)
        app = firebase_admin.initialize_app(cred)

    return firestore.client()


class FireBase:
    def __init__(self, file: str | Path):
        """
        Initialize the DataBase class with a path to the Firebase service account key file.

        Parameters
        ----------
        file : str | Path
            Path to the Firebase service account key file.
        """

        self.file = file
        self.connection = None

    def __enter__(self):
        self.get_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection = None

    def get_connection(self):
        self.connection = initialize_firebase(self.file)

    def collections(self):
        """
        Get a list of all collections in the Firestore database.

        Returns
        -------
        list
            List of collection names in the Firestore database.
        """
        self.get_connection()
        collections = self.connection.collections()
        return [collection.id for collection in collections]

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()

    def read_table(self, table: str) -> pd.DataFrame:
        """
        Read a table from the Firestore database.

        Parameters
        ----------
        table : str
            Name of the Firestore collection to read.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the data from the specified Firestore collection.
        """
        self.get_connection()
        docs = self.connection.collection(table).stream()
        self.close_connection()
        data = [doc.to_dict() for doc in docs]

        if not data:
            raise ValueError(f"No data found in {table} collection.")

        return pd.DataFrame(data)
