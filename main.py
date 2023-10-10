from langchain.document_loaders import PyPDFLoader, UnstructuredPDFLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.qa_with_sources.loading import load_qa_with_sources_chain, BaseCombineDocumentsChain
from langchain.tools import BaseTool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from pydantic import Field
import os
import trafilatura

def _get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20,
        length_function=len,
    )

class WebpageQATool(BaseTool):
    name = "query_webpage"
    description = "Browse a webpage and retrieve the information relevant to the question."
    text_splitter: RecursiveCharacterTextSplitter = Field(default_factory=_get_text_splitter)
    qa_chain: BaseCombineDocumentsChain
    
    def _run(self, question: str) -> str:
        result = trafilatura.extract(trafilatura.fetch_url(url))
        docs = [Document(page_content=result, metadata={"source": url})]
        web_docs = self.text_splitter.split_documents(docs)
        results = []
        for i in range(0, len(web_docs), 4):
            input_docs = web_docs[i:i+4]
            window_result = self.qa_chain({"input_documents": input_docs, "question": question}, return_only_outputs=True)
            results.append(f"Response from window {i} - {window_result}")
        results_docs = [Document(page_content="\n".join(results), metadata={"source": url})]
        return self.qa_chain({"input_documents": results_docs, "question": question}, return_only_outputs=True)
    
    async def _arun(self, url: str, question: str) -> str:
        raise NotImplementedError

llm = ChatOpenAI(temperature=1.0)        
query_website_tool = WebpageQATool(qa_chain=load_qa_with_sources_chain(llm))
url = "www.altacademy.org"
print(query_website_tool.run("what are there pricings"))

# PDF-related code
loader = UnstructuredPDFLoader("book.pdf")
pages = loader.load_and_split()
embeddings = OpenAIEmbeddings()
docsearch = Chroma.from_documents(pages, embeddings).as_retriever()

query = "Who is Rich Dad?"
docs = docsearch.get_relevant_documents(query)
chain = load_qa_chain(ChatOpenAI(temperature=0), chain_type="stuff")
output = chain.run(input_documents=docs, question=query)
print(output)
