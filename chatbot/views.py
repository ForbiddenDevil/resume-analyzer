import time
from django.conf import settings
from django.shortcuts import render
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.files.base import ContentFile
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
from django.core.files.storage import default_storage
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import FunctionTool
from llama_index.core.vector_stores import MetadataFilters, FilterCondition
from typing import List, Optional
from llama_index.agent.openai import OpenAIAgent
from llama_index.embeddings.openai import OpenAIEmbedding
import chromadb
import shutil
import os

load_dotenv()


# ---------------------------------------
#  Gen AI
# ---------------------------------------
def create_indexing():
    # Set the directory path where your PDF files are located
    pdf_directory = os.path.join(default_storage.location, "chatbot/uploads")

    # Set the directory to store the index
    index_directory = os.path.join(default_storage.location, "chatbot/index")

    # Create a SimpleDirectoryReader to read PDF files from the directory
    documents = SimpleDirectoryReader(pdf_directory).load_data()

    print("len of doc: ", len(documents))

    splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=100)
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"Length of nodes : {len(nodes)}")

    db = chromadb.PersistentClient(path=index_directory)
    chroma_collection = db.get_or_create_collection("multidocument-agent")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    # vector_index = VectorStoreIndex(nodes, storage_context=storage_context)

    # define embedding function
    embed_model = OpenAIEmbedding(
        model_name="text-embedding-3-small", embed_batch_size=10
    )

    vector_index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, embed_model=embed_model
    )

    # Save the index to the specified directory
    vector_index.storage_context.vector_store.persist(persist_path=index_directory)

    print(f"Index created and saved for {len(documents)} PDF files.")


def vector_query(query: str, page_numbers: Optional[List[str]] = None):
    # Set the directory where the index is stored
    index_directory = os.path.join(default_storage.location, "chatbot/index")

    # define embedding function
    embed_model = OpenAIEmbedding(
        model_name="text-embedding-3-small", embed_batch_size=10
    )

    # load from disk
    db2 = chromadb.PersistentClient(path=index_directory)
    chroma_collection = db2.get_or_create_collection("multidocument-agent")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    vector_index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )

    page_numbers = page_numbers or []
    metadata_dict = [{"key": "page_label", "value": p} for p in page_numbers]

    query_engine = vector_index.as_query_engine(
        similarity_top_k=2,
        filters=MetadataFilters.from_dicts(metadata_dict, condition=FilterCondition.OR),
    )

    return query_engine.query(query)


def delete_directory(path):
    try:
        # Check if the path exists
        if os.path.exists(path):
            # Check if it's a directory
            if os.path.isdir(path):
                # Remove the directory and all its contents
                shutil.rmtree(path)
                print(f"Directory '{path}' has been successfully deleted.")
            else:
                print(f"'{path}' is not a directory.")
        else:
            print(f"The path '{path}' does not exist.")
    except Exception as e:
        print(f"An error occurred while deleting the directory: {e}")


# Create your views here.
def chatbot_page(request):
    if request.method == "POST":

        files = request.FILES.getlist("files")
        file_list = []

        # delete the existing directory
        # delete_directory(settings.CB_MEDIA_ROOT)

        for f in files:
            file_name = f.name
            path = default_storage.save(
                os.path.join(settings.CB_MEDIA_ROOT, file_name), ContentFile(f.read())
            )
            tmp_file = os.path.join(default_storage.location, path)
            file_list.append(tmp_file)

        print("\n\n Now generating indexes...")
        create_indexing()

    return render(request, "chatbot/chatbot.html")


@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")
        vector_query_tool = FunctionTool.from_defaults(
            name=f"vector_tool", fn=vector_query
        )

        initial_tools = [vector_query_tool]
        agent = OpenAIAgent.from_tools(initial_tools, verbose=True)
        response = agent.chat(user_message)
        metadata_dict = (
            response.sources[0].raw_output.metadata if len(response.sources) > 0 else {}
        )
        metadata = []
        for f in metadata_dict.values():
            metadata.append(f"File name: {f['file_name']} - {f['page_label']}")

        return JsonResponse({"response": response.response, "metadata": metadata})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)
