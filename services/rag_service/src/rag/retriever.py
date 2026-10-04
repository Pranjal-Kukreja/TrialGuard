from src.rag.embeddings import (
    EmbeddingService
)

from src.rag.vector_store import (
    VectorStore
)


class Retriever:

    def __init__(
        self,
        embedder=None,
        store=None
    ):

        self.embedder = (
            embedder
            or EmbeddingService()
        )

        self.store = (
            store
            or VectorStore(
                self.embedder
            )
        )

    def retrieve_trial(
        self,
        query: str,
        trial_id: str,
        k: int = 6
    ):

        embedding = (
            self.embedder
            .embed_query(query)
        )

        # Never request more results than
        # exist in this trial if possible.
        result = (
            self.store
            .trials
            .query(
                query_embeddings=[
                    embedding
                ],

                n_results=k,

                where={
                    "trial_id":
                        trial_id
                }
            )
        )

        return self._format(
            result
        )

    def retrieve_fda(
        self,
        query: str,
        k: int = 4
    ):

        embedding = (
            self.embedder
            .embed_query(query)
        )

        result = (
            self.store
            .fda
            .query(
                query_embeddings=[
                    embedding
                ],

                n_results=k
            )
        )

        return self._format(
            result
        )

    @staticmethod
    def _format(
        result
    ):

        if not result:
            return []

        documents = result.get(
            "documents",
            []
        )

        if (
            not documents
            or not documents[0]
        ):

            return []

        ids = result["ids"][0]
        docs = result[
            "documents"
        ][0]

        metadatas = result[
            "metadatas"
        ][0]

        distances = result.get(
            "distances",
            [[]]
        )[0]

        output = []

        for index, text in enumerate(
            docs
        ):

            distance = (
                distances[index]
                if index
                < len(distances)
                else None
            )

            output.append({
                "chunk_id":
                    ids[index],

                "text":
                    text,

                "metadata":
                    metadatas[index],

                "distance":
                    distance
            })

        return output