# Medusa Storefront Automation Feasibility Assessment

Date: 2026-09-07  
Source: [immutable master workbook](../master/medusa-storefront-master-test-cases.xlsx)  
Source SHA-256: `2188CA0B0732053D096E6403C8D071F1F85A1CEDA5431960DF302CAF3FAADFBC`

## Executive decision

All 90 unique source cases were assessed individually. No automation tests were written.

| Decision | Count |
|---|---:|
| Feasible | 0 |
| Conditionally feasible | 89 |
| Blocked | 1 |
| **Feasibility total** | **90** |
| Automate independently | 46 |
| Consolidate/parameterize | 31 |
| Partially automate with manual coverage | 12 |
| Do not automate as written | 1 |
| **Recommendation total** | **90** |

`TC-PS-005` is blocked because it asks only to observe multi-filter behavior and compare it with an unapproved business rule. The other 89 cases are credible automation candidates in full or in part once their named environment, data, and framework conditions are met.

The five currently failing manual cases - `TC-LGN-005`, `TC-LGN-006`, `TC-LGN-007`, `TC-PD-015`, and `TC-CHK-005` - remain high-value Wave 1 defect-regression candidates. Their current failures are not reasons to exclude them.

## Assessment basis

The portfolio was evaluated using automation value, business risk, stability, determinism, observability, controllability, repeatability, environment support, duplication, and maintenance cost. These factors align with the suitability and maintainability concerns in the [ISTQB CTAL Test Automation Engineering syllabus](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTAL-TAE_Syllabus_v2.0.pdf).

Current repository readiness is broadly conditional:

- Customer authentication configuration and customer fixtures are absent. The existing `LoginPage` opens the Admin login route and cannot represent storefront customer login as written.
- Storefront catalog/listing coverage is missing. `ProductPage` covers only a small product-detail surface, and all current Page Object locators remain provisional until checked against the deployed storefront DOM and accessibility tree.
- Cart and checkout Page Objects and Store API clients provide useful foundations, but controlled setup/cleanup for customers, variants, inventory, related products, regions, prices, taxes, delivery methods, payment outcomes, sessions, carts, and orders is incomplete.
- Store requests must carry the configured publishable key and operate on sales-channel-scoped data, consistent with [Medusa's cart guidance](https://docs.medusajs.com/resources/storefront-development/cart/create).
- Mutation-heavy scenarios need isolated Admin setup and cleanup with explicit authorization. Network and server failures should use Playwright request routing where this proves UI recovery; an approved server-side mechanism is still required for real session expiry and inventory transitions.

Regression waves used below are: W1 = critical path and known-defect protection; W2 = stable functional regression; W3 = state, resilience, and failure handling; W4 = compatibility, responsive, accessibility, or judgment-heavy coverage.

## Browser, responsive, and accessibility boundaries

The supported browser matrix must be approved explicitly. Playwright supports Chromium, Firefox, WebKit, Chrome, and Edge. Its WebKit build is not branded Safari, so true Safari certification requires macOS/manual execution or an external browser grid; see [Playwright browser guidance](https://playwright.dev/python/docs/browsers).

Responsive checks should use named desktop, tablet, and mobile configurations with deterministic visibility, overlap, clipping, and interaction assertions. Emulation covers viewport, screen size, user agent, and touch behavior, but it is not a substitute for all physical-device review; see [Playwright emulation](https://playwright.dev/python/docs/emulation).

Accessibility automation should cover keyboard order and operation, programmatic labels, focus state, and error association. Manual review remains necessary for visual quality and assistive-technology experience, following [WCAG Focus Visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible) and [WCAG Error Identification](https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html).

## Case-by-case assessment

| ID | Module | Recommendation | Feasibility | Layer | Wave | Engineering rationale | Prerequisites | Missing capability / clarification | Consolidation target |
|---|---|---|---|---|---|---|---|---|---|
| TC-LGN-001 | Customer Login | Automate independently | conditionally feasible | UI | W2 | Stable presence checks for required controls. | Storefront login route and page. | Customer Login Page Object and verified locators. | - |
| TC-LGN-002 | Customer Login | Consolidate/parameterize | conditionally feasible | Hybrid | W1 | Same successful-authentication journey as TC-LGN-011. | Registered customer and clean session. | Customer auth config, fixture, and route. | CG-01 |
| TC-LGN-003 | Customer Login | Automate independently | conditionally feasible | UI | W2 | Password input type is deterministic. | Storefront login page. | Customer password locator. | - |
| TC-LGN-004 | Customer Login | Automate independently | conditionally feasible | UI | W2 | Toggle state and retained value are observable. | Login page and password value. | Verified visibility-control locator. | - |
| TC-LGN-005 | Customer Login | Consolidate/parameterize | conditionally feasible | UI | W1 | Required-field regression; currently fails manually. | Login page and valid password. | Approved browser-vs-app validation contract. | CG-02 |
| TC-LGN-006 | Customer Login | Consolidate/parameterize | conditionally feasible | UI | W1 | Required-field regression; currently fails manually. | Registered email and login page. | Approved browser-vs-app validation contract. | CG-02 |
| TC-LGN-007 | Customer Login | Automate independently | conditionally feasible | UI | W1 | High-value invalid-format defect regression. | Login page and valid password. | Approved email-format message and trigger. | - |
| TC-LGN-008 | Customer Login | Automate independently | conditionally feasible | Hybrid | W2 | Trimming plus successful session can be observed. | Registered customer with known credentials. | Customer fixture and session assertion. | - |
| TC-LGN-009 | Customer Login | Consolidate/parameterize | conditionally feasible | UI | W1 | Same generic rejection contract as TC-LGN-010. | Registered email and wrong password. | Customer login surface and stable error contract. | CG-03 |
| TC-LGN-010 | Customer Login | Consolidate/parameterize | conditionally feasible | UI | W1 | Parameterized invalid-credential response reduces duplication. | Guaranteed unregistered email. | Deterministic unique customer data. | CG-03 |
| TC-LGN-011 | Customer Login | Consolidate/parameterize | conditionally feasible | Hybrid | W1 | Duplicates TC-LGN-002 with added redirect/session checks. | Registered customer and clean session. | Customer auth setup and account locator. | CG-01 |
| TC-LGN-012 | Customer Login | Automate independently | conditionally feasible | Hybrid | W1 | Logout and protected-route denial prove session termination. | Authenticated customer session. | Customer logout and account Page Objects. | - |
| TC-LGN-013 | Customer Login | Automate independently | conditionally feasible | Hybrid | W3 | Expiry behavior is valuable but needs controlled invalidation. | Authenticated customer and account route. | Approved session-expiry mechanism. | - |
| TC-LGN-014 | Customer Login | Automate independently | conditionally feasible | Hybrid | W3 | Request count can prove submit deduplication. | Valid customer and interceptable auth request. | Customer auth endpoint observability. | - |
| TC-LGN-015 | Customer Login | Partially automate with manual coverage | conditionally feasible | UI | W4 | Keyboard path, focus, and error linkage are deterministic. | Approved control order and error semantics. | Manual visual and assistive-technology review. | - |
| TC-LGN-016 | Customer Login | Partially automate with manual coverage | conditionally feasible | UI | W4 | Cross-engine behavior automates; true Safari remains external. | Approved browser matrix and customer. | Safari/macOS or external grid; visual review. | - |
| TC-LGN-017 | Customer Login | Partially automate with manual coverage | conditionally feasible | UI | W4 | Named viewport interaction checks are repeatable. | Approved device/viewport matrix. | Physical-device and visual-quality review. | - |
| TC-PS-001 | Product Search & Listing | Automate independently | conditionally feasible | Hybrid | W2 | Card fields can be reconciled to Store API data. | Sales-channel catalog with available products. | Catalog Page Object and product data fixture. | - |
| TC-PS-002 | Product Search & Listing | Automate independently | conditionally feasible | UI | W1 | Selected card identity can match destination details. | Stable product with known handle. | Listing locators and storefront route mapping. | - |
| TC-PS-003 | Product Search & Listing | Automate independently | conditionally feasible | Hybrid | W2 | Sort orders are deterministic with distinct data. | Products with known prices and creation dates. | Catalog fixture and approved latest-arrival key. | - |
| TC-PS-004 | Product Search & Listing | Automate independently | conditionally feasible | Hybrid | W2 | Filter membership and reset are observable. | Products spanning a known filter value. | Filter semantics and catalog Page Object. | - |
| TC-PS-005 | Product Search & Listing | Do not automate as written | blocked | UI | W4 | No expected AND/OR rule exists to assert. | Approved multi-size and multi-colour behavior. | Business acceptance criteria. | - |
| TC-PS-006 | Product Search & Listing | Partially automate with manual coverage | conditionally feasible | UI | W4 | Functional matrix automates; visual/browser nuances need review. | Approved browsers and stable catalog. | Safari coverage and manual rendering review. | - |
| TC-PS-007 | Product Search & Listing | Partially automate with manual coverage | conditionally feasible | UI | W4 | Controls and navigation can be asserted per viewport. | Named viewport/device configurations. | Manual layout-quality and physical-device review. | - |
| TC-PD-001 | Product Details | Automate independently | conditionally feasible | Hybrid | W2 | Required sections can be compared with product data. | Fully populated product fixture. | Complete Product Page Object and field rules. | - |
| TC-PD-002 | Product Details | Consolidate/parameterize | conditionally feasible | UI | W2 | Same option-selection contract as size selection. | Product with Black and White variants. | Variant-option locators and state assertion. | CG-04 |
| TC-PD-003 | Product Details | Consolidate/parameterize | conditionally feasible | UI | W2 | Parameterize option type and values with TC-PD-002. | Product with multiple sizes. | Variant-option locators and state assertion. | CG-04 |
| TC-PD-004 | Product Details | Automate independently | conditionally feasible | Hybrid | W1 | End-to-end variant identity is high business value. | In-stock Black/M variant and empty cart. | Variant-aware add-to-cart and cart assertions. | - |
| TC-PD-005 | Product Details | Consolidate/parameterize | conditionally feasible | UI | W2 | Same missing-required-option behavior as TC-PD-006. | Product requiring colour and size. | Approved disabled-button or validation contract. | CG-05 |
| TC-PD-006 | Product Details | Consolidate/parameterize | conditionally feasible | UI | W2 | Parameterize omitted option with TC-PD-005. | Product requiring colour and size. | Approved disabled-button or validation contract. | CG-05 |
| TC-PD-007 | Product Details | Automate independently | conditionally feasible | Hybrid | W2 | Invalid combination can be seeded and rejected. | Known unavailable option combination. | Deterministic variant fixture and UI mapping. | - |
| TC-PD-008 | Product Details | Consolidate/parameterize | conditionally feasible | Hybrid | W1 | Same stock enforcement contract as TC-PD-013. | Out-of-stock variant in sales channel. | Inventory setup and teardown. | CG-06 |
| TC-PD-009 | Related Products | Partially automate with manual coverage | conditionally feasible | Hybrid | W4 | Configured membership automates; relevance is judgmental. | Product with configured related products. | Authoritative relation data; manual relevance review. | - |
| TC-PD-010 | Related Products | Automate independently | conditionally feasible | UI | W2 | Link identity and destination are deterministic. | Product with available related item. | Related-product locators. | - |
| TC-PD-011 | Related Products | Automate independently | conditionally feasible | UI | W2 | Empty state and absence of errors are observable. | Product with no related items. | No-related-products fixture and expected UI rule. | - |
| TC-PD-012 | Add to Cart | Automate independently | conditionally feasible | Hybrid | W1 | Cart badge and line-item state prove success. | Purchasable product and empty cart. | Storefront catalog/add-to-cart coverage. | - |
| TC-PD-013 | Add to Cart | Consolidate/parameterize | conditionally feasible | Hybrid | W1 | Duplicate stock rule with TC-PD-008 at cart boundary. | Out-of-stock product. | Inventory fixture and stable cart observation. | CG-06 |
| TC-PD-014 | Add to Cart | Automate independently | conditionally feasible | Hybrid | W1 | Boundary needs known stock and cart quantity. | Variant with small fixed inventory. | Inventory control and exact limit behavior. | - |
| TC-PD-015 | Add to Cart | Automate independently | conditionally feasible | Hybrid | W1 | Known failure regression protects idempotent cart state. | Controlled add-line-item failure and empty cart. | Request routing plus approved failure response. | - |
| TC-CART-001 | Shopping Cart | Automate independently | conditionally feasible | Hybrid | W2 | Cart UI can reconcile known API-seeded items. | Cart with multiple known variants. | Deterministic cart fixture and item locators. | - |
| TC-CART-002 | Shopping Cart | Consolidate/parameterize | conditionally feasible | Hybrid | W2 | Quantity direction is a simple parameter. | Cart item below stock limit. | Stable quantity controls and state polling. | CG-07 |
| TC-CART-003 | Shopping Cart | Consolidate/parameterize | conditionally feasible | Hybrid | W2 | Shares quantity-update assertions with TC-CART-002. | Cart item quantity above one. | Stable quantity controls and state polling. | CG-07 |
| TC-CART-004 | Shopping Cart | Consolidate/parameterize | conditionally feasible | Hybrid | W2 | Exact duplicate intent with TC-CART-008. | Cart containing target product. | Stable removal control and API state check. | CG-08 |
| TC-CART-005 | Shopping Cart | Consolidate/parameterize | conditionally feasible | Hybrid | W2 | Broad totals case overlaps subtotal and charge cases. | Known prices, region, tax, and shipping. | Deterministic pricing/tax configuration. | CG-09 |
| TC-CART-006 | Shopping Cart | Consolidate/parameterize | conditionally feasible | Hybrid | W2 | Subtotal is one assertion set within totals recalculation. | Known unit price and quantity. | Currency-safe amount parsing. | CG-09 |
| TC-CART-007 | Shopping Cart | Consolidate/parameterize | conditionally feasible | Hybrid | W1 | Parameterized totals oracle avoids repeated checkout state. | Known region, taxes, and shipping method. | Deterministic tax/shipping setup and oracle. | CG-09 |
| TC-CART-008 | Shopping Cart | Consolidate/parameterize | conditionally feasible | Hybrid | W2 | Exact removal duplicate of TC-CART-004. | Cart containing target product. | Stable removal control and API state check. | CG-08 |
| TC-CART-009 | Shopping Cart | Automate independently | conditionally feasible | UI | W2 | Last-item removal has distinct empty-state value. | Single-item cart. | Verified empty-state locator. | - |
| TC-CART-010 | Shopping Cart | Automate independently | conditionally feasible | Hybrid | W1 | Checkout gating for unavailable items is observable. | Cart seeded with unavailable product. | Approved unavailable-cart behavior and fixture. | - |
| TC-CART-011 | Shopping Cart | Automate independently | conditionally feasible | UI | W1 | Positive checkout gate protects critical journey. | Cart with valid purchasable item. | Stable checkout navigation locator. | - |
| TC-CART-012 | Shopping Cart | Automate independently | conditionally feasible | Hybrid | W1 | Inventory transition after carting needs controlled mutation. | In-stock item changed to out of stock. | Isolated Admin inventory update/cleanup. | - |
| TC-CART-013 | Shopping Cart | Automate independently | conditionally feasible | Hybrid | W3 | Failure injection can prove atomic persistence. | Known cart and controlled update interruption. | Request routing and server-state oracle. | - |
| TC-CART-014 | Shopping Cart | Automate independently | conditionally feasible | Hybrid | W3 | Restore semantics need deliberate session transition. | Customer cart tied to restorable session. | Approved session restore/expiry mechanism. | - |
| TC-CART-015 | Shopping Cart | Partially automate with manual coverage | conditionally feasible | UI | W4 | Core behavior automates across engines; rendering needs review. | Approved browser matrix and cart fixture. | Safari/grid and manual browser-specific review. | - |
| TC-CART-016 | Shopping Cart | Partially automate with manual coverage | conditionally feasible | UI | W4 | Named viewport functionality is deterministic. | Desktop, tablet, and mobile profiles. | Manual physical-device and visual review. | - |
| TC-CART-017 | Shopping Cart | Partially automate with manual coverage | conditionally feasible | UI | W4 | Keyboard operation and focus state are automatable. | Approved keyboard order and cart fixture. | Manual focus quality and assistive-tech review. | - |
| TC-CHK-001 | Checkout | Automate independently | conditionally feasible | Hybrid | W1 | Valid address progression is a critical checkout gate. | Authenticated customer, cart, region, address. | Customer auth and checkout fixture. | - |
| TC-CHK-002 | Checkout | Consolidate/parameterize | conditionally feasible | UI | W2 | One parameterized matrix can omit each mandatory field. | Approved mandatory-field list and valid baseline. | Exact required fields and validation messages. | CG-10 |
| TC-CHK-003 | Checkout | Automate independently | conditionally feasible | UI | W2 | Optional-field omission is a distinct positive boundary. | Approved optional-field list. | Exact optional fields for target storefront. | - |
| TC-CHK-004 | Checkout | Consolidate/parameterize | conditionally feasible | UI | W1 | Contact-format validation shares a data-driven pattern. | Valid address baseline and invalid email. | Approved validation rule/message. | CG-11 |
| TC-CHK-005 | Checkout | Consolidate/parameterize | conditionally feasible | UI | W1 | Known phone-validation defect belongs in contact matrix. | Valid address baseline and invalid phone. | Approved phone requirement and formats. | CG-11 |
| TC-CHK-006 | Checkout | Consolidate/parameterize | conditionally feasible | Hybrid | W2 | Billing mode can be parameterized with TC-CHK-007. | Valid shipping address and cart. | Billing toggle locator and cart-state oracle. | CG-12 |
| TC-CHK-007 | Checkout | Consolidate/parameterize | conditionally feasible | Hybrid | W2 | Alternate billing mode shares the same checkout setup. | Distinct valid shipping and billing addresses. | Billing form locators and persistence check. | CG-12 |
| TC-CHK-008 | Checkout | Consolidate/parameterize | conditionally feasible | UI | W2 | Overlaps mandatory-field blocking in TC-CHK-002. | Incomplete address variant. | Correct source result and required-field contract. | CG-10 |
| TC-CHK-009 | Checkout | Automate independently | conditionally feasible | UI | W2 | Back-navigation persistence is directly observable. | Valid checkout session and navigation path. | Approved return navigation; source evidence is blank. | - |
| TC-CHK-010 | Checkout | Automate independently | conditionally feasible | Hybrid | W1 | Displayed methods should reconcile to configured options. | Region with known delivery methods. | Delivery setup and estimated-date rule. | - |
| TC-CHK-011 | Checkout | Automate independently | conditionally feasible | UI | W2 | No-selection gate is a stable negative check. | Delivery step with no default selection. | Approved disabled-button or error behavior. | - |
| TC-CHK-012 | Checkout | Automate independently | conditionally feasible | Hybrid | W1 | Selection, persistence, and progression protect checkout. | Known delivery method. | Shipping-option fixture and persistence oracle. | - |
| TC-CHK-013 | Checkout | Automate independently | conditionally feasible | Hybrid | W2 | Known method prices provide a deterministic oracle. | Two delivery methods with different costs. | Stable shipping price configuration. | - |
| TC-CHK-014 | Checkout | Automate independently | conditionally feasible | Hybrid | W1 | Payment-provider availability and selection are observable. | Manual Payment configured for region. | Deterministic provider setup. | - |
| TC-CHK-015 | Checkout | Automate independently | conditionally feasible | UI | W2 | Review gate can be asserted without placing an order. | Payment step with no default method. | Approved error/disabled behavior. | - |
| TC-CHK-016 | Checkout | Consolidate/parameterize | conditionally feasible | Hybrid | W1 | Payment disruption matrix must prove no order and retry. | Controlled provider failure and known checkout. | Failure injection and order-count oracle. | CG-13 |
| TC-CHK-017 | Checkout | Automate independently | conditionally feasible | Hybrid | W3 | Cancellation path is distinct from transport failures. | Cancellable payment interaction. | Provider cancellation mechanism. | - |
| TC-CHK-018 | Checkout | Consolidate/parameterize | conditionally feasible | Hybrid | W1 | Timeout is one payment-disruption parameter. | Controlled timeout and known checkout. | Timeout injection and order-state oracle. | CG-13 |
| TC-CHK-019 | Checkout | Consolidate/parameterize | conditionally feasible | Hybrid | W1 | Network interruption shares no-duplicate/retry assertions. | Interruptible payment request. | Request routing and transaction/order oracle. | CG-13 |
| TC-CHK-020 | Checkout | Automate independently | conditionally feasible | Hybrid | W1 | Review values can reconcile to known cart totals. | Known addresses, items, region, taxes, delivery. | Complete totals oracle and Review Page Object. | - |
| TC-CHK-021 | Checkout | Automate independently | conditionally feasible | UI | W1 | Incomplete-state order gate is critical and deterministic. | Checkout with one required step incomplete. | Direct-review access rule and Place Order locator. | - |
| TC-CHK-022 | Checkout | Consolidate/parameterize | conditionally feasible | Hybrid | W1 | Core order creation overlaps confirmation cases. | Purchasable item and valid checkout data. | Isolated order setup/cleanup and corrected source result. | CG-14 |
| TC-CHK-023 | Checkout | Automate independently | conditionally feasible | Hybrid | W2 | Pre-submit edit flow has distinct state-transition value. | Review step and alternate valid data. | Editable-step navigation and corrected source evidence. | - |
| TC-CHK-024 | Checkout | Automate independently | conditionally feasible | Hybrid | W2 | Post-submit immutability is a separate order-state rule. | Newly placed known order. | Confirmation controls and corrected source evidence. | - |
| TC-CHK-025 | Checkout | Consolidate/parameterize | conditionally feasible | Hybrid | W1 | Confirmation details belong with successful order flow. | Successfully created known order. | Corrected shifted result and detail locators. | CG-14 |
| TC-CHK-026 | Checkout | Consolidate/parameterize | conditionally feasible | UI | W2 | Exact message is a focused assertion in order flow. | Successful order. | Approved copy and corrected shifted result. | CG-14 |
| TC-CHK-027 | Checkout | Automate independently | conditionally feasible | Hybrid | W1 | Refresh idempotency needs UI plus order-count evidence. | Created order with known ID. | Customer order query and cleanup. | - |
| TC-CHK-028 | Checkout | Automate independently | conditionally feasible | Hybrid | W3 | Checkout expiry requires controlled invalidation. | Active authenticated checkout. | Approved session-expiry mechanism. | - |
| TC-CHK-029 | Checkout | Partially automate with manual coverage | conditionally feasible | UI | W4 | Cross-browser checkout behavior automates; visual nuance remains. | Approved browser matrix and checkout fixture. | Safari/grid if required and manual rendering review. | - |
| TC-CHK-030 | Checkout | Partially automate with manual coverage | conditionally feasible | UI | W4 | Viewport functionality is repeatable with named profiles. | Approved device profiles and checkout fixture. | Physical-device and visual-quality review. | - |
| TC-CHK-31 | Checkout | Partially automate with manual coverage | conditionally feasible | UI | W4 | Keyboard order, operation, focus, and errors partly automate. | Approved control order and invalid address case. | Normalize ID; manual assistive-tech/focus review. | - |
| TC-CHK-032 | Checkout | Automate independently | conditionally feasible | Hybrid | W1 | Direct protected-route denial proves authorization boundary. | Known checkout URL and logout flow. | Customer auth Page Object and route contract. | - |
| TC-CHK-033 | Checkout | Automate independently | conditionally feasible | UI | W2 | Forbidden credential exposure can be asserted in DOM/text. | Completed order with known sensitive sentinels. | Approved masking/allowed-payment-display rules. | - |
| TC-CHK-034 | Checkout | Automate independently | conditionally feasible | UI | W2 | Error correction and recovery are deterministic. | Valid baseline with First Name omitted. | Stable error association and progression locators. | - |

## Consolidation map

The 31 source cases map to 14 maintainable automation groups; each source ID remains traceable in test metadata.

| Target | Source cases | Proposed automated behavior |
|---|---|---|
| CG-01 | TC-LGN-002, TC-LGN-011 | Successful customer login, session creation, and Account redirect |
| CG-02 | TC-LGN-005, TC-LGN-006 | Required login fields, parameterized by omitted field |
| CG-03 | TC-LGN-009, TC-LGN-010 | Generic invalid-credential rejection, parameterized by credential defect |
| CG-04 | TC-PD-002, TC-PD-003 | Product option selection, parameterized by option type and value |
| CG-05 | TC-PD-005, TC-PD-006 | Required variant option omission, parameterized by missing option |
| CG-06 | TC-PD-008, TC-PD-013 | Out-of-stock presentation and purchase prevention |
| CG-07 | TC-CART-002, TC-CART-003 | Cart quantity change, parameterized by direction |
| CG-08 | TC-CART-004, TC-CART-008 | Remove line item and verify UI/API cart state |
| CG-09 | TC-CART-005, TC-CART-006, TC-CART-007 | Recalculate subtotal, shipping, tax, and grand total after quantity change |
| CG-10 | TC-CHK-002, TC-CHK-008 | Mandatory shipping-field validation and blocked Delivery transition |
| CG-11 | TC-CHK-004, TC-CHK-005 | Invalid contact formats, parameterized by field and invalid value |
| CG-12 | TC-CHK-006, TC-CHK-007 | Same-as-shipping versus distinct billing address |
| CG-13 | TC-CHK-016, TC-CHK-018, TC-CHK-019 | Payment failure/timeout/network disruption, no order/duplicate, and retry |
| CG-14 | TC-CHK-022, TC-CHK-025, TC-CHK-026 | Successful order creation, confirmation details, and exact message |

## Partial automation and retained manual coverage

The 12 partial cases are `TC-LGN-015`-`017`, `TC-PS-006`-`007`, `TC-PD-009`, `TC-CART-015`-`017`, and `TC-CHK-029`-`031` (the workbook spells the last ID `TC-CHK-31`).

Automate deterministic behavior: keyboard reachability and operation, DOM focus state, label/error association, configured related-product membership, browser-engine flows, viewport-specific visibility, absence of programmatic overlap/clipping, and successful interaction. Retain manual coverage for semantic relevance, true Safari/device rendering, visual polish, colour contrast, focus-indicator quality, screen-reader announcements, and broader assistive-technology experience.

## Source-quality findings

The master workbook is intentionally unchanged. Before authoring, correct or formally disposition these source defects in a controlled copy or requirements system:

- `TC-PS-005` and `TC-CHK-008` contain unrelated password-visibility text in Actual Result.
- `TC-CHK-009` has a blank Actual Result but status PASS.
- Actual/expected results appear mismatched or shifted across `TC-CHK-022` through `TC-CHK-026`.
- `TC-CHK-31` is inconsistent with the three-digit identifier format used elsewhere; references to `TC-CHK-031` in this report mean that source case.
- Exact duplicates include `TC-CART-004/008`; other overlaps are represented by all consolidation groups above.
- Case metadata also contains inconsistent capitalization and minor wording defects. These do not block portfolio assessment but should be normalized before test authoring.

## Readiness and next actions

No case is ready for immediate authoring without satisfying its row-level conditions. Portfolio-level readiness requires:

1. Approve storefront customer authentication routes, credentials handling, session-expiry behavior, supported browsers, named device profiles, and the `TC-PS-005` multi-filter rule.
2. Add deterministic, sales-channel-scoped fixtures for customers, products, variants, invalid combinations, inventory, related products, prices, regions, taxes, delivery methods, payment outcomes, sessions, carts, and orders.
3. Add isolated Admin setup/cleanup for mutation-heavy cases and approved request-routing fixtures for controlled client/network/server failures.
4. Validate storefront DOM/accessibility behavior and then implement dedicated Customer Login, Catalog, Product Details, Cart, Checkout, Review, and Confirmation Page Objects.
5. Resolve the workbook source-quality findings while retaining source IDs for traceability.
6. Move W1 candidates to `medusa-test-author` only after their specific prerequisites and acceptance criteria are approved.
