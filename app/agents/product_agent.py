import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.agents.base_agent import BaseAgent
from app.models.product import Product
from app.prompts.product_prompt import (
    PRODUCT_EXTRACT_SYSTEM,
    build_product_extract_prompt,
    build_target_customer_prompt,
)
from app.services.shopee_service import ShopeeService

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}


class ProductAgent(BaseAgent):
    def fetch_from_url(self, url: str) -> Product:
        platform = self._detect_platform(url)
        raw = self._fetch_by_platform(url, platform)

        if not raw.get("name") or not raw.get("price"):
            raw = self._extract_with_llm(url, raw)

        if not raw.get("target_customer"):
            raw["target_customer"] = self._infer_target_customer(raw)

        raw["url"] = url
        raw["platform"] = platform
        raw.pop("_raw_page_text", None)

        return Product.model_validate(raw)

    def _detect_platform(self, url: str) -> str:
        host = urlparse(url).netloc.lower()
        if "shopee" in host:
            return "shopee"
        if "tiktok" in host:
            return "tiktok"
        if "lazada" in host:
            return "lazada"
        return "generic"

    def _fetch_by_platform(self, url: str, platform: str) -> dict:
        if platform == "shopee":
            return ShopeeService().fetch(url)
        return self._fetch_generic(url)

    def _fetch_generic(self, url: str) -> dict:
        with httpx.Client(timeout=15.0, headers=DEFAULT_HEADERS, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        og_image = soup.find("meta", property="og:image")
        images = [og_image["content"]] if og_image and og_image.get("content") else []

        text = soup.get_text(separator="\n", strip=True)
        price_match = re.search(r"(\d[\d.,]*)\s*(?:đ|₫|VND|vnd)", text)

        return {
            "name": title,
            "price": price_match.group(0) if price_match else "",
            "description": text[:2000],
            "images": images,
            "_raw_page_text": text,
        }

    def _extract_with_llm(self, url: str, raw: dict) -> dict:
        page_text = raw.get("_raw_page_text") or raw.get("description") or ""
        prompt = build_product_extract_prompt(url, page_text)
        extracted = self.llm.generate_json(prompt, system=PRODUCT_EXTRACT_SYSTEM)

        for key, value in extracted.items():
            if value and (not raw.get(key) or raw.get(key) == ""):
                raw[key] = value

        return raw

    def _infer_target_customer(self, raw: dict) -> str:
        prompt = build_target_customer_prompt(
            name=raw.get("name", ""),
            description=raw.get("description", ""),
            category=raw.get("category"),
        )
        result = self.llm.generate_json(prompt)
        return result.get("target_customer", "Người tiêu dùng Việt Nam")
