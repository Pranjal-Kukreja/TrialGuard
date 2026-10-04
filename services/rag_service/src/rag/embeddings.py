from sentence_transformers import (
    SentenceTransformer
)


class EmbeddingService:

    def __init__(
        self,
        model_name=(
            "BAAI/bge-small-en-v1.5"
        )
    ):

        print(
            f"Loading embedding model: "
            f"{model_name}"
        )

        self.model = (
            SentenceTransformer(
                model_name
            )
        )

    def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:

        if not texts:
            return []

        embeddings = (
            self.model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False
            )
        )

        return embeddings.tolist()

    def embed_query(
        self,
        text: str
    ) -> list[float]:

        embedding = (
            self.model.encode(
                [text],
                normalize_embeddings=True,
                show_progress_bar=False
            )[0]
        )

        return embedding.tolist()