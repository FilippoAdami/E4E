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

def split_text(pages, min_chars=50, overlap_ratio=0.1):
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
                # Compute overlap using words so we don't cut words in half
                overlap_size = int(min_chars * overlap_ratio)
                words = current_chunk.split()
                overlap_words = " ".join(words[-overlap_size:]) if len(words) > overlap_size else current_chunk
                # Start new chunk with overlap; update metadata: keep the smallest page number
                current_chunk = overlap_words + " " + sentence
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

def compute_cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def compute_local_similarities(embeddings):
    """Compute similarity between each chunk and its right neighbor."""
    similarities = []
    for i in range(len(embeddings) - 1):
        sim = compute_cosine_similarity(embeddings[i], embeddings[i + 1])
        similarities.append(sim)
    return similarities

def compute_global_similarity(embeddings, num_samples=8, max_iterations=20, tolerance=0.05):
    """
    Estimate global similarity by sampling random pairs of non-neighboring chunks.
    This avoids an O(n^2) computation while reaching a stable average.
    """
    prev_avg = 0
    for _ in range(max_iterations):
        sample_indices = random.sample(range(len(embeddings)), min(num_samples, len(embeddings)))
        similarities = [
            compute_cosine_similarity(embeddings[i], embeddings[j])
            for i, j in zip(sample_indices[:-1], sample_indices[1:]) if abs(i - j) > 1
        ]
        avg_similarity = np.mean(similarities) if similarities else 0
        if abs(avg_similarity - prev_avg) < tolerance:
            break
        prev_avg = avg_similarity
    return avg_similarity

def merge_chunks(chunks, embeddings, threshold):
    """
    Merge neighboring chunks if their similarity exceeds threshold.
    Each chunk is a tuple (text, metadata) where metadata = {"page": int}.
    When merging, the resulting metadata 'page' is the minimum of the two.
    """
    merged_chunks = []
    merged_embeddings = []
    
    i = 0
    while i < len(chunks):
        current_text, current_metadata = chunks[i]
        current_embedding = embeddings[i]
        
        while i < len(embeddings) - 1:
            next_text, next_metadata = chunks[i + 1]
            next_similarity = compute_cosine_similarity(current_embedding, embeddings[i + 1])
            if next_similarity < threshold:
                break  # Stop merging if similarity is too low
            
            # Merge the texts
            current_text = current_text + " " + next_text
            # Update embedding by averaging
            current_embedding = (current_embedding + embeddings[i + 1]) / 2
            # Update metadata: take the smallest page number, ignoring 0 values
            current_page = current_metadata["page"]
            next_page = next_metadata["page"]
            if current_page == 0:
                current_page = next_page
            elif next_page != 0:
                current_page = min(current_page, next_page)
            current_metadata = {"page": current_page}
            i += 1  # Move to the next chunk
        merged_chunks.append((current_text.strip(), current_metadata))
        merged_embeddings.append(current_embedding)
        i += 1  # Move to the next unmerged chunk
    
    return merged_chunks, merged_embeddings

def iterative_merging(chunks, model_name="sentence-transformers/all-mpnet-base-v2"):
    """
    Perform iterative merging until dissimilarity stops improving.
    Uses SentenceTransformer for computing embeddings.
    Chunks are tuples (text, metadata).
    """
    # Extract text for embedding
    texts = [chunk[0] for chunk in chunks]
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    local_similarities = compute_local_similarities(embeddings)
    global_similarity = compute_global_similarity(embeddings)
    avg_local_similarity = np.mean(local_similarities) if local_similarities else 0
    
    while True:
        # Set threshold slightly above average local similarity
        threshold = avg_local_similarity * 1.05  
        prev_global_similarity = global_similarity

        new_chunks, new_embeddings = merge_chunks(chunks, embeddings, threshold)
        
        new_local_similarities = compute_local_similarities(new_embeddings)
        new_avg_local_similarity = np.mean(new_local_similarities) if new_local_similarities else 0
        new_global_similarity = compute_global_similarity(new_embeddings)
        
        print(f"Global Sim: {new_global_similarity:.4f}, Avg Local Sim: {new_avg_local_similarity:.4f}, Chunks: {len(new_chunks)}")
        
        # Stop if further merging doesn't improve (i.e. increases global similarity)
        if new_global_similarity >= prev_global_similarity or new_avg_local_similarity >= avg_local_similarity:
            break
        else:
            chunks = new_chunks
            embeddings = new_embeddings
            local_similarities = new_local_similarities
            avg_local_similarity = new_avg_local_similarity
            global_similarity = new_global_similarity
    
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

