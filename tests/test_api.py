import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from pydantic import ValidationError

from backend.main import get_meta, recommend
from backend.models import RecommendRequest


class RecommendRequestTests(unittest.TestCase):
    def test_invalid_budget_is_rejected(self):
        with self.assertRaises(ValidationError):
            RecommendRequest(skin_type_id="s1", concern_ids=["c1"], budget=0)

    def test_blank_skin_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            RecommendRequest(skin_type_id="   ", concern_ids=["c1"], budget=1000)

    def test_concerns_are_trimmed_and_deduplicated(self):
        request = RecommendRequest(
            skin_type_id=" s1 ",
            concern_ids=["c1", " c1 ", "c2"],
            budget=1000,
        )

        self.assertEqual(request.skin_type_id, "s1")
        self.assertEqual(request.concern_ids, ["c1", "c2"])


class ApiHandlerTests(unittest.TestCase):
    def test_recommend_rejects_unknown_skin_type(self):
        request = RecommendRequest(skin_type_id="s1", concern_ids=["c1"], budget=10000)

        with patch("backend.main.db.fetch", new=AsyncMock(side_effect=[[]])), patch(
            "backend.main.run_recommendation", new=AsyncMock(return_value=[])
        ) as run_recommendation:
            with self.assertRaises(HTTPException) as exc:
                asyncio.run(recommend(request))

        self.assertEqual(exc.exception.status_code, 400)
        self.assertEqual(exc.exception.detail, "Unknown skin type")
        run_recommendation.assert_not_awaited()

    def test_recommend_rejects_unknown_concern_ids(self):
        request = RecommendRequest(skin_type_id="s1", concern_ids=["c1", "c9"], budget=10000)

        with patch(
            "backend.main.db.fetch",
            new=AsyncMock(side_effect=[[{"exists": 1}], [{"concern_id": "c1"}]]),
        ), patch("backend.main.run_recommendation", new=AsyncMock(return_value=[])) as run_recommendation:
            with self.assertRaises(HTTPException) as exc:
                asyncio.run(recommend(request))

        self.assertEqual(exc.exception.status_code, 400)
        self.assertEqual(exc.exception.detail, "Unknown concern IDs: c9")
        run_recommendation.assert_not_awaited()

    def test_recommend_passes_normalized_values_to_engine(self):
        request = RecommendRequest(
            skin_type_id=" s1 ",
            concern_ids=["c1", " c1 ", "c2"],
            budget=10000,
        )
        run_recommendation = AsyncMock(return_value=[])

        with patch(
            "backend.main.db.fetch",
            new=AsyncMock(side_effect=[[{"exists": 1}], [{"concern_id": "c1"}, {"concern_id": "c2"}]]),
        ), patch("backend.main.run_recommendation", new=run_recommendation):
            result = asyncio.run(recommend(request))

        self.assertEqual(result, [])
        run_recommendation.assert_awaited_once_with("s1", ["c1", "c2"], 10000.0)

    def test_meta_returns_safe_error_message(self):
        with patch("backend.main.db.fetch", new=AsyncMock(side_effect=RuntimeError("boom"))):
            with self.assertRaises(HTTPException) as exc:
                asyncio.run(get_meta())

        self.assertEqual(exc.exception.status_code, 500)
        self.assertEqual(exc.exception.detail, "Unable to load metadata")


if __name__ == "__main__":
    unittest.main()
