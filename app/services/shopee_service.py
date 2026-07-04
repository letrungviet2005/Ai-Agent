import re

import httpx
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
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
        api_url = "https://shopee.vn/api/v4/item/get"
        params = {"shopid": shop_id, "itemid": item_id}

        try:
            with httpx.Client(timeout=15.0, headers=DEFAULT_HEADERS) as client:
                response = client.get(api_url, params=params)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError):
            return None

        item = payload.get("data", {})
        if not item:
            return None

        price = item.get("price", 0)
        price_min = item.get("price_min", price)
        price_str = self._format_price(price_min)

        images = []
        image_list = item.get("images") or []
        for image in image_list[:5]:
            images.append(f"https://cf.shopee.vn/file/{image}")

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
            "images": images,
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

        og_image = soup.find("meta", property="og:image")
        images = [og_image["content"]] if og_image and og_image.get("content") else []

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
