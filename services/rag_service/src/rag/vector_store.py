from pathlib import Path

import chromadb


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


DEFAULT_DB_PATH = (
    PROJECT_ROOT
    / "vector_db"
    / "chroma"
)


class VectorStore:

    def __init__(
        self,
        embedder,
        path=None
    ):

        self.embedder = embedder

        db_path = (
            Path(path)
            if path
            else DEFAULT_DB_PATH
        )

        db_path.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            f"Chroma DB: {db_path}"
        )

        self.client = (
            chromadb.PersistentClient(
                path=str(db_path)
            )
        )

        self.trials = (
            self.client
            .get_or_create_collection(
                name="trialguard_trials",
                metadata={
                    "hnsw:space":
                        "cosine"
                }
            )
        )

        self.fda = (
            self.client
            .get_or_create_collection(
                name=(
                    "trialguard_fda_labels"
                ),
                metadata={
                    "hnsw:space":
                        "cosine"
                }
            )
        )

    def add_trial_chunks(
        self,
        chunks
    ):

        if not chunks:
            return

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = (
            self.embedder
            .embed_documents(texts)
        )

        self.trials.upsert(
            ids=[
                chunk["chunk_id"]
                for chunk in chunks
            ],

            documents=texts,

            embeddings=embeddings,

            metadatas=[
                {
                    "trial_id":
                        chunk["trial_id"],

                    "section":
                        chunk["section"],

                    "source":
                        chunk["source"]
                }

                for chunk in chunks
            ]
        )

    def add_fda_chunks(
        self,
        chunks
    ):

        if not chunks:
            return

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = (
            self.embedder
            .embed_documents(texts)
        )

        metadatas = []

        for chunk in chunks:

            drug_names = (
                chunk.get(
                    "drug_names",
                    []
                )
            )

            metadatas.append({
                "document_id":
                    chunk[
                        "document_id"
                    ],

                "section":
                    chunk[
                        "section"
                    ],

                "source":
                    chunk[
                        "source"
                    ],

                # Chroma metadata should stay scalar.
                "drug_names":
                    " | ".join(
                        str(name)
                        for name
                        in drug_names
                    )
            })

        self.fda.upsert(
            ids=[
                chunk["chunk_id"]
                for chunk in chunks
            ],

            documents=texts,

            embeddings=embeddings,

            metadatas=metadatas
        )