# check_db_full.py
import sqlite3
import os
from datetime import datetime

# Connect to database
conn = sqlite3.connect('reports.db')
cursor = conn.cursor()

# Get table schema first
print("=" * 100)
print("DATABASE SCHEMA")
print("=" * 100)
cursor.execute("PRAGMA table_info(reports)")
columns = cursor.fetchall()
print(f"{'Column Name':<25} {'Type':<15} {'Nullable':<10} {'Primary Key':<12}")
print("-" * 70)
for col in columns:
    cid, name, col_type, notnull, dflt_value, pk = col
    print(f"{name:<25} {col_type:<15} {'NO' if notnull else 'YES':<10} {'YES' if pk else 'NO':<12}")

# Count reports
cursor.execute("SELECT COUNT(*) FROM reports")
count = cursor.fetchone()[0]
print(f"\n📊 Total Reports in database: {count}")

# Get all column names for the report
cursor.execute("SELECT * FROM reports LIMIT 1")
col_names = [description[0] for description in cursor.description]

# List all reports with ALL columns
print("\n" + "=" * 100)
print("DETAILED REPORT LISTING (ALL COLUMNS)")
print("=" * 100)

cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
reports = cursor.fetchall()

for report in reports:
    print("\n" + "-" * 100)
    print(f"📄 REPORT ID: {report[col_names.index('id')]}")
    print("-" * 100)
    
    # Group columns for better readability
    groups = {
        'Basic Info': ['id', 'filename', 'original_filename', 'client_name', 'client_email'],
        'Paths & Status': ['pdf_path', 'status', 'download_link', 'email_status'],
        'Timestamps': ['created_at', 'completed_at'],
        'Statistics': ['total_appointments', 'total_revenue'],
        'Settings': ['report_period', 'logo_path', 'hide_branding', 'template_used', 'include_insights'],
        'Other': ['error_message', 'notes']
    }
    
    for group_name, group_cols in groups.items():
        print(f"\n{group_name}:")
        print("-" * 40)
        for col_name in group_cols:
            if col_name in col_names:
                idx = col_names.index(col_name)
                value = report[idx]
                
                # Format based on column type
                if value is None:
                    display_value = "NULL"
                elif col_name in ['created_at', 'completed_at'] and value:
                    try:
                        display_value = str(value)
                    except:
                        display_value = value
                elif col_name == 'pdf_path':
                    exists = "✓ EXISTS" if value and os.path.exists(value) else "✗ MISSING"
                    display_value = f"{value} [{exists}]"
                elif col_name == 'email_status':
                    # Color code email status
                    if value == 'sent':
                        display_value = f"✅ {value}"
                    elif value == 'pending':
                        display_value = f"⏳ {value}"
                    elif value == 'failed':
                        display_value = f"❌ {value}"
                    elif value == 'resent':
                        display_value = f"🔄 {value}"
                    else:
                        display_value = f"❓ {value}"
                elif col_name == 'hide_branding' or col_name == 'include_insights':
                    display_value = "✅ YES" if value else "❌ NO"
                elif col_name == 'total_revenue' and value:
                    display_value = f"${float(value):,.2f}"
                else:
                    display_value = str(value)
                
                print(f"  {col_name:<25}: {display_value}")

# Summary Statistics
print("\n" + "=" * 100)
print("📈 SUMMARY STATISTICS")
print("=" * 100)

# Email status summary
cursor.execute("SELECT email_status, COUNT(*) FROM reports GROUP BY email_status")
email_stats = cursor.fetchall()
print("\nEmail Status Distribution:")
for status, count in email_stats:
    print(f"  {status or 'NULL':<10}: {count} reports")

# PDF existence check
cursor.execute("SELECT pdf_path FROM reports")
pdf_paths = cursor.fetchall()
existing = sum(1 for p in pdf_paths if p[0] and os.path.exists(p[0]))
print(f"\nPDF Files:")
print(f"  Existing: {existing}/{count}")
print(f"  Missing: {count - existing}/{count}")

# Revenue summary
cursor.execute("SELECT SUM(total_revenue) FROM reports WHERE total_revenue > 0")
total_rev = cursor.fetchone()[0] or 0
cursor.execute("SELECT AVG(total_revenue) FROM reports WHERE total_revenue > 0")
avg_rev = cursor.fetchone()[0] or 0
print(f"\nFinancial Summary:")
print(f"  Total Revenue: ${float(total_rev):,.2f}")
print(f"  Average Revenue per Report: ${float(avg_rev):,.2f}")

# Check PDF directories
print("\n" + "=" * 100)
print("📁 FILE SYSTEM CHECK")
print("=" * 100)

pdf_dirs = [
    "generated_pdfs",
    "app/generated_pdfs",
    "./generated_pdfs",
    "./app/generated_pdfs",
    "C:/report_system/app/generated_pdfs"
]

all_pdf_files = []
for pdf_dir in pdf_dirs:
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
        print(f"\n📂 Directory: '{pdf_dir}'")
        print(f"   Found: {len(pdf_files)} PDF files")
        for pdf in pdf_files[:10]:  # Show first 10 files
            full_path = os.path.join(pdf_dir, pdf)
            try:
                size = os.path.getsize(full_path)
                modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                print(f"   - {pdf:<40} ({size:,} bytes, {modified.strftime('%Y-%m-%d %H:%M')})")
            except:
                print(f"   - {pdf:<40} (Error reading file)")
        all_pdf_files.extend([os.path.join(pdf_dir, f) for f in pdf_files])
        
        if len(pdf_files) > 10:
            print(f"   ... and {len(pdf_files) - 10} more files")

# Cross-reference database with files
print("\n" + "=" * 100)
print("🔍 DATABASE vs FILESYSTEM CROSS-REFERENCE")
print("=" * 100)

cursor.execute("SELECT id, client_name, pdf_path FROM reports")
db_reports = cursor.fetchall()

print(f"\nDatabase entries: {len(db_reports)}")
print(f"PDF files found: {len(all_pdf_files)}")

print("\nMatching database entries with files:")
matches = 0
for report_id, client_name, pdf_path in db_reports:
    if pdf_path and os.path.exists(pdf_path):
        matches += 1
        print(f"  ✓ ID {report_id}: {client_name} - PDF exists")
    else:
        # Try to find the file
        found = False
        client_safe = ''.join(c if c.isalnum() else '_' for c in client_name)
        for pdf_file in all_pdf_files:
            if client_safe.lower() in os.path.basename(pdf_file).lower():
                print(f"  🔍 ID {report_id}: {client_name} - Possible match: {os.path.basename(pdf_file)}")
                found = True
                break
        if not found:
            print(f"  ✗ ID {report_id}: {client_name} - No PDF found")

print(f"\n📊 Match Rate: {matches}/{len(db_reports)} ({matches/len(db_reports)*100:.1f}%)")

# Close connection
conn.close()

print("\n" + "=" * 100)
print("✅ CHECK COMPLETED")
print("=" * 100)