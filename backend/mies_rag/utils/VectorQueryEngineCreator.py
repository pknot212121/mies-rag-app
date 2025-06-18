import os
from llama_index.llms.openai import OpenAI 
from llama_parse import LlamaParse 
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.core import VectorStoreIndex, StorageContext, get_response_synthesizer, load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine


class VectorQueryEngineCreator:
    def __init__(self, model, input_path):
        self.model = model
        self.input_path = input_path

    def parse_pdf_to_nodes(self, path_to_pdf):
        documents = LlamaParse(
            api_key=os.getenv("LLAMA_PARSE_API_KEY"),
            result_type="markdown"
        ).load_data(path_to_pdf)
        node_parser = MarkdownElementNodeParser(
            llm=OpenAI(model=self.model), num_workers=8
        )
        nodes = node_parser.get_nodes_from_documents(documents)
        
        # Remove chapters containing references
        documents = [doc for doc in documents if 'references' not in doc.text.lower()]

        return documents, node_parser, nodes

    def create_vector_index(self, documents, node_parser, nodes):
        base_nodes, objects = node_parser.get_nodes_and_objects(nodes)
        vector_index = VectorStoreIndex(base_nodes + objects)
        return vector_index

    def create_vector_query_engine(self, vector_index):
        retriever = VectorIndexRetriever(
            index=vector_index,
            similarity_top_k=5,
        )
        response_synthesizer = get_response_synthesizer()

        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            response_mode='tree_summarize',
            response_synthesizer=response_synthesizer,
        )
        return query_engine

    def get_query_engine(self, file):
        pdf_path = os.path.join(self.input_path, f"{file}.pdf")
        documents, node_parser, nodes = self.parse_pdf_to_nodes(pdf_path)
        vector_index = self.create_vector_index(documents, node_parser, nodes)
        
        query_engine = self.create_vector_query_engine(vector_index)
        return query_engine
