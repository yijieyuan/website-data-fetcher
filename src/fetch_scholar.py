import os
import time
import json
from scholarly import scholarly

SCHOLAR_ID = 'NJR_Z-gAAAAJ'
BASE_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(BASE_OUTPUT_DIR, "google_scholar.json")

def should_run():
    if not os.path.exists(OUTPUT_FILE):
        return True
    file_mod_time = os.path.getmtime(OUTPUT_FILE)
    return (time.time() - file_mod_time) > 86400

def run():
    if not should_run():
        print("   [Scholar] Data is less than 24h old. Skipping fetch.")
        return

    print("   [Scholar] Fetching Google Scholar data...")
    try:
        author = scholarly.search_author_id(SCHOLAR_ID)
        author_data = scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
        
        publications = author_data.get('publications', [])
        first_author_count = 0
        
        for pub in publications:
            p = scholarly.fill(pub)
            bib = p.get('bib', {})
            author_str = bib.get('author', '').lower()
            authors_list = [a.strip() for a in author_str.split(' and')]
            if len(authors_list) > 0:
                lead_author = authors_list[0]
                if 'yuan' in lead_author and (lead_author.startswith('y') or 'yijie' in lead_author):
                    first_author_count += 1
            time.sleep(0.5)

        data = {
            "citations": author_data.get('citedby', 0),
            "h_index": author_data.get('hindex', 0),
            "publications": len(publications),
            "first_author": first_author_count,
            "yearly_history": author_data.get('cites_per_year', {}),
            "last_updated": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
        
        # ATOMIC SAVE BUFFER
        temp_file = OUTPUT_FILE + ".tmp"
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file, OUTPUT_FILE)
            
        print(f"   [Scholar] Success. Safely saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"   [Scholar] Error: {e}")

if __name__ == "__main__":
    run()