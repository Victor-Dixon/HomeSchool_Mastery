from app.loot import roll_gear


def test_gear_roll_returns_item_for_passing_score():
    item = roll_gear(0.90, boss=True)
    assert item is not None
    assert "name" in item
    assert "slot" in item
    assert "rarity" in item


def test_low_score_only_returns_common():
    item = roll_gear(0.60, boss=False)
    assert item is not None
    assert item["rarity"] == "common"


def test_high_score_boss_can_return_high_tier_item():
    item = roll_gear(1.00, boss=True)
    assert item is not None
    assert item["rarity"] in {"rare", "legendary"}
