import pandas as pd

# 1. Load your converted M-Pesa CSV file
# Change 'my_mpesa_statement.csv' to your actual file name
file_path = "my_mpesa_statement.csv"

try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Error: Could not find the file '{file_path}'. Please check the path.")
    exit()

# 2. Clean the data columns (removes extra spaces from headers)
df.columns = df.columns.str.strip()

# 3. Convert financial columns to numeric values, handling commas or spaces
for col in ["Paid Out", "Paid In", "Balance"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(",", "")
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

# Filter out rows where no money was spent (we only want actual expenses)
df_expenses = df[df["Paid Out"] > 0].copy()


# 4. Define categorization rules based on common Kenyan M-Pesa keywords
def categorize_expense(detail):
    detail_lower = str(detail).lower()

    # Utilities & Bills
    if any(k in detail_lower for k in ["kplc", "tokens", "water", "zuku", "safaricom home", "dstv", "gotv"]):
        return "Utilities & Bills"
    
    # Food & Shopping (Supermarkets & common retail Tills)
    elif any(k in detail_lower for k in ["naivas", "carrefour", "quickmart", "chandarana", "tuskys", "supermarket", "retail"]):
        return "Food & Shopping"
    
    # Transport
    elif any(k in detail_lower for k in ["uber", "bolt", "yango", "matatu", "filling station", "shell", "totalenerg", "rubis"]):
        return "Transport"
    
    # Loans & Financial Services
    elif any(k in detail_lower for k in ["fuliza", "m-shwari", "mshwari", "kcb m-pesa", "kcb mpesa", "equity", "co-op"]):
        return "Loans & Banking"
    
    # Airtime & Bundles
    elif "airtime" in detail_lower:
        return "Airtime"
    
    # M-Pesa Fees
    elif any(k in detail_lower for k in ["withdrawal charge", "transaction charge", "agent withdrawal"]):
        return "M-Pesa Fees"
    
    # P2P Transfers (Sending money to individuals usually falls here)
    elif "customer transfer to" in detail_lower:
        return "Sent to Individuals (P2P)"
    
    # Paybill / Till defaults if not caught above
    elif "pay bill" in detail_lower:
        return "Other Paybills"
    elif "buy goods" in detail_lower:
        return "Other Merchant Tills"
    
    # Catch-all fallback
    else:
        return "Uncategorized / Miscellaneous"


# 5. Apply the categorization function to the dataset
df_expenses["Category"] = df_expenses["Details"].apply(categorize_expense)

# 6. Generate the Final Summary Report
print("\n=============================================")
print("          M-PESA EXPENDITURE SUMMARY         ")
print("=============================================\n")

# Calculate totals
total_spent = df_expenses["Paid Out"].sum()
summary = df_expenses.groupby("Category")["Paid Out"].sum().sort_values(ascending=False)

# Print category breakdown with percentages
for category, amount in summary.items():
    percentage = (amount / total_spent) * 100
    print(f"🔹 {category:<30} : KES {amount:,.2f} ({percentage:.1f}%)")

print("---------------------------------------------")
print(f"💰 TOTAL AMOUNT SPENT         : KES {total_spent:,.2f}")
print("=============================================")

# 7. Optional: Save the cleanly categorized data back to a new Excel/CSV sheet
output_file = "categorized_mpesa_expenses.csv"
df_expenses.to_csv(output_file, index=False)
print(f"\n💡 Detailed breakdown saved successfully to '{output_file}'!")
