# cleanup_orphaned.py
import sqlite3
import os

conn = sqlite3.connect('reports.db')
cursor = conn.cursor()

# Get all records
cursor.execute("SELECT id, pdf_path FROM reports")
records = cursor.fetchall()

# Find IDs to keep (those with existing PDFs)
keep_ids = []
delete_ids = []

for record_id, pdf_path in records:
    if pdf_path and os.path.exists(pdf_path):
        keep_ids.append(record_id)
        print(f"✓ Keeping ID {record_id} - PDF exists")
    else:
        delete_ids.append(record_id)
        print(f"✗ Deleting ID {record_id} - PDF missing")

# Delete orphaned records
if delete_ids:
    id_list = ','.join(map(str, delete_ids))
    cursor.execute(f"DELETE FROM reports WHERE id IN ({id_list})")
    conn.commit()
    print(f"\nDeleted {len(delete_ids)} orphaned records")
else:
    print("\nNo orphaned records to delete")

# Verify
cursor.execute("SELECT COUNT(*) FROM reports")
remaining = cursor.fetchone()[0]
print(f"Remaining records: {remaining}")

print("\nRemaining reports:")
cursor.execute("SELECT id, client_name, pdf_path FROM reports ORDER BY id")
for row in cursor.fetchall():
    print(f"ID {row[0]}: {row[1]} - {row[2]}")

conn.close()