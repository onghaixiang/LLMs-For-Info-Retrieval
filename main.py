import threading
from llama_index import SimpleDirectoryReader, VectorStoreIndex, ServiceContext, LangchainEmbedding, LLMPredictor, Prompt
from llama_index.vector_stores import ChromaVectorStore
from langchain.llms import LlamaCpp
from llama_index.storage.storage_context import StorageContext
from langchain.embeddings import HuggingFaceEmbeddings  
import tkinter as tk
from tkinter import font
import time
import customtkinter
import chromadb
from chromadb.config import Settings
from pathlib import Path
import os

src_list = []        
def query_function(f): 
    
    def process_input(): 
        
        #adjust widgets while output is being generated
        process_button.configure(text="Thinking...", fg_color="#3B8ED0", state=tk.DISABLED)
        response_box.delete(index1="0.0", index2=tk.END)
        root.update_idletasks()
        time.sleep(0.5)
        
        #get input
        user_input = text_box.get("1.0", tk.END).strip()
        global src_list
        #destroy all previous source widgets
        for t in src_list: 
            t.destroy()
        root.update_idletasks()

        src_list = []
        
        if (user_input != ""):
            
            #dump input into LLM
            global query_engine
            response_box.configure(state="normal")
            response = query_engine.query(user_input)
            
            #display answer
            ans = response.response.lstrip("-=_").rstrip("-=_")
            ans = ans.replace("\n", "")
            response_box.insert("1.0", ans)
            negative_patterns = ['unable to answer', 'impossible', 'guess', 'cannot determine', 'rough estimate', 'unable to determine', \
                'does not contain any relevant details', 'no information related', 'it is unclear', "unfortunately"]
            flag = True
            
            #check if answer seems to be guessing.
            for i in negative_patterns:
                if i in ans.lower() or ans.lower().strip() == "": 
                    print(i, ans)
                    process_button.configure(text="Done!", fg_color="green", command=process_input)
                    flag = False
                    break
            
            #Since LLM does not seem to be guessing, display sources.
            if flag: 
                x = 0
                for i in response.source_nodes:
                    text = customtkinter.CTkTextbox(f, height=150, width=450, wrap="word", font = default_font)
                    text.insert("1.0", i.node.text)
                    text.grid(column=x, row = 8, columnspan=2, padx=10, pady=10)
                    src_list.append(text)
                    test_label = customtkinter.CTkLabel(f, text=f"Source: {i.node.extra_info['file_name']}")
                    test_label.grid(column=x, row = 7, columnspan=2, padx=10, pady=10)
                    src_list.append(test_label)
                    open_file = customtkinter.CTkButton(f, text="Open File", command=lambda i=i: os.startfile(f"data\pdfs\{i.node.extra_info['file_name']}"))
                    open_file.grid(column=x, row = 9,columnspan=2, padx=10, pady=10)
                    src_list.append(open_file)
                    x += 2
                    
                process_button.configure(text="Done!", fg_color="green", command=process_input)

        #Input is missing, so display error. 
        else:
            response_box.insert("1.0", "Missing text!")
            process_button.configure(text="Done!", fg_color="red", command=process_input)
        process_button.configure(state=tk.NORMAL)
        root.update_idletasks()
        time.sleep(1.5)
        process_button.configure(text="Enter Prompt", fg_color="#3B8ED0")
          
    #destroy all previous widgets
    for w in f.winfo_children(): 
        w.destroy()
    
    #generate new widgets
    text_box_label = customtkinter.CTkLabel(f, text="Query")
    text_box_label.grid(column=0, row=3, columnspan=2, padx=10, pady=10)
    
    text_box = customtkinter.CTkTextbox(master=f, height=150, width=450, wrap="word", font = default_font)
    text_box.grid(column=0, row=4, columnspan=2, padx=10, pady=10)
    
    process_button = customtkinter.CTkButton(f, text="Enter Prompt", command=process_input)
    process_button.grid(column=1, row=5, columnspan=2, padx=10, pady=5)
    
    response_box_label = customtkinter.CTkLabel(f, text="Response")
    response_box_label.grid(column=2, row=3, columnspan=2, padx=10, pady=10)
    
    response_box = customtkinter.CTkTextbox(master=f, height=150, width=450, wrap="word", font = default_font)
    response_box.grid(column=2, row=4, columnspan=2, padx=10, pady=10)

def load_documents(): 
    #load documents and create a vector store. 
    documents = SimpleDirectoryReader(r'.\data\pdfs').load_data()
    global index
    index = VectorStoreIndex.from_documents(
        documents=documents, 
        storage_context=storage_context, 
        embed_model=embed_model, 
        service_context=service_context
        )


def load_documents_in_bg(pb): 
    #calls load_documents() while allowing the progress bar to move. 
    t = threading.Thread(target=load_documents, daemon=True)
    t.start()
    while t.is_alive(): 
        pb.update()
        time.sleep(0.3)
        
def delete_docs_intro(f): 
    #destroy all previous widgets
    for w in f.winfo_children(): 
        w.destroy()
    
    fp = "./data/delete_files"
    mainpdfs = "./data/pdfs"
    filenames = [i for i in os.listdir(fp) if os.path.isfile(os.path.join(fp,i))]
    
    #If there are no files, do not continue attempting to update vector store.
    if len(filenames) == 0: 
        message_label = customtkinter.CTkLabel(f, text="No files found!", font = default_font)
        message_label.grid(column=0, row=0, columnspan=2, rowspan=1, pady=10)
        button = customtkinter.CTkButton(f, text="Go Back", command=lambda: intro_page(f), state=tk.NORMAL, fg_color="green")
        button.grid(column=0, row=1, columnspan = 2)
    
    #There are files present, so ask for confirmation before updating vector store. 
    else: 
        text = ""
        for i in filenames: 
            text += f"{i}\n"
        message_label = customtkinter.CTkLabel(f, text="List of files to delete: ", font = default_font)
        message_label.grid(column=0, row=0, columnspan=2, pady=10)
        lstOfFiles = customtkinter.CTkTextbox(master=f, height=150, width=450, wrap="word", font = default_font)
        lstOfFiles.grid(column=0, row=2, columnspan=2, padx=10, pady=10)
        lstOfFiles.insert("1.0", text)
        y = customtkinter.CTkButton(f, text="Continue", command=lambda: delete_docs_in_bg(f, filenames, fp, mainpdfs), state=tk.NORMAL, fg_color="green")
        y.grid(column=0, row=4, rowspan=1, pady=10)
        n = customtkinter.CTkButton(f, text="Go Back", command= lambda: intro_page(f), state=tk.NORMAL, fg_color="red")
        n.grid(column=1, row=4, rowspan=1, pady=10)

def delete_docs(f, filenames, fp, mainpdfs):
    
    #destroy all previous widgets
    for w in f.winfo_children(): 
        w.destroy()
        
    message_label = customtkinter.CTkLabel(f, text="Deleting files...", font = default_font)
    message_label.grid(column=0, row=0, columnspan=2, pady=10)
    button = customtkinter.CTkButton(f, text="Waiting...", command = lambda: intro_page(f), state=tk.DISABLED,fg_color="red")
    button.grid(column=0, row=1, columnspan=2, pady=10)
    
    #For every file found in /delete_files, search for associated nodes in the vector store and delete them. 
    for i in filenames: 
        x = chroma_collection.get(
            where={'file_name' : i},
            include=['metadatas']) 
        for id in x["ids"]:
            chroma_collection.delete(ids = id)

    #Remove the files from /delete_files and /pdfs
    for file in filenames: 
        os.remove(os.path.join(fp, file))
        os.remove(os.path.join(mainpdfs, file))
    message_label.configure(text="Files deleted from db!")
    button.configure(text="Go Back", state=tk.NORMAL)

def delete_docs_in_bg(f, filenames, fp, mainpdfs):
    #Call delete_docs() to prevent the GUI from freezing.
    t = threading.Thread(target= lambda: delete_docs(f, filenames, fp, mainpdfs), daemon=True)
    t.start()

def add_docs_intro(f): 
    #destroy all previous widgets
    for w in f.winfo_children(): 
        w.destroy()
    fp = "./data/insert_files"
    mainpdfs = "./data/pdfs"
    filenames = [i for i in os.listdir(fp) if os.path.isfile(os.path.join(fp,i))]
    
    #If there are no files found in /insert_files, stop attempting to update the vector store. 
    if len(filenames) == 0: 
        message_label = customtkinter.CTkLabel(f, text="No files found!", font = default_font)
        message_label.grid(column=0, row=0, columnspan=2, rowspan=1, pady=10)
        button = customtkinter.CTkButton(f, text="Go Back", command=lambda: intro_page(f), state=tk.NORMAL, fg_color="green")
        button.grid(column=0, row=1, columnspan = 2)
    
    #Files have been found, so allow the user to confirm addition before updating the vector store. 
    else: 
        text = ""
        for i in filenames: 
            text += f"{i}\n"
        message_label = customtkinter.CTkLabel(f, text="List of files to add: ", font = default_font)
        message_label.grid(column=0, row=0, columnspan=2, pady=10)
        lstOfFiles = customtkinter.CTkTextbox(master=f, height=150, width=450, wrap="word", font = default_font)
        lstOfFiles.grid(column=0, row=2, columnspan=2, padx=10, pady=10)
        lstOfFiles.insert("1.0", text)
        y = customtkinter.CTkButton(f, text="Continue", command=lambda: add_docs_in_bg(f, filenames, fp, mainpdfs), state=tk.NORMAL, fg_color="green")
        y.grid(column=0, row=4, rowspan=1, pady=10)
        n = customtkinter.CTkButton(f, text="Go Back", command= lambda: intro_page(f), state=tk.NORMAL, fg_color="red")
        n.grid(column=1, row=4, rowspan=1, pady=10)

def add_docs_in_bg(f, filenames, fp, mainpdfs):
    #call add_docs() to prevent the GUI from freezing.
    t = threading.Thread(target= lambda: add_docs(f, filenames, fp, mainpdfs), daemon=True)
    t.start()

def add_docs(f, filenames, fp, mainpdfs):
    #destroy all previous widgets
    for w in f.winfo_children(): 
        w.destroy()
    message_label = customtkinter.CTkLabel(f, text="Adding files...", font = default_font)
    message_label.grid(column=0, row=0, columnspan=2, pady=10)
    button = customtkinter.CTkButton(f, text="Waiting...", command = lambda: intro_page(f), state=tk.DISABLED,fg_color="red")
    button.grid(column=0, row=1, columnspan=2, pady=10)
    new_docs = SimpleDirectoryReader(fp).load_data()
    
    #Delete any nodes associated with the files to add in the vector store. This essentially overwrites 
    #any existing nodes that are associated with the files to prevent double addition. 
    for i in filenames: 
        x = chroma_collection.get(
        where={"file_name": i},
        include = ['metadatas']
        )
        
        for ids in x["ids"]: 
            chroma_collection.delete(ids = ids)
    
    #This breaks up the new documents into nodes before adding hem to the vector store.         
    for doc in new_docs: 
        index.insert(doc)
    index.storage_context.persist()

    #Move the files from /insert_files to /pdfs. 
    for file in filenames: 
        os.rename(os.path.join(fp, file), os.path.join(mainpdfs, file))
    
    message_label.configure(text="Files added into db!")
    button.configure(text="Go Back", state=tk.NORMAL)

def load_index(f): 
    
    for w in f.winfo_children(): 
        w.destroy()

    pb = customtkinter.CTkProgressBar(f, orientation="horizontal", mode="indeterminate", width = 250 )
    pb.grid(column = 0, row = 0, columnspan = 1, padx = 20, pady= 10)
    pb.start()
    message_label = customtkinter.CTkLabel(f, text="Finding ChromaDB file...", font = default_font)
    message_label.grid(column=0, row=1, columnspan=1, padx = 20, pady = 10)

    path = Path("./chroma_db")
    global index 
    #There is no chroma_db file found. Continue creating the vector DB.
    if not path.is_dir():
        message_label.configure(text="ChromaDB file missing! Creating DB...")
        load_documents_in_bg(pb)
    else: 
        
    #directly import the db file
        message_label.configure(text="ChromaDB file found! Loading index...")
        root.update_idletasks()
        index = VectorStoreIndex.from_vector_store(
            vector_store= vector_store, 
            storage_context=storage_context, 
            embed_model=embed_model, 
            service_context=service_context
            )

    global query_engine
    query_engine = index.as_query_engine(text_qa_template=QA_TEMPLATE)

    pb.configure(mode="determinate", progress_color="green")
    pb.set(1)
    pb.stop()
    root.update_idletasks()
    message_label.configure(text="Index loaded successfully!")
    button = customtkinter.CTkButton(f, text = 'Query', command = lambda :query_function(f), state=tk.NORMAL)
    button.grid(column = 0, row = 2, padx=20,  pady=10)

def intro_page(f):
    #destroy all previous widgets
    for w in f.winfo_children(): 
        w.destroy()
    
    x = chroma_collection.get(
        where={"file_name" : "details_understandingwar.org_20220228.pdf"},
        include=['metadatas']
    )

    insert = customtkinter.CTkButton(f, text="Insert Documents", command = lambda: add_docs_intro(f), state=tk.NORMAL,fg_color="green")
    insert.grid(column=1, row=0, columnspan=2, padx= 20, pady = 20)
    delete = customtkinter.CTkButton(f, text="Delete Documents", command = lambda: delete_docs_intro(f), state=tk.NORMAL,fg_color="red")
    delete.grid(column=3, row=0, columnspan=2, padx= 20, pady = 20)
    start = customtkinter.CTkButton(f, text="Start", command = lambda: load_index(f), state=tk.NORMAL)
    start.grid(column=5, row=0, columnspan=2, padx= 20, pady = 20)

    
template = (
    "USER: We have provided the context information below. \n"
    "-----------------------------------\n"
    "{context_str}"
    "\n----------------------------------\n"
    "Given this context, please answer this question: {query_str}\n"
    "If the context is insufficient to answer my question, tell me so. \
    Simply tell me 'I am unable to answer this question with this context.' \
    Otherwise, just give me the answer without preamble. \
    Do not attempt to do any calculations or try to extrapolate data.\n"
    "ASSISTANT: "
)

QA_TEMPLATE = Prompt(template)

db = chromadb.PersistentClient(path="./chroma_db")

llm = LlamaCpp(
        model_path=r'.\models\Wizard-Vicuna-30B-Uncensored.ggmlv3.q2_K.bin', 
        verbose=False,
        n_ctx=2048,
        n_gpu_layers=55,
        n_batch=512,
        n_threads=11,
        temperature=0.55)

embed_model = LangchainEmbedding(HuggingFaceEmbeddings(
        model_name=r".\models\all-mpnet-base-v2"
    ))

llm_predictor = LLMPredictor(llm=llm)
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, chunk_size = 300, embed_model=embed_model)
chroma_collection = db.get_or_create_collection("index")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, 
        chunk_size = 512, 
        embed_model=embed_model
        )

root = customtkinter.CTk()
root.title("Demo")
default_font = customtkinter.CTkFont(size=20)
root.option_add("*Font", default_font)
root.grid() 
frame = tk.Frame(root)
frame.grid(column=0, row=0)
message_label = customtkinter.CTkLabel(frame, text="Files loaded!", font = default_font)
message_label.grid(column=0, row=0, columnspan=2, pady=10)

button = customtkinter.CTkButton(frame, text="Start", command= lambda: intro_page(frame), state=tk.NORMAL, fg_color="green")
button.grid(column=0, row=1, columnspan=2, padx=10, pady=10)

index = None
root.mainloop()

