from typing import List

try:
    from sentence_transformers import SentenceTransformer

    _model = SentenceTransformer("all-MiniLM-L6-v2")

    def _encode(texts: List[str]) -> List[List[float]]:
        return _model.encode(texts).tolist()
except ImportError:
    from transformers import AutoModel, AutoTokenizer
    import torch

    _tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    _base_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    def _mean_pooling(model_output, attention_mask: torch.Tensor) -> torch.Tensor:
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def _encode(texts: List[str]) -> List[List[float]]:
        encodings = _tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        outputs = _base_model(**encodings)
        embeddings = _mean_pooling(outputs, encodings["attention_mask"])
        return embeddings.detach().cpu().tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Takes a list of strings and returns a list of vector embeddings.
    """
    return _encode(texts)