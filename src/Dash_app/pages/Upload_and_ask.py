# Import packages
import dash
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

import pymupdf
import pymupdf4llm
import fitz

# For PDF mining
import PyPDF2
import re
import base64
import os
import io

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# For processing all PDFs
from src.utils.PDFprocessor02_Marisa import PDFprocessor
from src.dashboard.components.chatbot_button import get_chatbot
from src.rag.generate_vectorstore import get_vectorstore, add_document

# -----------------------
# Initialize the page
# app = dash.get_app()
dash.register_page(__name__)


# Initialize the PDFprocessor
processor = PDFprocessor()

header = html.Div(
    [
        html.H1("Chatbot test"),
        html.P("This is a testpage for a simple chatbot running locally."),
        html.P("For now, the page is a placeholder to show a different presentation of the Chatbot")
        # "an explanation of NPU and a presentation of the Laptop used will be presented. The chatbot is implemented to answer questions regarding the Laptop and its capabilities. Lastly, if the layout allows, this page should include some performance display for NPU/GPU/CPU capabilities")
    ]
)
### Chatbot placeholder
# chatbot_placeholder = html.Div([
#         html.H3("Chatbot placeholder"),
#         html.P("This is nonsense text to show how the chatbot will be embedded between two text paragraphs"),
#         html.P("Further test test test"),
#         html.P("Test test test")
#         # "an explanation of NPU and a presentation of the Laptop used will be presented. The chatbot is implemented to answer questions regarding the Laptop and its capabilities. Lastly, if the layout allows, this page should include some performance display for NPU/GPU/CPU capabilities")
#     ], style={'border': '2px dashed gray', 'padding': '20px', 'margin-bottom': '20px'}
# )

chatbot_layout = get_chatbot()

# chatbot_layout.children

### PDF uploader
pdf_uploader = html.Div([
    html.H3("Upload a PDF File"),
    dcc.Upload(
        id='upload-pdf',
        children=html.Div([
            'Drag and drop or ', html.A('click to upload a PDF file')
        ]),
        style={
            'width': '80%',
            'font-family': 'sans-serif',
            'font-size': '18px',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True  # Allow multiple files to be uploaded
    ),
    html.Div(id='output-data-upload')
])


# App layout
def layout (**kwawrgs):
    page = dbc.Container(
        fluid=True,
        children=[
            header,
            html.Hr(),
            chatbot_layout,
            dcc.Store(id='vectorstore'),
            # dcc.Store(id="store-conversation", data=[]),
            #chatbot_layout,
            html.Hr(),
            pdf_uploader
        ]
    )
    return page


def process_pdf(content, filename):

    if not filename.lower().endswith(".pdf"):
        return "Please upload a PDF file."

    _, content_string = content.split(",")
    pdf_bytes = base64.b64decode(content_string)
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    raw_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    data = Document(page_content=raw_text, metadata=pdf_reader.metadata)
    return data

### ADD CONTENT OF UPLOADED PDF
def add_new_content(content, filename):
    # Check if PDF
    vector_store = get_vectorstore()

    if not filename.lower().endswith(".pdf"):
        return html.Div(["Please upload a PDF file."])

    try:
        # Extract base64-encoded string and decode it 
        _, content_string = content.split(",")
        pdf_bytes = base64.b64decode(content_string)

        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        raw_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        data = Document(page_content=raw_text, metadata=pdf_reader.metadata)
        add_document(vector_store, data)
        vector_store.similarity_search("Prompt engineering")
        # 1. Extract text

        ###### Using the PDFprocessor methods:

        # # 2. Clean the text and get chunks
        # cleaned_text = processor.clean_text(raw_text)
        # processor.text = cleaned_text
        # processor.get_text_chunks()

        # # 3. Create vector store
        # processor.get_vectorstore(api_key = api_key)  # To be changed when we decide the embeddings, in the meantime, set api_key in the .env

        return html.Div([
            html.H5(filename),
            html.P("Your file uploaded and processed successfully."),
            html.Hr()
            #print(new_content) # Just to check that it's processed
        ])

    except Exception as e:
        return html.Div([f"Error processing the PDF file."])

# Callbacks-------------------

@callback(Output('output-data-upload', 'children'),
              Input('upload-pdf', 'contents'),
              State('upload-pdf', 'filename')
)
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            add_new_content(conts, names) for conts, names in
            zip(list_of_contents, list_of_names)]
        
        children = [
            process_pdf(conts, names) for conts, names in
            zip(list_of_contents, list_of_names)
        ]

        return children



# Save for RAG


# Run the app
if __name__ == '__main__':
    # app.run(port=8888, debug=True)
    None