import logging
import os
import time
from typing import List

import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer


logger = logging.getLogger(__name__)


class MultilingualE5Embedder:
    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-small",
        normalize_embeddings: bool = True
    ):
        self.model_name = model_name
        self.normalize_embeddings = normalize_embeddings
        self.embedding_dim = 384

        start_time = time.time()

        logger.info("Loading ONNX E5 model...")

        model_file = self._get_model_file()

        tokenizer_file = hf_hub_download(
            repo_id=self.model_name,
            filename="onnx/tokenizer.json"
        )

        self.tokenizer = Tokenizer.from_file(tokenizer_file)

        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        options.graph_optimization_level = (
            ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        )

        self.session = ort.InferenceSession(
            model_file,
            sess_options=options,
            providers=["CPUExecutionProvider"]
        )

        self.input_names = {
            item.name for item in self.session.get_inputs()
        }

        self.output_name = self.session.get_outputs()[0].name

        self.load_time_s = round(
            time.time() - start_time,
            3
        )

        logger.info(
            f"ONNX embedder ready in {self.load_time_s}s "
            f"(dimension: {self.embedding_dim})"
        )

    def _get_model_file(self) -> str:
        cpu_info = ""

        try:
            with open("/proc/cpuinfo", "r") as file:
                cpu_info = file.read().lower()
        except OSError:
            pass

        if "avx512_vnni" in cpu_info:
            model_file = "onnx/model_qint8_avx512_vnni.onnx"
        else:
            model_file = "onnx/model_O4.onnx"

        logger.info(f"Using ONNX model: {model_file}")

        return hf_hub_download(
            repo_id=self.model_name,
            filename=model_file
        )

    def _encode(self, texts: List[str]) -> np.ndarray:
        encoded = self.tokenizer.encode_batch(texts)

        input_ids = np.array(
            [item.ids for item in encoded],
            dtype=np.int64
        )

        attention_mask = np.array(
            [item.attention_mask for item in encoded],
            dtype=np.int64
        )

        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }

        if "token_type_ids" in self.input_names:
            inputs["token_type_ids"] = np.zeros_like(
                input_ids,
                dtype=np.int64
            )

        outputs = self.session.run(
            [self.output_name],
            inputs
        )

        hidden_states = outputs[0]

        mask = attention_mask.astype(np.float32)
        mask = np.expand_dims(mask, axis=-1)

        summed = np.sum(
            hidden_states * mask,
            axis=1
        )

        counts = np.clip(
            mask.sum(axis=1),
            a_min=1e-9,
            a_max=None
        )

        embeddings = summed / counts

        if self.normalize_embeddings:
            norms = np.linalg.norm(
                embeddings,
                axis=1,
                keepdims=True
            )

            embeddings = embeddings / np.clip(
                norms,
                a_min=1e-12,
                a_max=None
            )

        return embeddings.astype(np.float32)

    def embed_documents(
        self,
        texts: List[str],
        batch_size: int = 16,
        show_progress: bool = False
    ) -> np.ndarray:

        if not texts:
            return np.empty(
                (0, self.embedding_dim),
                dtype=np.float32
            )

        all_embeddings = []

        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]

            passages = [
                f"passage: {text}"
                for text in batch
            ]

            embeddings = self._encode(passages)
            all_embeddings.append(embeddings)

        return np.vstack(all_embeddings)

    def embed_query(self, query: str) -> np.ndarray:
        text = f"query: {query}"

        embedding = self._encode([text])

        return embedding[0].astype(np.float32)

    def get_embedding_dimension(self) -> int:
        return self.embedding_dim