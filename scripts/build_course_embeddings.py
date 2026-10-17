#!/usr/bin/env python3
"""
Build course embeddings for semantic search.

Embeds every course (title + description) in data/utd_courses.json with
Amazon Titan Text Embeddings V2 on Bedrock and writes:
  data/course_embeddings.npy       - (num_courses, dims) float32, unit-length rows
  data/course_embedding_ids.json   - course codes in the same row order

Run from the project root:  python scripts/build_course_embeddings.py
Re-run whenever the course catalog changes.
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.course_catalog_agent.course_catalog_agent import (
    EMBEDDINGS_FILE, EMBEDDING_IDS_FILE, course_embedding_text
)
from src.core.aws.bedrock_service import BedrockService

COURSES_FILE = "data/utd_courses.json"
MAX_WORKERS = 8  # Titan embeds one text per call, so parallelize the calls


def main():
    with open(COURSES_FILE, 'r', encoding='utf-8') as f:
        courses = json.load(f)["courses"]

    codes = [course.get("course_code") or f"{course['prefix']} {course['number']}" for course in courses]
    texts = [course_embedding_text(course) for course in courses]

    bedrock = BedrockService()
    print(f"🔢 Embedding {len(texts)} courses with {bedrock.embedding_model_id}...")

    done = 0

    def embed(text):
        nonlocal done
        vector = bedrock.embed_text(text)
        done += 1
        if done % 250 == 0:
            print(f"  {done}/{len(texts)}")
        return vector

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        vectors = list(pool.map(embed, texts))

    matrix = np.array(vectors, dtype=np.float32)
    np.save(EMBEDDINGS_FILE, matrix)
    with open(EMBEDDING_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(codes, f)

    print(f"✅ Saved {matrix.shape} embeddings to {EMBEDDINGS_FILE}")


if __name__ == "__main__":
    main()
