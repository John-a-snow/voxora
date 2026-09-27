import os
from typing import List

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer


class MultilingualE5Embedder:
    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-small",
        model_path: str = "onnx/model_int8.onnx",
        max_length: int = 128,
    ):
        self.model_name = model_name
        self.device = "cpu"
        self.max_length = max_length

        project_root = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )
        )

        self.model_path = os.path.join(project_root, model_path)

        tokenizer_path = os.path.join(
            project_root,
            "onnx",
            "tokenizer.json"
        )

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"ONNX model not found: {self.model_path}"
            )

        if not os.path.exists(tokenizer_path):
            raise FileNotFoundError(
                f"Tokenizer not found: {tokenizer_path}"
            )

        session_options = ort.SessionOptions()
        session_options.intra_op_num_threads = 1
        session_options.inter_op_num_threads = 1
        session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        session_options.graph_optimization_level = (
            ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
        )
        session_options.enable_cpu_mem_arena = False

        self.session = ort.InferenceSession(
            self.model_path,
            sess_options=session_options,
            providers=["CPUExecutionProvider"],
        )

        self.tokenizer = Tokenizer.from_file(tokenizer_path)

        self.input_names = {
            item.name for item in self.session.get_inputs()
        }

    def _tokenize(self, texts: List[str]):
        encoded = self.tokenizer.encode_batch(texts)

        input_ids = []
        attention_mask = []
        token_type_ids = []

        for item in encoded:
            ids = item.ids[:self.max_length]
            mask = item.attention_mask[:self.max_length]

            padding_length = self.max_length - len(ids)

            ids = ids + [0] * padding_length
            mask = mask + [0] * padding_length

            input_ids.append(ids)
            attention_mask.append(mask)

            if item.type_ids:
                types = item.type_ids[:self.max_length]
                types = types + [0] * (
                    self.max_length - len(types)
                )
            else:
                types = [0] * self.max_length

            token_type_ids.append(types)

        inputs = {
            "input_ids": np.asarray(
                input_ids,
                dtype=np.int64
            ),
            "attention_mask": np.asarray(
                attention_mask,
                dtype=np.int64
            ),
        }

        if "token_type_ids" in self.input_names:
            inputs["token_type_ids"] = np.asarray(
                token_type_ids,
                dtype=np.int64
            )

        return inputs

    @staticmethod
    def _mean_pool(
        embeddings: np.ndarray,
        attention_mask: np.ndarray
    ) -> np.ndarray:
        mask = attention_mask[..., None].astype(
            np.float32
        )

        summed = np.sum(
            embeddings * mask,
            axis=1
        )

        counts = np.clip(
            np.sum(mask, axis=1),
            1e-9,
            None
        )

        return summed / counts

    @staticmethod
    def _normalize(
        embeddings: np.ndarray
    ) -> np.ndarray:
        norms = np.linalg.norm(
            embeddings,
            axis=1,
            keepdims=True
        )

        return embeddings / np.clip(
            norms,
            1e-12,
            None
        )

    def embed_texts(
        self,
        texts: List[str]
    ) -> np.ndarray:
        if not texts:
            return np.empty(
                (0, 384),
                dtype=np.float32
            )

        inputs = self._tokenize(texts)

        outputs = self.session.run(
            None,
            inputs
        )

        token_embeddings = outputs[0]

        embeddings = self._mean_pool(
            token_embeddings,
            inputs["attention_mask"]
        )

        embeddings = self._normalize(
            embeddings
        )

        return embeddings.astype(
            np.float32
        )

    def embed_text(
        self,
        text: str
    ) -> np.ndarray:
        return self.embed_texts([text])

    def embed_query(
        self,
        text: str
    ) -> np.ndarray:
        return self.embed_texts(
            ["query: " + text]
        )

    def embed_passages(
        self,
        texts: List[str]
    ) -> np.ndarray:
        return self.embed_texts(
            ["passage: " + text for text in texts]
        )

    def embed_documents(
        self,
        texts: List[str]
    ) -> np.ndarray:
        return self.embed_passages(texts)