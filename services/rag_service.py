# services/rag_service.py

import logging
import config
import utils.file_utils as fu
from services.segmenter import TextSegmenter
from services.llm_judge import humanize_answer

logger = logging.getLogger(__name__)

# один раз инициализируем сегментер
_segmenter = TextSegmenter(
    segment_size=50,
    use_student=False,
    student_ckpt="mini_frida.pt",
    device=config.DEVICE,
)
_segmenter.vectorize_batch_size = 64  # батчи по 64 сегмента

def process_text(chat_id: int, text: str, orig_name: str, doc_id: int) -> int:
    logger.info("process_text: start for doc_id=%d, orig_name=%s", doc_id, orig_name)

    # 1) разбиваем на предложения
    sentences = _segmenter.split_text(text)
    logger.info("process_text: split_text -> %d sentences", len(sentences))

    # 2) группируем в сегменты
    segments = _segmenter.segment_text(sentences)
    logger.info("process_text: segment_text -> %d segments", len(segments))

    # 3) векторизуем батчами
    try:
        logger.info("process_text: calling vectorize")
        vectors = _segmenter.vectorize(segments)
        logger.info("process_text: vectorize returned %s embeddings", vectors.shape)
    except Exception as e:
        logger.error("process_text: vectorize failed: %s", e, exc_info=True)
        raise

    # 4) сохраняем карты сегментов и векторов
    try:
        segments_map, vectors_map = fu.load_segments_vectors(chat_id)
        segments_map[doc_id] = segments
        vectors_map[doc_id]  = vectors
        fu.save_segments_vectors(chat_id, segments_map, vectors_map)
        logger.info("process_text: saved segments/vectors for doc_id=%d", doc_id)
    except Exception as e:
        logger.error("process_text: saving failed: %s", e, exc_info=True)
        raise

    logger.info("process_text: finished for doc_id=%d", doc_id)
    return doc_id

def find_answer(chat_id: int, doc_id: int, question: str) -> str:
    segments_map, vectors_map = fu.load_segments_vectors(chat_id)
    if doc_id not in segments_map:
        return "❗ Документ не найден. Выберите файл в «Мои документы»."
    segments = segments_map[doc_id]
    vectors  = vectors_map[doc_id]
    frags = _segmenter.find_relevant_segments(question, vectors, segments, top_n=3)
    answer = humanize_answer(question, *frags) if frags else "❗ Не нашёл ответ в этом документе."
    return answer
