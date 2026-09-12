from __future__ import annotations

import pytest
from playwright.sync_api import expect

from medusa_automation.pages import CatalogPage, ProductPage
from tests.support import assert_no_horizontal_overflow

pytestmark = [pytest.mark.e2e]


@pytest.mark.source_case("TC-PS-001")
def test_available_product_cards_show_image_name_and_price(
    catalog_page: CatalogPage,
) -> None:
    catalog_page.open()
    catalog_page.assert_loaded()
    catalog_page.assert_cards_complete()


@pytest.mark.source_case("TC-PS-002")
def test_product_card_opens_matching_product_details(
    catalog_page: CatalogPage, storefront_product_page: ProductPage, require_test_data
) -> None:
    data = require_test_data("product_name")
    catalog_page.open()
    catalog_page.open_product(data.product_name)
    storefront_product_page.assert_product_heading(data.product_name)


@pytest.mark.source_case("TC-PS-003")
def test_product_sort_options_apply_expected_order(
    catalog_page: CatalogPage, require_test_data
) -> None:
    data = require_test_data("latest_product_name")
    catalog_page.open()
    catalog_page.choose_sort("Price: Low to High")
    catalog_page.wait_for_price_order()
    low_to_high = catalog_page.product_prices()
    assert len(low_to_high) >= 2, "Sorting needs at least two visible product prices"
    assert low_to_high == sorted(low_to_high)

    catalog_page.choose_sort("Price: High to Low")
    catalog_page.wait_for_price_order(descending=True)
    high_to_low = catalog_page.product_prices()
    assert high_to_low == sorted(high_to_low, reverse=True)

    catalog_page.choose_sort("Latest Arrivals")
    expect(catalog_page.product_cards.first).to_contain_text(data.latest_product_name)


@pytest.mark.source_case("TC-PS-004")
def test_single_filter_limits_and_then_restores_product_list(
    catalog_page: CatalogPage, require_test_data
) -> None:
    data = require_test_data(
        "filter_name", "filter_value", "filter_expected_product_names"
    )
    expected_names = {
        name.strip()
        for name in data.filter_expected_product_names.split(",")
        if name.strip()
    }
    assert expected_names, "TEST_FILTER_EXPECTED_PRODUCT_NAMES must contain names"
    catalog_page.open()
    original_names = catalog_page.product_names()
    assert original_names
    catalog_page.set_filter(data.filter_name, data.filter_value, True)
    expect(catalog_page.product_cards).to_have_count(len(expected_names))
    filtered_names = catalog_page.product_names()
    assert set(filtered_names) == expected_names
    catalog_page.set_filter(data.filter_name, data.filter_value, False)
    expect(catalog_page.product_cards).to_have_count(len(original_names))


@pytest.mark.source_case("TC-PS-006")
@pytest.mark.partial
def test_listing_core_behavior_in_configured_browser(
    catalog_page: CatalogPage,
    storefront_product_page: ProductPage,
    require_test_data,
) -> None:
    data = require_test_data(
        "filter_name", "filter_value", "product_name", "product_handle"
    )
    catalog_page.open()
    catalog_page.assert_cards_complete()
    catalog_page.choose_sort("Price: Low to High")
    catalog_page.set_filter(data.filter_name, data.filter_value, True)
    catalog_page.set_filter(data.filter_name, data.filter_value, False)
    catalog_page.open_product(data.product_name)
    storefront_product_page.assert_product_heading(data.product_name)


@pytest.mark.source_case("TC-PS-007")
@pytest.mark.partial
def test_listing_is_usable_at_named_viewports(catalog_page: CatalogPage) -> None:
    for width, height in ((1440, 900), (768, 1024), (390, 844)):
        catalog_page.page.set_viewport_size({"width": width, "height": height})
        catalog_page.open()
        catalog_page.assert_loaded()
        assert_no_horizontal_overflow(catalog_page.page)
        expect(
            catalog_page.product_cards.first.get_by_role("link").first
        ).to_be_enabled()
