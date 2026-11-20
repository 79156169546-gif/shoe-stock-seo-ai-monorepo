import os
import re
import sys
import json
from pathlib import Path

class ContentQualityGate:
    def __init__(self, blog_dir: str = "content/blog", registry_path: str = "seo-agent/registry.json"):
        self.blog_dir = Path(blog_dir)
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"published_slugs": [], "titles": []}

    def validate_article(self, file_path: Path) -> tuple[bool, list[str]]:
        errors = []
        warnings = []
        
        if not file_path.exists():
            return False, [f"Файл {file_path} не существует."]

        content = file_path.read_text(encoding="utf-8")

        # 1. URL & Slug Sanitizer (БЛОКИРУЮЩИЙ)
        slug = file_path.stem
        if not re.match(r"^[a-z0-9-]+$", slug):
            errors.append(f"Gate 1 [BLOCKING]: Недопустимый slug '{slug}'. Разрешены только латиница, цифры и дефис.")

        # 2. Duplicate Slug Check (БЛОКИРУЮЩИЙ)
        if slug in self.registry.get("published_slugs", []) and not os.environ.get("ALLOW_UPDATE"):
            errors.append(f"Gate 1 [BLOCKING]: Slug '{slug}' уже существует в опубликованном реестре.")

        # Парсинг frontmatter
        frontmatter_match = re.search(r"^---\s*(.*?)\s*---", content, re.DOTALL)
        if not frontmatter_match:
            errors.append("Gate 5 [BLOCKING]: Отсутствует заголовок Frontmatter (метаданные статьи).")
            return False, errors

        fm_text = frontmatter_match.group(1)
        
        # 3. Title & Description Check (БЛОКИРУЮЩИЙ)
        title_match = re.search(r'title:\s*["\']?(.*?)["\']?$', fm_text, re.MULTILINE)
        desc_match = re.search(r'description:\s*["\']?(.*?)["\']?$', fm_text, re.MULTILINE)

        if not title_match or not title_match.group(1).strip():
            errors.append("Gate 4 [BLOCKING]: Пустой или отсутствующий тег title.")
        else:
            title = title_match.group(1).strip()
            if len(title) > 90:
                warnings.append(f"Gate 4 [WARN]: Длина title ({len(title)}) превышает 90 символов.")
            if title in self.registry.get("titles", []) and not os.environ.get("ALLOW_UPDATE"):
                errors.append(f"Gate 2 [BLOCKING]: Полный дубль заголовка статьи: '{title}'.")

        if not desc_match or not desc_match.group(1).strip():
            errors.append("Gate 4 [BLOCKING]: Пустой тег description.")
        elif len(desc_match.group(1).strip()) > 260:
            warnings.append(f"Gate 4 [WARN]: Длина description ({len(desc_match.group(1).strip())}) превышает 260 символов.")

        # 4. Проверка Self-Canonical (БЛОКИРУЮЩИЙ)
        canonical_match = re.search(r'canonical:\s*["\']?(.*?)["\']?$', fm_text, re.MULTILINE)
        if not canonical_match or not canonical_match.group(1).strip():
            errors.append("Gate 6 [BLOCKING]: Отсутствует обязательное поле canonical во Frontmatter.")
        elif not canonical_match.group(1).strip().endswith(slug):
            warnings.append(f"Gate 6 [WARN]: Canonical URL '{canonical_match.group(1).strip()}' может не совпадать со слагом '{slug}'.")

        # 5. Анализ структуры тела статьи
        body = content[frontmatter_match.end():]
        lines = [l.strip() for l in body.split("\n") if l.strip()]
        
        # Проверка плотности списков (не более 25-30%)
        list_lines = [l for l in lines if l.startswith(("-", "*", "1.", "2.", "3."))]
        if lines and (len(list_lines) / len(lines)) > 0.30:
            warnings.append("Gate 7 [WARN]: Доля маркированных списков превышает 30%. Добавьте связный аналитический текст.")

        # 6. Проверка изображений и alt-атрибутов
        images = re.findall(r"!\[(.*?)\]\((.*?)\)", body)
        if not images:
            warnings.append("Gate 10 [WARN]: В статье нет ни одной иллюстрации или инфографики.")
        else:
            for alt, src in images:
                if not alt.strip():
                    warnings.append(f"Gate 10 [WARN]: Изображение '{src}' не содержит описания alt.")

        # 7. Проверка перелинковки
        links = re.findall(r"\[(.*?)\]\((.*?)\)", body)
        internal_links = [url for text, url in links if url.startswith("/") or not url.startswith("http")]
        if len(internal_links) < 2:
            warnings.append("Gate 11 [WARN]: Менее 2 внутренних ссылок в теле статьи. Добавьте ссылки на релевантные разделы.")

        is_valid = len(errors) == 0
        return is_valid, errors + warnings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python validator.py <путь_к_статье.mdx>")
        sys.exit(1)

    target_file = Path(sys.argv[1])
    validator = ContentQualityGate()
    success, messages = validator.validate_article(target_file)

    for msg in messages:
        print(msg)

    if not success:
        print("\n❌ [ОТК] Статья не прошла блокирующие проверки. В публикацию не допускается.")
        sys.exit(1)
    else:
        print("\n✅ [ОТК] Все критические проверки пройдены. Допущено к деплою.")
        sys.exit(0)
