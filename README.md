This project was done from May 2023 - August 2023 as part of my internship as an AI Engineer intern. 

This project aims to use LLMs to support an information retrieval system to dramatically reduce the amount of manual document reading required of users. 
By storing nodes of text into a vector store and using the nearest neighbours of a query, it drastically reduces the possible context window length that 
is fed into an LLM, thus supporting offline models over the more powerful online models like GPT-3.5. 

The program runs completely offline and can be used to transform a document knowledge base into a vector store. Following initial processing, queries can be run against the vector store and sources to back up the LLM answers are displayed. Users can open the source files if they so wish to from the program. 

To add or remove documents and then update the vector stores, copy over documents from /pdfs to /insert_files or /delete_files respectively. This updates the chromaDB vector store for future querying.

To run: 
1. Install any Python version above 3.10.0. Do take note that this was tested with [Python 3.11.0](https://www.python.org/downloads/release/python-3110/). Remember to add python.exe to PATH.
2. Run in terminal:
    ```
    git clone https://github.com/onghaixiang/TODO
    ``` 
3. Install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html).
4. Download [cuda](https://developer.nvidia.com/cuda-downloads).
5. In the directory, run: 
    ```
    cd models
    git lfs install 
    git clone https://huggingface.co/sentence-transformers/all-mpnet-base-v2
    ```
6. Download any LLM model based on your computing power and place the model weights file in /models. This was tested with [Wizard-Vicuna-30B-Uncensored.ggmlv3.q2_K.bin](https://huggingface.co/TheBloke/Wizard-Vicuna-30B-Uncensored-GGML).
7. Set up a virtual environment: 
    ```
    py -m env myenv
    source myenv/Scripts/activate
    ```
8. Adjust GPU offloading in line 306-312 as per GPU power. 
9. Install cuBLAS support: 
    ```
    pip uninstall -y llama-cpp-python
    set CMAKE_ARGS="-DLLAMA_CUBLAS=on"
    set FORCE_CMAKE=1
    pip install llama-cpp-python --no-cache-dir
    ```
10. Install dependencies: 
    ```
    pip install -r requirements.txt
    ```
9. To start the program, run: 
    ```
    py main.py
    ```
