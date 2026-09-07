from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from medusa_automation.pages.base_page import BasePage


class CatalogPage(BasePage):
    """Storefront product listing with test-id-first, semantic fallbacks."""

    card_selector = (
        "[data-testid='product-card'], [data-product-card], "
        "article:has(a[href*='/products/'])"
    )
    price_selector = (
        "[data-testid='product-price'], [data-product-price], [class*='price']"
    )

    @property
    def product_cards(self) -> Locator:
        return self.page.locator(self.card_selector)

    def open(self) -> None:
        self.open_path(self.config.product_listing_path)

    def assert_loaded(self) -> None:
        expect(self.product_cards.first).to_be_visible()

    def product_card(self, name: str) -> Locator:
        return self.product_cards.filter(
            has_text=re.compile(re.escape(name), re.IGNORECASE)
        ).first

    def product_names(self) -> list[str]:
        cards = self.product_cards.all()
        return [
            card.get_by_role("link").first.inner_text().strip()
            for card in cards
            if card.get_by_role("link").count()
        ]

    def product_prices(self) -> list[float]:
        values = self.product_cards.locator(self.price_selector).all_text_contents()
        prices: list[float] = []
        for value in values:
            normalized = re.sub(r"[^0-9,.-]", "", value).replace(",", "")
            if normalized:
                prices.append(float(normalized))
        return prices

    def assert_cards_complete(self) -> None:
        cards = self.product_cards.all()
        assert cards, "Expected at least one available product card"
        for index, card in enumerate(cards):
            expect(card.get_by_role("img").first, f"card {index} image").to_be_visible()
            expect(
                card.get_by_role("link").first, f"card {index} name/link"
            ).not_to_be_empty()
            price = card.locator(self.price_selector).first
            expect(price, f"card {index} price").to_contain_text(re.compile(r"\d"))

    def wait_for_price_order(self, *, descending: bool = False) -> None:
        self.page.wait_for_function(
            """({cardSelector, priceSelector, descending}) => {
                const parse = (text) => Number(text.replace(/[^0-9,.-]/g, '').replace(/,/g, ''));
                const values = Array.from(document.querySelectorAll(cardSelector))
                    .map(card => card.querySelector(priceSelector))
                    .filter(Boolean)
                    .map(price => parse(price.textContent || ''));
                if (values.length < 2 || values.some(Number.isNaN)) return false;
                return values.every((value, index) => index === 0 ||
                    (descending ? values[index - 1] >= value : values[index - 1] <= value));
            }""",
            arg={
                "cardSelector": self.card_selector,
                "priceSelector": self.price_selector,
                "descending": descending,
            },
        )

    def choose_sort(self, label: str) -> None:
        select = self.page.get_by_label(re.compile(r"sort", re.IGNORECASE)).first
        if select.count():
            select.select_option(label=label)
        else:
            self.page.get_by_role(
                "button", name=re.compile(r"sort", re.IGNORECASE)
            ).click()
            self.page.get_by_role("option", name=label).or_(
                self.page.get_by_role("menuitem", name=label)
            ).first.click()

    def set_filter(self, name: str, value: str, checked: bool) -> None:
        label = re.compile(
            rf"{re.escape(name)}.*{re.escape(value)}|{re.escape(value)}", re.IGNORECASE
        )
        control = (
            self.page.get_by_role("checkbox", name=label)
            .or_(self.page.get_by_label(label))
            .first
        )
        control.set_checked(checked)

    def open_product(self, name: str) -> None:
        self.product_card(name).get_by_role("link").first.click()
