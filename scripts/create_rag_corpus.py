import os
import sys
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr
import vertexai

PROJECT_ID = "qwiklabs-gcp-03-61708ee92f67"
LOCATION = "us-central1"
GCS_PATH = "gs://travel-destination-explorer-media-61708/rag/pg49513.txt"

PARSING_PROMPT = (
    "Extract the individual useful facts, travel details, historical notes, plant descriptions, and remedy instructions. "
    "Ignore and omit all Gutenberg license metadata, header/footer boilerplate, and formatting artifacts. "
    "Output clean, self-contained prose."
)

def main():
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print("1. Updating RAG Engine config to serverless mode...")
    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    rag.update_rag_engine_config(
        rag_engine_config=rag.RagEngineConfig(
            name=cfg,
            rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
        )
    )

    print("2. Creating serverless RAG corpus...")
    corpus = rag.create_corpus(
        display_name="travel-guide-corpus",
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    corpus_name = corpus.name
    print("Created Corpus Name:", corpus_name)

    print("3. Importing file into RAG corpus...")
    resp = rag.import_files(
        corpus_name=corpus_name,
        paths=[GCS_PATH],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-2.5-flash",
            custom_parsing_prompt=PARSING_PROMPT,
        ),
    )
    print(f"Import complete! Imported file count: {resp.imported_rag_files_count}")

    with open("corpus_name.txt", "w") as f:
        f.write(corpus_name)

if __name__ == "__main__":
    main()
