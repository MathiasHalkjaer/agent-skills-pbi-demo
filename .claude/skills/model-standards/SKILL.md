---
name: model-standards
description: Naming, display folder, description and DAX conventions for our Power BI
  semantic models. Use when creating, renaming, tidying, documenting or reviewing tables,
  columns or measures in a PBIP or TMDL project, when writing or fixing DAX measures, or
  when preparing a model for Copilot or data agents.
---
# Model standards

Our team's rules for semantic models. They apply to the TMDL files in
`*.SemanticModel/definition/`, one file per table.

## Names
- Tables: singular business nouns, no prefixes (Customer, not DimCustomer; Sales, not FactSales).
- Columns and measures: words with spaces, each word capitalised (Order Date, Total Sales).
  No underscores, no abbreviations (Quantity, not qty).
- Percentages end in " %" (Margin %).
- Keys are named "<Table> Key" (Customer Key) and hidden.

## Renaming in TMDL
- Change the object's name. Keep `sourceColumn` as it is, and never change the Power Query source.
- Update every reference in the same change: DAX in measures, `relationships.tmdl`,
  `sortByColumn`, the `ref table` lines in `model.tmdl`, and the table file's own name.
- Report visuals refer to fields by name. This project's report has no visuals; in other
  projects, check the report definition as well.
- Renames touch several files, so do them in one place, never in parallel.

## Descriptions, folders and formats
- Every visible column and every measure gets a one-sentence description in business words
  from references/glossary.md, as a `///` line directly above it.
- Measures go in display folders by topic: Revenue, Profitability, Indicators.
- Every measure gets a format string: `#,0` for amounts, `0.0%` for percentages.

## DAX
For style and patterns, read references/dax-style.md.

## Decisions
Before deciding something the glossary doesn't cover, read references/decisions.md.

## Before you finish
Run `python .claude/skills/model-standards/scripts/check_names.py` and fix everything it reports.
