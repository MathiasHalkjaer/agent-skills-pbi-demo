"""Writes the demo's Sales model as a PBIP project, messy or clean.

    python tools/build_model.py messy    # the inherited model the demo starts from
    python tools/build_model.py clean    # the fallback: what the agent should end up with

Both versions come from the one definition below, so names, relationships and measures
always agree. The data is inline (#table in Power Query), so the model refreshes without
any data source.
"""
import json
import pathlib
import random
import shutil
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
NS = uuid.UUID("6f1c3a52-6d2b-4a59-9a3e-0b7a5d1e2c11")


def tag(*parts):
    return str(uuid.uuid5(NS, "/".join(parts)))


# --- the definition: messy name, clean name, and the details ---------------------------

TABLES = {
    "DimCustomer": "Customer",
    "DimProduct": "Product",
    "DimDate": "Date",
    "FactSales": "Sales",
}

# (table, source column, messy name, clean name, type, hidden when clean, description, display folder)
COLUMNS = [
    ("DimCustomer", "cust_id", "cust_id", "Customer Key", "int64", True, "Key that links a customer to their sales.", ""),
    ("DimCustomer", "cust_name", "cust_name", "Customer Name", "string", False, "The customer's company name.", ""),
    ("DimCustomer", "cust_country", "cust_country", "Country", "string", False, "Country the customer is invoiced in.", "Location"),
    ("DimCustomer", "CustSegment", "CustSegment", "Segment", "string", False, "Customer segment: Enterprise, Mid-market or Small business.", ""),
    ("DimProduct", "prod_id", "prod_id", "Product Key", "int64", True, "Key that links a product to its sales.", ""),
    ("DimProduct", "ProductName", "ProductName", "Product Name", "string", False, "The product's name as shown on invoices.", ""),
    ("DimProduct", "prod_category", "prod_category", "Category", "string", False, "Product category code: BIK bikes, ACC accessories, CLO clothing.", ""),
    ("DimProduct", "list_price", "list_price", "List Price", "double", False, "Price before discounts, in EUR.", "Pricing"),
    ("DimDate", "date_key", "date_key", "Date", "dateTime", False, "Calendar date.", ""),
    ("DimDate", "yr", "yr", "Year", "int64", False, "Calendar year.", ""),
    ("DimDate", "month_no", "month_no", "Month Number", "int64", True, "Month number, 1 to 12; used to sort Month.", ""),
    ("DimDate", "MonthName", "MonthName", "Month", "string", False, "Month name, sorted by Month Number.", ""),
    ("FactSales", "order_id", "order_id", "Order Number", "int64", False, "The order's number from the ERP system.", ""),
    ("FactSales", "order_date", "order_date", "Order Date", "dateTime", True, "Date the order was placed; links to Date.", ""),
    ("FactSales", "cust_id", "cust_id", "Customer Key", "int64", True, "Links the order line to Customer.", ""),
    ("FactSales", "prod_id", "prod_id", "Product Key", "int64", True, "Links the order line to Product.", ""),
    ("FactSales", "qty", "qty", "Quantity", "int64", False, "Units on the order line.", "Order details"),
    ("FactSales", "sales_amt", "sales_amt", "Sales Amount", "double", False, "Invoiced amount for the line, in EUR, before returns.", "Order details"),
    ("FactSales", "cost_amt", "cost_amt", "Cost Amount", "double", False, "Cost of the goods on the line, in EUR.", "Order details"),
    ("FactSales", "return_flag", "return_flag", "Is Return", "int64", False, "1 if the line was returned, otherwise 0.", "Order details"),
]

# (messy name, clean name, messy DAX, clean DAX, clean format, clean description, clean folder)
MEASURES = [
    ("TotalSales", "Total Sales",
     "SUM(FactSales[sales_amt])",
     "SUM(Sales[Sales Amount])",
     "#,0", "Invoiced sales in EUR, including lines that were later returned.", "Revenue"),
    ("total_cost", "Total Cost",
     "SUM(FactSales[cost_amt])",
     "SUM(Sales[Cost Amount])",
     "#,0", "Cost of the goods sold, in EUR.", "Profitability"),
    ("Margin", "Margin %",
     "DIVIDE([TotalSales]-[total_cost],[TotalSales])",
     "DIVIDE([Total Sales] - [Total Cost], [Total Sales])",
     "0.0%", "Gross margin: sales minus cost, as a share of sales.", "Profitability"),
    ("NetSales", "Net Sales",
     "CALCULATE([TotalSales],FactSales[return_flag]=0)",
     "CALCULATE([Total Sales], Sales[Is Return] = 0)",
     "#,0", "Sales excluding returned lines. Finance's headline number.", "Revenue"),
    ("Sales LY", "Sales LY",
     "CALCULATE([TotalSales],SAMEPERIODLASTYEAR(DimDate[date_key]))",
     "CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date'[Date]))",
     "#,0", "Total Sales for the same period last year.", "Revenue"),
    ("Sales Status", "Sales Status",
     'IF([TotalSales]>50000,"High",IF([TotalSales]>20000,"Medium","Low"))',
     'VAR CurrentSales = [Total Sales]\nRETURN\n    SWITCH(\n        TRUE(),\n        CurrentSales > 50000, "High",\n        CurrentSales > 20000, "Medium",\n        "Low"\n    )',
     "", "High above 50,000 EUR of sales, Medium above 20,000, otherwise Low.", "Indicators"),
]

RELATIONSHIPS = [  # (from table, from column, to table, to column), by source column
    ("FactSales", "cust_id", "DimCustomer", "cust_id"),
    ("FactSales", "prod_id", "DimProduct", "prod_id"),
    ("FactSales", "order_date", "DimDate", "date_key"),
]

CUSTOMERS = [(1, "Contoso Retail", "Denmark", "Enterprise"), (2, "Fabrikam Cycles", "Italy", "Mid-market"),
             (3, "Northwind Sport", "Germany", "Enterprise"), (4, "Adatum Outdoor", "Italy", "Small business"),
             (5, "Tailspin Bikes", "Sweden", "Mid-market"), (6, "Wingtip Gear", "Denmark", "Small business")]
PRODUCTS = [(1, "Road Bike 500", "BIK", 1450.0), (2, "Mountain Bike 300", "BIK", 980.0),
            (3, "Helmet Pro", "ACC", 89.0), (4, "Bottle Cage", "ACC", 12.5),
            (5, "Rain Jacket", "CLO", 129.0), (6, "Cycling Gloves", "CLO", 35.0)]


def sales_rows():
    rnd = random.Random(7)
    rows = []
    for i in range(1, 121):
        year = 2024 if i <= 55 else 2025
        month = rnd.randint(1, 12)
        day = rnd.randint(1, 28)
        cust = rnd.randint(1, 6)
        prod = rnd.randint(1, 6)
        qty = rnd.randint(1, 12)
        price = PRODUCTS[prod - 1][3]
        sales = round(qty * price * rnd.uniform(0.85, 1.0), 2)
        cost = round(sales * rnd.uniform(0.55, 0.75), 2)
        ret = 1 if rnd.random() < 0.08 else 0
        rows.append((1000 + i, year, month, day, cust, prod, qty, sales, cost, ret))
    return rows


# --- writing TMDL ---------------------------------------------------------------------

def q(name):
    """Quote a TMDL name when it isn't a plain identifier."""
    return name if name.replace("_", "").isalnum() and not name[0].isdigit() else "'" + name.replace("'", "''") + "'"


def m_source(table):
    if table == "DimCustomer":
        body = ", ".join('{%d, "%s", "%s", "%s"}' % r for r in CUSTOMERS)
        return ['let',
                '    Source = #table(type table [cust_id = Int64.Type, cust_name = text, cust_country = text, CustSegment = text],',
                '        {' + body + '})',
                'in',
                '    Source']
    if table == "DimProduct":
        body = ", ".join('{%d, "%s", "%s", %s}' % r for r in PRODUCTS)
        return ['let',
                '    Source = #table(type table [prod_id = Int64.Type, ProductName = text, prod_category = text, list_price = number],',
                '        {' + body + '})',
                'in',
                '    Source']
    if table == "DimDate":
        return ['let',
                '    Dates = List.Dates(#date(2024, 1, 1), 731, #duration(1, 0, 0, 0)),',
                '    AsTable = Table.FromList(Dates, Splitter.SplitByNothing(), type table [date_key = date]),',
                '    Year = Table.AddColumn(AsTable, "yr", each Date.Year([date_key]), Int64.Type),',
                '    MonthNo = Table.AddColumn(Year, "month_no", each Date.Month([date_key]), Int64.Type),',
                '    MonthName = Table.AddColumn(MonthNo, "MonthName", each Date.MonthName([date_key], "en-US"), type text)',
                'in',
                '    MonthName']
    lines = ['let',
             '    Source = #table(type table [order_id = Int64.Type, order_date = date, cust_id = Int64.Type, prod_id = Int64.Type,',
             '            qty = Int64.Type, sales_amt = number, cost_amt = number, return_flag = Int64.Type], {']
    rows = sales_rows()
    for n, r in enumerate(rows):
        sep = "," if n < len(rows) - 1 else ""
        lines.append('        {%d, #date(%d, %d, %d), %d, %d, %d, %s, %s, %d}%s' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], sep))
    lines += ['    })', 'in', '    Source']
    return lines


def write_table(table, clean, out):
    name = TABLES[table] if clean else table
    L = [f"table {q(name)}", f"\tlineageTag: {tag(table)}", ""]
    if table == "FactSales":
        for messy, cname, mdax, cdax, fmt, desc, folder in MEASURES:
            mname, dax = (cname, cdax) if clean else (messy, mdax)
            if clean:
                L.append(f"\t/// {desc}")
            if "\n" in dax:
                L.append(f"\tmeasure {q(mname)} =")
                L += ["\t\t\t" + line for line in dax.split("\n")]
            else:
                L.append(f"\tmeasure {q(mname)} = {dax}")
            if clean and fmt:
                L.append(f"\t\tformatString: {fmt}")
            if clean and folder:
                L.append(f"\t\tdisplayFolder: {folder}")
            L += [f"\t\tlineageTag: {tag(table, 'measure', messy)}", ""]
    for t, src, messy, cname, dtype, hidden, desc, folder in COLUMNS:
        if t != table:
            continue
        cn = cname if clean else messy
        if clean:
            L.append(f"\t/// {desc}")
        L.append(f"\tcolumn {q(cn)}")
        L.append(f"\t\tdataType: {dtype}")
        if dtype == "dateTime":
            L.append("\t\tformatString: yyyy-mm-dd")
        if dtype == "double":
            L.append("\t\tformatString: #,0.00")
        if clean and hidden:
            L.append("\t\tisHidden")
        if clean and folder:
            L.append(f"\t\tdisplayFolder: {folder}")
        L.append(f"\t\tlineageTag: {tag(table, 'column', src)}")
        L.append("\t\tsummarizeBy: none")
        L.append(f"\t\tsourceColumn: {src}")
        if src == "MonthName":
            L.append(f"\t\tsortByColumn: {q('Month Number' if clean else 'month_no')}")
        L += ["", "\t\tannotation SummarizationSetBy = Automatic", ""]
    L.append(f"\tpartition {q(name)} = m")
    L.append("\t\tmode: import")
    L.append("\t\tsource =")
    L += ["\t\t\t\t" + line for line in m_source(table)]
    L += ["", "\tannotation PBI_ResultType = Table", ""]
    (out / "tables" / f"{name}.tmdl").write_text("\n".join(L), encoding="utf-8")


def colname(table, src, clean):
    for t, s, messy, cname, *_ in COLUMNS:
        if t == table and s == src:
            return cname if clean else messy
    raise KeyError(src)


def build(clean):
    sm = ROOT / "Sales.SemanticModel"
    if sm.exists():
        shutil.rmtree(sm)
    d = sm / "definition"
    (d / "tables").mkdir(parents=True)
    for table in TABLES:
        write_table(table, clean, d)
    names = [TABLES[t] if clean else t for t in TABLES]
    model = ["model Model", "\tculture: en-US", "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
             "\tsourceQueryCulture: en-US", "\tdataAccessOptions", "\t\tlegacyRedirects", "\t\treturnErrorValuesAsNull", "",
             "annotation __PBI_TimeIntelligenceEnabled = 0", "",
             "annotation PBI_QueryOrder = " + json.dumps(names), ""]
    model += [f"ref table {q(n)}" for n in names] + [""]
    (d / "model.tmdl").write_text("\n".join(model), encoding="utf-8")
    (d / "database.tmdl").write_text("database\n\tcompatibilityLevel: 1567\n", encoding="utf-8")
    rel = []
    for ft, fc, tt, tc in RELATIONSHIPS:
        fn, tn = (TABLES[ft], TABLES[tt]) if clean else (ft, tt)
        rel += [f"relationship {tag('rel', ft, fc)}",
                f"\tfromColumn: {q(fn)}.{q(colname(ft, fc, clean))}",
                f"\ttoColumn: {q(tn)}.{q(colname(tt, tc, clean))}", ""]
    (d / "relationships.tmdl").write_text("\n".join(rel), encoding="utf-8")
    (sm / "definition.pbism").write_text(json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2", "settings": {}}, indent=2), encoding="utf-8")
    (sm / ".platform").write_text(json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": "Sales"},
        "config": {"version": "2.0", "logicalId": tag("semanticmodel")}}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build(clean=(sys.argv[1:] == ["clean"]))
    print("built", "clean" if sys.argv[1:] == ["clean"] else "messy", "model")
