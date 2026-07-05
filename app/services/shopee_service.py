import re
from html import unescape

import httpx
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    "Referer": "https://shopee.vn/",
}


class ShopeeService:
    def parse_ids(self, url: str) -> tuple[int, int] | None:
        patterns = [
            r"shopee\.vn/product/(\d+)/(\d+)",
            r"shopee\.vn/i\.(\d+)\.(\d+)",
            r"shopee\.vn/[^/]+-i\.(\d+)\.(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                shop_id, item_id = match.groups()
                return int(shop_id), int(item_id)

        return None

    def fetch(self, url: str) -> dict:
        ids = self.parse_ids(url)
        if ids:
            shop_id, item_id = ids
            api_data = self._fetch_api(shop_id, item_id)
            if api_data:
                return api_data

        return self._fetch_html(url)

    def _fetch_api(self, shop_id: int, item_id: int) -> dict | None:
        api_urls = [
            (
                "https://shopee.vn/api/v4/item/get",
                {"shopid": shop_id, "itemid": item_id},
            ),
            (
                "https://shopee.vn/api/v4/pdp/get_pc",
                {"shop_id": shop_id, "item_id": item_id},
            ),
        ]

        for api_url, params in api_urls:
            try:
                with httpx.Client(timeout=15.0, headers=DEFAULT_HEADERS) as client:
                    response = client.get(api_url, params=params)
                    response.raise_for_status()
                    payload = response.json()
            except (httpx.HTTPError, ValueError):
                continue

            item = self._extract_item_payload(payload)
            if item:
                return self._normalize_item(item, shop_id, item_id)

        return None

    def _extract_item_payload(self, payload: dict) -> dict | None:
        item = payload.get("data") or {}
        if item.get("item"):
            item = item["item"]
        if item.get("name") or item.get("images") or item.get("image"):
            return item
        return None

    def _normalize_item(self, item: dict, shop_id: int, item_id: int) -> dict:
        price = item.get("price", 0)
        price_min = item.get("price_min", price)
        price_str = self._format_price(price_min)

        images = []
        image_list = item.get("images") or []
        if item.get("image"):
            image_list.insert(0, item["image"])
        for image in image_list[:5]:
            images.append(self._image_url(str(image)))

        description = item.get("description") or ""
        if not description:
            attributes = item.get("attributes") or []
            description = "\n".join(
                f"{attr.get('name', '')}: {attr.get('value', '')}"
                for attr in attributes
                if attr.get("name")
            )

        return {
            "name": item.get("name", ""),
            "price": price_str,
            "description": description.strip(),
            "images": self._dedupe(images),
            "category": self._extract_category(item),
            "rating": item.get("item_rating", {}).get("rating_star"),
            "sold_count": item.get("historical_sold") or item.get("sold"),
            "platform": "shopee",
            "url": f"https://shopee.vn/product/{shop_id}/{item_id}",
        }

    def _fetch_html(self, url: str) -> dict:
        with httpx.Client(timeout=15.0, headers=DEFAULT_HEADERS, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        images = self._extract_images_from_html(html)
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            images.insert(0, og_image["content"])
        images = self._dedupe(images)[:5]

        text = soup.get_text(separator="\n", strip=True)
        return {
            "name": title.replace(" | Shopee Việt Nam", "").strip(),
            "price": "",
            "description": text[:2000],
            "images": images,
            "platform": "shopee",
            "url": url,
            "_raw_page_text": text,
        }

    def _extract_images_from_html(self, html: str) -> list[str]:
        decoded = unescape(html).replace("\\/", "/")
        images: list[str] = []

        url_pattern = re.compile(
            r"https?://(?:down-[^/\"']+\.img\.susercontent\.com|cf\.shopee\.[^/\"']+)/"
            r"(?:file/)?[A-Za-z0-9._%-]+"
        )
        images.extend(match.group(0) for match in url_pattern.finditer(decoded))

        hash_pattern = re.compile(
            r'"(?:image|image_id|image_id_str|cover|main_image)"\s*:\s*"([A-Za-z0-9_-]{24,})"'
        )
        for match in hash_pattern.finditer(decoded):
            image_hash = match.group(1)
            if "." in image_hash or "/" in image_hash:
                continue
            images.append(self._image_url(image_hash))

        return self._dedupe(images)

    def _image_url(self, image_hash: str) -> str:
        if image_hash.startswith("http://") or image_hash.startswith("https://"):
            return image_hash
        return f"https://down-vn.img.susercontent.com/file/{image_hash}"

    def _format_price(self, price_raw: int) -> str:
        if price_raw >= 100000:
            vnd = price_raw // 100000
            return f"{vnd:,}".replace(",", ".") + "đ"
        return str(price_raw)

    def _extract_category(self, item: dict) -> str | None:
        categories = item.get("categories") or []
        if categories:
            return categories[-1].get("display_name")
        return item.get("catid")

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result
