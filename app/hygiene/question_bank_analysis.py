import numpy as np

from app.ai.embedding_service import generate_embedding


def cosine_similarity(a, b):

    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def detect_duplicate_questions(questions):

    embeddings = []

    duplicates = []

    for q in questions:

        emb = generate_embedding(q["text"])

        for prev in embeddings:

            sim = cosine_similarity(prev["embedding"], emb)

            if sim > 0.92:

                duplicates.append(
                    {
                        "original": prev["question"],
                        "duplicate": q,
                        "similarity": sim,
                    }
                )

        embeddings.append(
            {
                "question": q,
                "embedding": emb,
            }
        )

    return duplicates
