# models

This directory holds no model files and nothing in the code loads from it.

The embedding model is `BAAI/bge-small-en-v1.5` (see `src/rag/embeddings.py`). `sentence-transformers` downloads it from Hugging Face on first use and caches it in the user cache directory, outside the repo. The first index build or API start therefore needs network access (or a pre-populated Hugging Face cache).

Do not commit model weights. See `../README.md` for how to build the vector index.
