"""
This file will contain helper functions for loading, splitting, merging, and embedding documents.
"""

import re
import random
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings

def clean_text(text):
    """Replace newlines with spaces unless they indicate a paragraph break."""
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)  # Replace single newlines with a space
    text = re.sub(r"\n{2,}", "\n\n", text)  # Preserve paragraph breaks
    return text.strip()

def load_pdf(file_path):
    """Load a PDF and clean text per page."""
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    for page in pages:
        page.page_content = clean_text(page.page_content)
    return pages

def split_text(pages, min_chars=2500):
    """
    Split text into chunks at '.', '\n\n', or after min_chars with overlap.
    Keeps track of page numbers in the metadata.
    Each chunk is a tuple: (text, metadata) where metadata = {"page": int}.
    When a chunk is incomplete (not ending with punctuation), we mark its page as 0 
    so it can later be merged with the next page's content.
    """
    chunks = []
    current_chunk = ""
    current_metadata = None
    page_number = 1  # Track the page number

    for page in pages:
        text = page.page_content
        # Split at sentence boundaries or paragraphs
        sentences = re.split(r'(?<=\.)\s|\n\n', text)

        # If the last chunk was marked as incomplete, merge it with the first sentence of the new page
        if chunks and chunks[-1][1]["page"] == 0 and sentences:
            prev_text, _ = chunks.pop()
            merged_text = prev_text + " " + sentences[0]
            merged_metadata = {"page": page_number}  # use current page number
            chunks.append((merged_text.strip(), merged_metadata))
            sentences = sentences[1:]  # Remove the merged sentence

        for sentence in sentences:
            if current_chunk == "":
                # Start a new chunk and record its page
                current_chunk = sentence
                current_metadata = {"page": page_number}
            elif len(current_chunk) + len(sentence) < min_chars:
                current_chunk += " " + sentence
            else:
                # Save current chunk along with its metadata
                chunks.append((current_chunk.strip(), current_metadata))
                current_metadata = {"page": min(current_metadata["page"], page_number)}
        # End of page: check if the chunk ends with proper punctuation
        if re.search(r"[.!?](”|')?$", current_chunk.strip()):
            chunks.append((current_chunk.strip(), current_metadata))
        else:
            # Mark as incomplete with page 0 to indicate pending merge
            chunks.append((current_chunk.strip(), {"page": 0}))
        current_chunk = ""
        current_metadata = None
        page_number += 1

    return chunks

def compute_cosine_similarity(e1, e2):
    e1 = np.array(e1).reshape(1, -1)
    e2 = np.array(e2).reshape(1, -1)
    sim = cosine_similarity(e1, e2)[0][0]
    return sim

def compute_similarities(embeddings):
    """Compute similarity between each chunk and its right neighbor."""
    similarities = []
    e1 = np.array(embeddings[0]).reshape(1, -1)
    for i in range(len(embeddings) - 1):
        e2 = np.array(embeddings[i + 1]).reshape(1, -1)
        sim = cosine_similarity(e1, e2)[0][0]
        similarities.append(sim)
        e1 = e2
    avg_inter_similarity = np.mean(similarities)
    return similarities, avg_inter_similarity

def iterative_merging(chunks, model_name="sentence-transformers/all-mpnet-base-v2"):
    """
    Perform iterative merging until dissimilarity stops improving.
    Uses SentenceTransformer for computing embeddings.
    Chunks are tuples (text, metadata).
    """
    average_intra_similarity = 0
    average_inter_similarity = 1000
    # Extract text for embedding
    texts = [chunk[0] for chunk in chunks]
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True)

    similarities, avg_inter_similarity = compute_similarities(embeddings)
    print("Initial average inter chunk similarity:", avg_inter_similarity)

    
    similarities_copy = similarities.copy()
    threshold = 0.95
    groups = []
    last_index = 0

    while last_index < len(similarities_copy):  
        current_group = [last_index]  # Start new group
        i = last_index  # Track current position
        
        # Group chunks based on similarity threshold
        while i < len(similarities_copy) and similarities_copy[i] > threshold:
            i += 1  # Move to next similarity entry
            current_group.append(i)
        print(f"Last similarity: {similarities_copy[i]}")

        # Compute average embedding for merged chunks
        average_emb = np.zeros(embeddings.shape[1])
        for j in current_group:
            average_emb += embeddings[j]
        average_emb /= len(current_group)

        # Compute average intra-similarity
        intra_similarities = [compute_cosine_similarity(embeddings[j], average_emb) for j in current_group]
        avg_intra_similarity = np.mean(intra_similarities)

        print(f"Average intra-similarity: {avg_intra_similarity}, Group members: {current_group}")

        groups.append((current_group, average_emb, avg_intra_similarity))

        # Move to the next ungrouped index
        last_index = i + 1  # Skip merged chunks and start a new group

    if last_index < len(embeddings):
        groups.append(([last_index], embeddings[last_index], 1.0))  # Assume self-similarity = 1.0
        print(f"Average intra-similarity: 1.0, Group members: [{last_index}]")
    
    # Compute inter-similarity between merged chunks (lower is better)
    new_inter_similarities = []
    for i in range(len(groups)-1):
        new_inter_similarities.append(compute_cosine_similarity(groups[i][1], groups[i + 1][1]))
    new_avg_inter_similarity = np.mean(new_inter_similarities)

    print(f"New average inter-similarity: {new_avg_inter_similarity}")
    '''
    new_avg_intra_similarity = 0
    for i in enumerate(merged):
        new_avg_intra_similarity += merged[i][2]
    new_avg_intra_similarity = new_avg_intra_similarity / len(merged)

    print(f"Iteration {i}: Average intra-similarity: {new_avg_intra_similarity}, Average inter-similarity: {new_avg_inter_similarity}")

    '''
    return chunks

def generate_final_embeddings(chunks):
    """
    Generate embeddings for text chunks using HuggingFaceEmbeddings.
    Chunks is a list of tuples (text, metadata).
    Returns the HuggingFaceEmbeddings object and a list of embeddings.
    """
    model_name = "sentence-transformers/all-mpnet-base-v2"
    hf_embeddings = HuggingFaceEmbeddings(model_name=model_name)
    final_embeddings = [hf_embeddings.embed_query(chunk[0]) for chunk in chunks]
    return final_embeddings

def semantic_chunking(file_path):
    # Load the source
    pages = load_pdf(file_path)
    chunks = split_text(pages)
    print(f"Loaded {len(chunks)} chunks from {file_path}.")
    
    # Generate embeddings
    final_chunks = iterative_merging(chunks)
    final_chunks_embeddings = generate_final_embeddings(final_chunks)
    print(f"Generated embeddings for {len(final_chunks)} chunks.")
    
    # Prepare documents for MongoDB
    documents = []
    for (text, metadata), embedding in zip(final_chunks, final_chunks_embeddings):
        doc = {
            "text": text,
            "embedding": embedding,
            "metadata": metadata  # Stores page number and other relevant metadata
        }
        documents.append(doc)
    
    return documents
