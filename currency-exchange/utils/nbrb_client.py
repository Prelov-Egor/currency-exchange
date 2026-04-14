from datetime import date
from typing import Any

import httpx

from config import settings  # ← исправлено


class NBRBClient:
    def __init__(self):
        self.base_url = settings.NBRB_BASE_URL
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_daily_rates(self, on_date: date | None = None) -> list[dict[str, Any]]:
        url = f"{self.base_url}/exrates/rates"

        params = {"periodicity": 0}
        if on_date:
            params["ondate"] = on_date.isoformat()

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        return response.json()

    async def close(self):
        await self.client.aclose()
