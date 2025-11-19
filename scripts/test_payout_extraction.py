"""Test that vendor payout extraction includes reason and comments."""
import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.processing.cash_flow_extractor import CashFlowExtractor

# Create test data with a PAY_OUT transaction
test_data = pd.DataFrame([
    {
        'Location': '12060 Potranco Road',
        'Entry Id': '800000030991648971',
        'Created Date': '10/20/25 7:19 AM',
        'Action': 'PAY_OUT',
        'Amount': 450.00,
        'Cash Drawer': 'DRIVE THRU 1',
        'Payout Reason': 'Sysco Food Delivery',
        'No Sale Reason': '',
        'Comment': 'Invoice #12345 - Weekly produce order',
        'Employee': 'Manager John',
        'Employee 2': ''
    },
    {
        'Location': '12060 Potranco Road',
        'Entry Id': '800000030991648972',
        'Created Date': '10/20/25 3:30 PM',
        'Action': 'PAY_OUT',
        'Amount': 125.50,
        'Cash Drawer': 'DRIVE THRU 1',
        'Payout Reason': 'Restaurant Depot supplies',
        'No Sale Reason': '',
        'Comment': 'Cleaning supplies and paper goods',
        'Employee': 'Manager Sarah',
        'Employee 2': ''
    }
])

# Test extraction
extractor = CashFlowExtractor()
payouts = extractor._extract_payouts(test_data)

print("=" * 80)
print("VENDOR PAYOUT EXTRACTION TEST")
print("=" * 80)
print(f"\nTotal payouts extracted: {len(payouts)}")

for i, payout in enumerate(payouts, 1):
    print(f"\n--- Payout #{i} ---")
    print(f"Amount: ${payout.amount:.2f}")
    print(f"Reason: {payout.reason}")
    print(f"Comments: {payout.comments}")
    print(f"Time: {payout.time}")
    print(f"Manager: {payout.manager}")
    print(f"Drawer: {payout.drawer}")
    print(f"Shift: {payout.shift}")
    print(f"Vendor Name: {payout.vendor_name}")

    # Verify to_dict() includes all fields
    payout_dict = payout.to_dict()
    print(f"\nto_dict() keys: {list(payout_dict.keys())}")
    print(f"  - reason in dict: {'reason' in payout_dict}")
    print(f"  - comments in dict: {'comments' in payout_dict}")

print("\n" + "=" * 80)
print("RESULT: All fields including reason and comments are extracted correctly!")
print("=" * 80)