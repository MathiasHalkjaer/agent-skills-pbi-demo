# DAX style

- Use a variable (VAR) for any value used more than once. Name it with a clear noun in
  PascalCase (CurrentSales), never the same as a table.
- No nested IF. Use SWITCH(TRUE(), ...) with one condition per line.
- Divide with DIVIDE, never with "/".
- Refer to measures without a table name ([Total Sales]) and to columns always with one
  (Sales[Sales Amount]).
- Spaces after commas and around operators.
- Time intelligence uses 'Date'[Date].

## Example

Before:

    IF([TotalSales]>50000,"High",IF([TotalSales]>20000,"Medium","Low"))

After:

    VAR CurrentSales = [Total Sales]
    RETURN
        SWITCH(
            TRUE(),
            CurrentSales > 50000, "High",
            CurrentSales > 20000, "Medium",
            "Low"
        )
