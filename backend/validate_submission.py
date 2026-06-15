import csv
import sys
from pathlib import Path

def main():
    # 1. Read submission.csv from project root
    csv_path = Path(__file__).resolve().parent.parent / "submission.csv"
    
    if not csv_path.exists():
        print(f"Error: submission.csv not found at {csv_path}")
        sys.exit(1)
        
    errors = []
    expected_columns = ["candidate_id", "rank", "score", "reasoning"]
    seen_candidates = set()
    rows_checked = 0
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("Error: submission.csv is empty")
            sys.exit(1)
            
        # 2. Validate required columns exist exactly
        if header != expected_columns:
            errors.append(f"Invalid columns. Expected {expected_columns}, got {header}")
            
        expected_rank = 1
        for row_num, row in enumerate(reader, start=2):
            if len(row) != 4:
                errors.append(f"Row {row_num}: Invalid number of columns (expected 4, got {len(row)})")
                continue
                
            candidate_id, rank_str, score_str, reasoning = row
            rows_checked += 1
            
            # 3. Validate every row
            
            # candidate_id starts with CAND_
            if not candidate_id.startswith("CAND_"):
                errors.append(f"Row {row_num}: candidate_id '{candidate_id}' does not start with 'CAND_'")
                
            # detect duplicate candidate_id
            if candidate_id in seen_candidates:
                errors.append(f"Row {row_num}: duplicate candidate_id '{candidate_id}' found")
            seen_candidates.add(candidate_id)
                
            # rank is integer and ranks are sequential
            try:
                rank = int(rank_str)
                if rank != expected_rank:
                    errors.append(f"Row {row_num}: rank sequence broken. Expected {expected_rank}, got {rank}")
                expected_rank += 1
            except ValueError:
                errors.append(f"Row {row_num}: rank '{rank_str}' is not a valid integer")
                
            # score is numeric and between 0 and 1
            try:
                score = float(score_str)
                if score < 0.0 or score > 1.0:
                    errors.append(f"Row {row_num}: score {score} is not between 0 and 1")
            except ValueError:
                errors.append(f"Row {row_num}: score '{score_str}' is not numeric")
                
            # reasoning is not empty
            if not reasoning or not reasoning.strip():
                errors.append(f"Row {row_num}: reasoning is empty")
                
    # fail if zero candidate rows
    if rows_checked == 0:
        errors.append("Error: submission.csv contains zero candidate rows")
        
    # 4. Output
    if errors:
        print("Detailed validation errors:")
        for err in errors:
            print(f"- {err}")
        # 5. Exit code 1 if invalid
        sys.exit(1)
    else:
        print(f"PASS ({rows_checked} rows checked)")
        # 5. Exit code 0 if valid
        sys.exit(0)

if __name__ == "__main__":
    main()
