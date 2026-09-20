import numpy as np


def batch_encode_documents(
    embedder,
    texts,
    batch_size=32,
    show_progress=False
):
    if not texts:
        return np.empty(
            (0, 384),
            dtype=np.float32
        )

    all_embeddings = []

    for start in range(
        0,
        len(texts),
        batch_size
    ):
        batch = texts[
            start:start + batch_size
        ]

        embeddings = embedder.embed_documents(
            batch
        )

        all_embeddings.append(
            embeddings
        )

        if show_progress:
            done = min(
                start + batch_size,
                len(texts)
            )
            print(
                f"Embedded {done}/{len(texts)}"
            )

    return np.vstack(
        all_embeddings
    ).astype(np.float32)