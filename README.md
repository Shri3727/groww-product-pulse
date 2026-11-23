# Groww weekly product pulse

Product and support workflow for the Groww app. It turns 12 weeks of public Play Store reviews into an internal weekly pulse and a facts-only explanation of the fee users mix up.

Milestone 1 product: Groww. This repository is only the review-intelligence workflow.

## How to run

```bash
py -3 scripts/serve_pulse.py
```

Open http://127.0.0.1:8000/pulse

On Vercel, import **this** repository (`groww-product-pulse`). The root redirects to `/pulse`. https://groww-nqm9.vercel.app is the Milestone 1 FAQ app and does not serve this page.

The page clusters `data/reviews/groww_reviews.csv` (30 Aug 2026–22 Nov 2026, 3,244 reviews) into at most five themes, shows the top three, three real quotes, the weekly pulse, and the fee explainer.

## Where MCP approval happens

On `/pulse`, in the **Approval** section.

The **Approve and log** button stays disabled until you check **I approve appending this entry to the notes doc and creating an email draft.** Nothing is written and nothing is sent before that.

After approval the app:

- Appends one entry to `deliverables/pulse/notes.md` with `date`, `top_themes`, `weekly_pulse`, `identified_fee_issue`, `explanation_bullets`, and `source_links`
- Writes `deliverables/pulse/email_draft.txt`

Subject: `Weekly Product Pulse + Customer Clarification — Equity brokerage and sell-side charges`

The draft is not sent. On Vercel the new entry is stored for that request under `/tmp`, because the hosted filesystem is read-only. The committed notes file and email draft in this repo are the submission copies.

## Fee issue identified from reviews

Equity brokerage. Reviewers compare Groww with apps that charge about ₹10 per order and treat Groww’s ₹20 or 0.1% equity brokerage as the whole cost of a sell. The reviews also describe extra amounts on a sell. Those are separate DP charges, GST, and statutory charges. Account maintenance is ₹0, which is why the headline looks free.

## Deliverables in this repo

| Item | Path |
|---|---|
| Reviews CSV | `data/reviews/groww_reviews.csv` |
| Weekly product pulse | `deliverables/pulse/weekly_product_pulse.md` |
| Notes entry | `deliverables/pulse/notes.md` |
| Email draft | `deliverables/pulse/email_draft.txt` |
| Source list (5 URLs) | `deliverables/pulse/sources.md` |

Fee explainer links, both checked 22 Nov 2026:

- https://groww.in/pricing
- https://groww.in/help/stocks,-f&o,-ipo-&-mtf/sx-demat-account/how-much-does-groww-charge-for-stocks-1

The source list adds three more official Groww help pages on DP charges and the contract-note charge lines.
