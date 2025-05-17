# utils/file_utils.py

import shutil
from pathlib import Path
import json
import numpy as np
import pickle

import config

def ensure_chat_dir(chat_id: int) -> Path:
    """
    Создаёт и возвращает корневую папку для хранения данных чата.
    """
    chat_dir = config.DATA_DIR / str(chat_id)
    (chat_dir / "raw_texts").mkdir(parents=True, exist_ok=True)
    return chat_dir

def next_doc_id(chat_id: int) -> int:
    """
    Находит максимальный существующий doc_id и возвращает +1.
    """
    raw_dir = config.DATA_DIR / str(chat_id) / "raw_texts"
    if not raw_dir.exists():
        return 1
    ids = []
    for p in raw_dir.glob("*.txt"):
        stem = p.stem
        parts = stem.split("_", 1)
        if parts[0].isdigit():
            ids.append(int(parts[0]))
    return max(ids, default=0) + 1

def save_raw_text(chat_id: int, file_name: str, content: bytes) -> Path:
    """
    Сохраняет загруженный .txt-файл под уникальным именем и возвращает путь.
    """
    chat_dir = ensure_chat_dir(chat_id)
    doc_id = next_doc_id(chat_id)
    saved = chat_dir / "raw_texts" / f"{doc_id}_{file_name}"
    with open(saved, "wb") as f:
        f.write(content)
    return saved

def clear_chat_data(chat_id: int) -> None:
    """
    Удаляет всю папку чата целиком.
    """
    chat_dir = config.DATA_DIR / str(chat_id)
    if chat_dir.exists():
        shutil.rmtree(chat_dir)

def save_json(path: Path, obj) -> None:
    """
    Сохраняет объект в JSON.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def load_json(path: Path):
    """
    Загружает JSON-объект из файла.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_segments_vectors(chat_id: int, segments_map: dict, vectors_map: dict) -> None:
    """
    Сохраняет segments.pkl, vectors.npy и docs.json после обработки.
    """
    chat_dir = config.DATA_DIR / str(chat_id)
    # docs.json: список документов с текстом
    docs = [{"doc_id": doc_id, "text": "\n---\n".join(segs)}
            for doc_id, segs in segments_map.items()]
    save_json(chat_dir / "docs.json", docs)

    # segments.pkl
    with open(chat_dir / "segments.pkl", "wb") as f:
        pickle.dump(segments_map, f)

    # vectors.npy
    np.save(chat_dir / "vectors.npy", vectors_map)

def load_segments_vectors(chat_id: int):
    """
    Загружает segments_map и vectors_map.
    Если файлов нет — возвращает два пустых словаря.
    """
    chat_dir = config.DATA_DIR / str(chat_id)
    try:
        with open(chat_dir / "segments.pkl", "rb") as f:
            segments_map = pickle.load(f)
    except FileNotFoundError:
        segments_map = {}

    try:
        vectors_map = np.load(chat_dir / "vectors.npy", allow_pickle=True).item()
    except (FileNotFoundError, ValueError):
        vectors_map = {}

    return segments_map, vectors_map

def list_docs(chat_id: int) -> list[tuple[int, str]]:
    """
    Возвращает список загруженных файлов из raw_texts:
    [(doc_id, original_name_with_ext), ...]
    Поддерживаются любые расширения (txt, pdf, docx, jpg, png и т.п.).
    """
    raw_dir = config.DATA_DIR / str(chat_id) / "raw_texts"
    out = []
    if not raw_dir.exists():
        return out

    for p in sorted(raw_dir.iterdir()):
        # берём все файлы, у которых имя начинается с "<doc_id>_"
        parts = p.name.split("_", 1)
        if len(parts) != 2:
            continue
        id_part, orig_name = parts
        if not id_part.isdigit():
            continue
        doc_id = int(id_part)
        out.append((doc_id, orig_name))
    return out


def delete_doc(chat_id: int, doc_id: int) -> None:
    """
    Удаляет файл raw_texts/{doc_id}_*, а также обновляет segments и vectors.
    """
    chat_dir = config.DATA_DIR / str(chat_id)
    raw_dir = chat_dir / "raw_texts"
    # Удалить все файлы с данным doc_id
    for p in raw_dir.glob(f"{doc_id}_*"):
        try:
            p.unlink()
        except FileNotFoundError:
            pass

    # Пересохранить maps без этого документа
    segments_map, vectors_map = load_segments_vectors(chat_id)
    segments_map.pop(doc_id, None)
    vectors_map.pop(doc_id, None)
    save_segments_vectors(chat_id, segments_map, vectors_map)
