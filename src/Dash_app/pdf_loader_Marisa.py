# Import packages
from dash import Dash, html, dcc, Input, Output, State

## For PDF mining
import PyPDF2
import re
import base64
import os
import io

# -----------------------

# Initialize the app
app = Dash()

# App layout
app.layout = html.Div([
    html.H1(children = "Marisa's PDF loader"),

    # Upload the file:
    dcc.Upload(
        id='upload-pdf',
        children=html.Div(['Drag and drop or ',
            html.A('click to upload a PDF file')
        ]),
        style={ # --> To be added to a CSS style sheet and have fun with it
            'width': '70%',
            'font-family': 'sans-serif',
            'font-size': '16px',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '2px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True # Allow multiple files to be uploaded
       ),
    html.Div(id='output-data-upload'),
])

### PDF TO TEXT function

def pdf_to_text(pdf_bytes):

    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes)) # --> Doing this in case the PDF is Base64 encoded!!
    text = [page.extract_text() for page in reader.pages if page.extract_text()]

    # Converting list to string and removing line breaks
    full_text = " ".join(text).replace("\n", " ")

    # Removing extra spaces
    clean_text = re.sub(r'\s+', ' ', full_text).strip()

    return clean_text

### BUILD CORPUS

folder_path = "./sample_pdfs" # To be changed to the folder on the laptop
all_content = []
for file in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file)
    with open(file_path, "rb") as f:
        file_content = pdf_to_text(f.read())
    all_content.append(file_content)

### ADD CONTENT OF UPLOADED PDF

def add_new_content(content, filename):
    # Check if PDF
    if not filename.lower().endswith(".pdf"):
        return html.Div(["Please upload a PDF file."])

    try:
        # Extract base64-encoded string and decode it 
        _, content_string = content.split(",")
        pdf_bytes = base64.b64decode(content_string)

        # Add PDF content to corpus
        new_content = pdf_to_text(pdf_bytes)
        all_content.append(new_content)

        return html.Div([
            html.H5(filename),
            'uploaded',
            html.Hr(), # horizontal line
            # print(new_content)  --> It works
        ])

    except Exception as e:
        return html.Div([f"Error processing the PDF file."])
    
# TO DO
# Embed PDF in vector store
# save vector store

# Callbacks-------------------

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-pdf', 'contents'),
              State('upload-pdf', 'filename')
)
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            add_new_content(conts, names) for conts, names in
            zip(list_of_contents, list_of_names)]
        
        return children


# Save for RAG


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
