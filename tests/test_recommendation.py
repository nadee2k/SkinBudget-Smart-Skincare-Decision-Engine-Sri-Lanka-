import unittest

import pandas as pd

from backend.recommendation import _select_best_routine


class SelectBestRoutineTests(unittest.TestCase):
    def test_selects_best_combination_within_total_budget(self):
        df = pd.DataFrame(
            [
                {
                    "product_id": "cleanser_low",
                    "name": "Cleanser Low",
                    "brand": "Brand A",
                    "category": "Cleanser",
                    "step_order": 1,
                    "price": 3000.0,
                    "final_score": 0.70,
                    "concern_score": 0.0,
                },
                {
                    "product_id": "cleanser_high",
                    "name": "Cleanser High",
                    "brand": "Brand A",
                    "category": "Cleanser",
                    "step_order": 1,
                    "price": 5000.0,
                    "final_score": 0.90,
                    "concern_score": 0.0,
                },
                {
                    "product_id": "serum_low",
                    "name": "Serum Low",
                    "brand": "Brand B",
                    "category": "Serum",
                    "step_order": 2,
                    "price": 4000.0,
                    "final_score": 0.80,
                    "concern_score": 0.1,
                },
                {
                    "product_id": "serum_high",
                    "name": "Serum High",
                    "brand": "Brand B",
                    "category": "Serum",
                    "step_order": 2,
                    "price": 6000.0,
                    "final_score": 0.95,
                    "concern_score": 0.1,
                },
            ]
        )

        routine = _select_best_routine(df, budget=9000)

        self.assertEqual([item["product_id"] for item in routine], ["cleanser_high", "serum_low"])
        self.assertLessEqual(sum(item["price"] for item in routine), 9000)


if __name__ == "__main__":
    unittest.main()
