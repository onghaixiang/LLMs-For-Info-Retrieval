#This script converts html files into pdf files for further processing. 

import os 
import pdfkit  
#Replace input with file path to wkhtmltopdf binary file.
config = pdfkit.configuration(wkhtmltopdf = r"")  

#Replace input with directory path of htmls to convert to pdfs. 
directory = os.fsencode(r"")

for file in os.listdir(directory): 
    filename = os.fsdecode(file)
    #Create the file path of the HTML file. 
    filepath = r"" + filename
    #Create the file path of the output PDF file. 
    output_name = r"" + filename[:-4] + ".pdf"

    try:
        pdfkit.from_file(filepath, output_name, configuration = config, options={"enable-local-file-access": ""})
    except OSError as e:
        pass
        
