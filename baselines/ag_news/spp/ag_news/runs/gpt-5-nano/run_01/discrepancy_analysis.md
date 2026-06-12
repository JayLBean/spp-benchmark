# Discrepancy analysis — run_01 (prompt_v01, bare seed)

**Partition reviewed:** dev (80) + train (80). Score-blind clustering: rows are grouped by
*confusion type* and the categorical convention they reveal, NOT by chasing the metric.

## Confusion summary (gold → pred)

dev errors 9/80; train errors 10/80. Combined confusion, the recurring directions:

| gold → pred | dev | train | combined | reading |
|---|---:|---:|---:|---|
| Tech → World | 2 | 4 | **6** | science/nature framed as world news |
| Tech → Business | 3 | 1 | **4** | tech-company corporate event read as Business |
| World → Business | 1 | 2 | 3 | trade/economic policy read as corporate |
| Business → World | 2 | 1 | 3 | sanctions/labor read as geopolitics |
| Business → Tech | 0 | 1 | 1 | web product read as Tech |
| World → Sports | 1 | 0 | 1 | national-team match read as Sports |
| Tech → Sports | 0 | 1 | 1 | (singleton) |

## Categorical clusters (generalizable conventions)

### Cluster A — science/research/nature → Tech, not World  (combined 6, one direction)
Examples (gold=Tech, pred=World): "Global Warming Means More Frost-Free Days"; "Scientists
Intrigued by Rare Dead Whale"; "Found: Nessie's distant cousin [fossil]"; "Scientists hope to
find more tiny hominids". The AG News **Sci/Tech** class covers *science* (research, nature,
discovery, space, medicine-as-research) as well as technology. The bare seed's "Tech" reads to
the model as *gadgets/computing only*, so science stories framed as international or
human-interest news fall to World. This is a clean, one-directional, categorical convention.

### Cluster B — technology/internet/software company: classify by primary subject  (Tech↔Business ~4, noisier)
Tech→Business (gold=Tech): "AOL Aims to Lead Internet Travel Purchases"; "Will Beatles Take a
Bite out of Apple? [Apple Computer court case]"; "IBM To Spin Off PC Unit"; "Proxim, Symbol
settle in patent case". Business→Tech (gold=Business): "Amazon Launches A9 Web Search Service".
The convention AG News follows: when the article's **primary subject is a technology/internet/
software company's product, service, or technology**, it is **Tech** even if the news peg is a
corporate event (acquisition, spinoff, lawsuit, settlement); when the company is incidental to
a purely financial/market/earnings story, it is **Business**. The gold is genuinely noisy at
this boundary (the Amazon A9 counter-example), so the edit states the *convention*, not a
per-row patch — it is expected to net-help, not perfectly resolve.

## Non-categorical / noise (NOT to be patched)
- World→Sports: "Roddick Powers U.S. to Lead in Davis Semis" (gold=World) — reads as Sports;
  a national-team framing quirk in the gold. Row-specific; no generalizable rule.
- Tech→World: "Two Miami students die of carbon monoxide poisoning" (gold=Tech) — reads as
  general/World news; a noisy gold label. Row-specific.
- World↔Business trade/sanctions rows are mixed-direction (EU sanctions, AXA buyout, US Airways
  strike) — no consistent categorical lean; leaving to the model's prior rather than risk
  overfitting the small dev.

## Proposed edits (categorical only) → for the isolated rule-edit stage
1. **Edit 1 (Cluster A):** add a `<rules>` line making explicit that **Tech = science AND
   technology** — research, nature/environment, space, discoveries, medical research, and the
   internet — not only gadgets/computing; such a story is Tech even when it reads as world or
   human-interest news.
2. **Edit 2 (Cluster B):** add a `<rules>` line: for a technology/internet/software company,
   classify by the article's primary subject — its product/technology/service → Tech (even on a
   corporate-event news peg); a purely financial/market/earnings story with the company
   incidental → Business.

Both are statements about *class boundaries*, not about specific rows. Forwarded to the
score-blind auditor for a categorical-vs-row-specific verdict.
