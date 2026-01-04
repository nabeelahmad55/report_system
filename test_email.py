# test_email_trigger.py
import sys
sys.path.append('.')

# Check if email is triggered in generate_report
with open('app/routes/reports.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # Find generate_report function
    start = content.find('async def generate_report')
    if start != -1:
        func_content = content[start:start+5000]  # First 5000 chars of function
        
        print("Checking generate_report function for email calls:")
        
        # Check for key terms
        checks = [
            ("send_email_with_pdf", "Email function call"),
            ("background_tasks.add_task", "Background task usage"),
            ("email_status", "Email status variable"),
            ("Email queued", "Debug print for email"),
        ]
        
        for term, description in checks:
            if term in func_content:
                print(f"✅ Found: {description}")
            else:
                print(f"❌ Missing: {description}")
        
        # Show around email sending area
        email_idx = func_content.find('send_email_with_pdf')
        if email_idx != -1:
            print("\n📧 Email sending code found:")
            start_context = max(0, email_idx - 200)
            end_context = min(len(func_content), email_idx + 300)
            print(func_content[start_context:end_context])
    else:
        print("❌ Could not find generate_report function")