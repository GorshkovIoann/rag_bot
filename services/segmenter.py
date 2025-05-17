import nltk
import torch
import logging
import numpy as np
import torch.nn.functional as F
from transformers import AutoTokenizer, T5EncoderModel
from sklearn.neighbors import NearestNeighbors

logger = logging.getLogger(__name__)

#from simple_proj2.student_distill import MiniFRIDA  # ваша distilled-модель

nltk.download('punkt')  # Раскомментируйте при первом запуске

class TextSegmenter:
    """
    Разбивает тексты на сегменты и векторизует их
    через оригинальную FRIDA или через MiniFRIDA.
    """
    def __init__(
        self,
        model_name: str = "ai-forever/FRIDA",
        device: str = "cuda",
        segment_size: int = 50,
        use_student: bool = False,
        student_ckpt: str = "mini_frida.pt"
    ):
        
        self.vectorize_batch_size = 64  
        self.device = torch.device(device)
        self.segment_size = segment_size
        self.use_student = use_student

        # всегда одинаковый токенизатор
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = T5EncoderModel.from_pretrained(model_name).to(device)

    def split_text(self, text: str) -> list[str]:
        if isinstance(text, tuple):
            text = " ".join(text)
        elif not isinstance(text, str):
            raise ValueError("`text` must be a string or tuple of strings")
        return nltk.tokenize.sent_tokenize(text)

    def segment_text(self, sentences: list[str]) -> list[str]:
        segments, temp, count = [], [], 0
        for sent in sentences:
            words = sent.split()
            temp.append(sent)
            count += len(words)
            if count >= self.segment_size:
                segments.append(" ".join(temp))
                temp, count = [], 0
        if temp:
            segments.append(" ".join(temp))
        return segments

    # services/segmenter.py  (отрезок vectorize)

    def vectorize(self, segments: list[str], prompt_name: str = "search_document") -> np.ndarray:
        """
        Возвращает numpy-array [n_segments × dim], батчами по vectorize_batch_size.
        """
        all_embs = []
        total = len(segments)
        logger.info("Начало векторизации %d сегментов батчами по %d", total, self.vectorize_batch_size)
        for i in range(0, total, self.vectorize_batch_size):
            batch = segments[i : i + self.vectorize_batch_size]
            logger.info("  Векторизуем сегменты %d–%d", i, i+len(batch))
            toks = self.tokenizer(
                [f"{prompt_name}: {seg}" for seg in batch],
                max_length=512, padding=True, truncation=True, return_tensors="pt"
            ).to(self.device)
            logger.info("  токенизировали %d–%d", i, i+len(batch))
            with torch.no_grad():
                out = self.model(input_ids=toks["input_ids"], attention_mask=toks["attention_mask"])
            embs = out.last_hidden_state[:, 0]
            embs = F.normalize(embs, p=2, dim=1).cpu().numpy()
            all_embs.append(embs)
            logger.info("  векторизовали %d–%d", i, i+len(batch))
        result = np.vstack(all_embs) if all_embs else np.zeros((0, self.model.config.hidden_size))
        logger.info("Векторизация завершена, получено %s эмбеддингов", result.shape)
        return result


    def find_relevant_segments(
        self,
        query: str,
        segment_vectors,
        segments: list[str],
        top_n: int = 3
    ) -> list[str]:
        qv = self.vectorize([query], prompt_name="search_query")
        n = min(top_n, len(segments))
        if n == 0:
            return []
        nn = NearestNeighbors(n_neighbors=n, metric="cosine")
        nn.fit(segment_vectors)
        _, idx = nn.kneighbors(qv)
        return [segments[i] for i in idx[0]]
