from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from pathlib import Path

from .models import SensorInfo

def iter_blocks(document):
    """
    Iterate through paragraphs and tables
    in the actual order they appear in the Word document.
    """

    body = document.element.body

    for child in body.iterchildren():

        if child.tag.endswith("}p"):
            yield Paragraph(child, document)

        elif child.tag.endswith("}tbl"):
            yield Table(child, document)


# -----------------------------------
# Load Word document
# -----------------------------------

print("hi inside helpers2")
# -----------------------------------
# Find Table 1
# -----------------------------------


def process_files(path):


    found_table_1 = False
    found_table_2=False



    doc = Document(path)
    
    for block in iter_blocks(doc):

        print(block)
        if isinstance(block, Paragraph):
            text = block.text.strip()
            print("hi",text,block.text)

            if text == "Table 1":

                print("Found Table 1")
                found_table_1 = True

            if text=="Table 2":
                print("Table 2")
                found_table_2=True


        # --------------------------------
        # Paragraph
        # --------------------------------
        # --------------------------------
        # Table
        # --------------------------------
        elif isinstance(block, Table):

            # This is the table immediately
            # after "Table 1"
            #print(block.table,block.rows)
            print(found_table_1)
            if found_table_1:
                print("Found the required table")

            # --------------------------------
            # Iterate row by row
            # --------------------------------

            for row in block.rows[1:]:

                row_values = []

                for cell in row.cells:

                    value = cell.text.strip()
                    row_values.append(value)
                    #print(value)

                print(row_values)


            #for value in row_values[1:]:
                SensorInfo.objects.get_or_create(sensor_name=row_values[0],sensor_type=row_values[1],year=row_values[2],value=row_values[3])


            # Stop because we only want Table 1
            break





def process_all_files():
    path="/Users/ncvhome/NodeApp/Ecommerce/core/data_inegstion/data_set2/"


    DATA_DIR = Path(path)


    for file_path in DATA_DIR.iterdir():

        if file_path.suffix.lower() == ".docx":
            print(file_path)
            process_files(file_path)


if "__name__"=="__main__":
    process_all_files()




    



        


            