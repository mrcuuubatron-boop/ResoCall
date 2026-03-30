import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Optional


class SemanticSearch:
    """
    Индексирует транскрипции звонков и выполняет поиск по смыслу.
    """
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = {}          # {file_id: embedding}
        self.metadata = {}       # {file_id: metadata (текст, время, путь)}

    def index_file(self, file_id: str, text: str, metadata: Optional[Dict] = None):
        """Добавляет один документ в индекс."""
        emb = self.model.encode(text, convert_to_numpy=True)
        self.index[file_id] = emb
        self.metadata[file_id] = {
            'text': text,
            'metadata': metadata or {}
        }

    def index_from_json(self, json_path: str, text_key: str = "full_text"):
        """
        Индексирует звонки из JSON-файла (результат работы CallAnalyzer).
        Ожидается список записей или объект с полем segments.
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            for item in data:
                file_id = item.get('file', str(hash(item.get('segments', ''))))
                text = self._extract_text(item, text_key)
                self.index_file(file_id, text, item)
        elif isinstance(data, dict):
            file_id = data.get('file', str(hash(data.get('segments', ''))))
            text = self._extract_text(data, text_key)
            self.index_file(file_id, text, data)
        else:
            raise ValueError("Unsupported JSON structure")

    def _extract_text(self, data: Dict, text_key: str) -> str:
        """Извлекает полный текст из структуры результата."""
        if 'segments' in data:
            return ' '.join([seg['text'] for seg in data['segments']])
        elif 'full_text' in data:
            return data['full_text']
        else:
            raise KeyError("No text field found")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Выполняет поиск, возвращает top_k документов с оценками."""
        query_emb = self.model.encode(query, convert_to_numpy=True).reshape(1, -1)

        if not self.index:
            return []

        file_ids = list(self.index.keys())
        embeddings = np.vstack([self.index[fid] for fid in file_ids])

        similarities = cosine_similarity(query_emb, embeddings).flatten()
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            file_id = file_ids[idx]
            results.append({
                'file_id': file_id,
                'similarity': float(similarities[idx]),
                'text': self.metadata[file_id]['text'],
                'metadata': self.metadata[file_id]['metadata']
            })
        return results

    def save_index(self, path: str):
        """Сохраняет индексы и метаданные на диск."""
        np.savez(path, index=np.vstack(list(self.index.values())),
                 file_ids=np.array(list(self.index.keys())))
        with open(path + '.meta.json', 'w') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def load_index(self, path: str):
        """Загружает индексы с диска."""
        data = np.load(path)
        file_ids = data['file_ids'].tolist()
        embeddings = data['index']
        self.index = {fid: emb for fid, emb in zip(file_ids, embeddings)}
        with open(path + '.meta.json', 'r') as f:
            self.metadata = json.load(f)


if __name__ == '__main__':
    # Пример использования
    searcher = SemanticSearch()
    # Индексация из папки с JSON-логами
    log_dir = "asr_logs"
    for fname in os.listdir(log_dir):
        if fname.endswith('_log.json'):
            searcher.index_from_json(os.path.join(log_dir, fname))

    while True:
        q = input("Запрос: ")
        if not q:
            break
        results = searcher.search(q, top_k=3)
        for res in results:
            print(f"{res['similarity']:.3f}: {res['text'][:100]}...")
