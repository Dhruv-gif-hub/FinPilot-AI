from numpy import ndarray
from sentence_transformers import SentenceTransformer

from ...models.object_models.pdf_chunks import PDFChunks

embed_model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def get_embeddings(texts: list[PDFChunks]) -> ndarray:
    texts_list = [text.content for text in texts]
    embeddings = embed_model.encode_document(texts_list,
                                        batch_size=32,
                                        normalize_embeddings=True,
                                        show_progress_bar=False)
    return embeddings

def query_embeddings(query: str) -> ndarray:
    query_embedding = embed_model.encode_query([query],
                                        normalize_embeddings=True,
                                        show_progress_bar=False)
    return query_embedding