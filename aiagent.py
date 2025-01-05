import os
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, util

class DocumentQAAgent:
    def __init__(self, document_path):
        
        self.document = self.load_document(document_path)
        self.chunks = self.split_into_chunks(self.document)

        self.qa_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-cased-distilled-squad")
        self.qa_model = AutoModelForQuestionAnswering.from_pretrained("distilbert-base-cased-distilled-squad")
        self.qa_pipeline = pipeline("question-answering", model=self.qa_model, tokenizer=self.qa_tokenizer)

        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

        self.similarity_model = SentenceTransformer("all-MiniLM-L6-v2")

    def load_document(self, document_path):
        
        if not os.path.exists(document_path):
            raise FileNotFoundError(f"Document not found: {document_path}")
        with open(document_path, "r", encoding="utf-8") as file:
            return file.read()

    def split_into_chunks(self, document):
        
        return document.split("\n\n")  

    def find_relevant_chunk(self, question):
        
        question_embedding = self.similarity_model.encode(question, convert_to_tensor=True)
        chunk_embeddings = self.similarity_model.encode(self.chunks, convert_to_tensor=True)
        similarities = util.cos_sim(question_embedding, chunk_embeddings)[0]
        best_chunk_idx = similarities.argmax().item()
        return self.chunks[best_chunk_idx]

    def generate_comprehensive_answer(self, question, chunk):
        
        # Use the QA pipeline to extract the most relevant span
        try:
            qa_result = self.qa_pipeline(question=question, context=chunk)
            extracted_answer = qa_result['answer']
        except Exception:
            return "I couldn't find a good answer. Please try rephrasing your question."

        # Combine the extracted span with the chunk and summarize
        input_text = f"Question: {question}\nAnswer: {extracted_answer}\nContext: {chunk}"
        try:
            summary = self.summarizer(input_text, max_length=60, min_length=30, do_sample=False)
            return summary[0]['summary_text']
        except Exception:
            return "I couldn't generate a comprehensive answer. Please try rephrasing your question."

    def answer_question(self, question):
        
        relevant_chunk = self.find_relevant_chunk(question)
        return self.generate_comprehensive_answer(question, relevant_chunk)


if __name__ == "__main__":
    
    document_path = "current.txt"

    
    if not os.path.exists(document_path):
        print(f"Error: The document '{document_path}' was not found.")
        exit()

    agent = DocumentQAAgent(document_path)

    print("Ask a question about the document (type 'exit' to quit):")
    while True:
        question = input("\nYou: ")
        if question.lower() == "exit":
            print("Goodbye!")
            break

        answer = agent.answer_question(question)
        print(f"Agent: {answer}")
