import csv
from app.database import SessionLocal
from app.models.candidate import Candidate
from app.models.ranking import Ranking

db = SessionLocal()

keywords = ['AUDIT', 'TEST', 'DEMO', 'SAMPLE']
candidates = db.query(Candidate).all()
matched_cands = []
for c in candidates:
    if c.candidate_id and any(kw in c.candidate_id.upper() for kw in keywords):
        matched_cands.append(c)

print(f"Found {len(matched_cands)} matching candidates in DB.")

submission_data = {}
try:
    with open('../submission.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            submission_data[row['candidate_id']] = row
except Exception as e:
    print('Could not read submission.csv', e)

for c in matched_cands:
    print(f"\nCandidate ID: {c.candidate_id}")
    print(f"Title: {c.title}")
    
    # Check ranking table
    rankings = db.query(Ranking).filter(Ranking.candidate_id == c.id).all()
    if rankings:
        for r in rankings:
            print(f"In DB Ranking: True (Score={r.match_score})")
    else:
        print("In DB Ranking: False")
        
    # Check submission.csv
    if c.candidate_id in submission_data:
        row = submission_data[c.candidate_id]
        print(f"In submission.csv: True (Rank={row['rank']}, Score={row['score']})")
        print(f"Current Rank: {row['rank']}")
        print(f"Current Score: {row['score']}")
    else:
        print("In submission.csv: False")
        print("Current Rank: N/A")
        print("Current Score: N/A")
