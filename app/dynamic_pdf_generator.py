# from weasyprint import HTML
# from jinja2 import Environment, FileSystemLoader
# import os
# from datetime import datetime
# from typing import List, Dict, Any

# class DynamicPDFGenerator:
#     """Generate PDF from any CSV with responsive design"""
    
#     def __init__(self, template_dir: str = None):
#         self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), "templates")
#         self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
#     def generate_cover_page(self, report_title: str, client_name: str, 
#                           column_count: int, row_count: int, logo_path: str = None) -> str:
#         """Generate cover page matching medical report theme"""
        
#         logo_html = ""
#         if logo_path and os.path.exists(logo_path):
#             logo_html = f'''
#             <div class="logo-container">
#                 <img src="{logo_path}" class="logo-img">
#             </div>
#             '''
        
#         return f'''
#         <div class="cover-page">
#             {logo_html}
            
#             <div class="cover-content">
#                 <h1 class="cover-title">{report_title}</h1>
                
#                 <div class="dataset-overview">
#                     <h3 class="overview-title">📊 Dataset Overview</h3>
#                     <div class="stats-grid">
#                         <div class="stat-item">
#                             <div class="stat-number">{row_count:,}</div>
#                             <div class="stat-label">Total Records</div>
#                         </div>
#                         <div class="stat-item">
#                             <div class="stat-number">{column_count}</div>
#                             <div class="stat-label">Data Columns</div>
#                         </div>
#                     </div>
#                 </div>
                
#                 <div class="client-info">
#                     <h2 class="client-name">{client_name}</h2>
#                     <p class="generation-date">
#                         Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}
#                     </p>
#                 </div>
                
#                 <div class="cover-footer">
#                     <p class="footer-note">
#                         This report was automatically generated from CSV data. 
#                         All data is presented as-is from the source file.
#                     </p>
#                 </div>
#             </div>
#         </div>
#         '''
    
#     def generate_analysis_page(self, analysis: Dict, summary: Dict) -> str:
#         """Generate data analysis page"""
        
#         # Create column overview table
#         columns_html = ""
#         for col_info in analysis.get("columns", []):
#             columns_html += f'''
#             <tr class="column-row">
#                 <td class="column-name">{col_info.get('name', '')}</td>
#                 <td class="column-type">{col_info.get('type', 'text')}</td>
#                 <td class="column-unique">{col_info.get('unique_count', 0):,}</td>
#                 <td class="column-empty">{col_info.get('empty_count', 0):,}</td>
#             </tr>
#             '''
        
#         # Create numeric summary
#         numeric_html = ""
#         for col_name, stats in summary.get("numeric_columns", {}).items():
#             avg = stats.get('avg')
#             total = stats.get('sum')
            
#             numeric_html += f'''
#             <div class="numeric-summary">
#                 <div class="numeric-title">{col_name}</div>
#                 <div class="numeric-stats">
#                     <div class="stat-box">
#                         <span class="stat-label">Min:</span>
#                         <span class="stat-value">{stats.get('min', 'N/A')}</span>
#                     </div>
#                     <div class="stat-box">
#                         <span class="stat-label">Max:</span>
#                         <span class="stat-value">{stats.get('max', 'N/A')}</span>
#                     </div>
#                     <div class="stat-box">
#                         <span class="stat-label">Avg:</span>
#                         <span class="stat-value">{round(avg, 2) if avg else 'N/A'}</span>
#                     </div>
#                     <div class="stat-box">
#                         <span class="stat-label">Total:</span>
#                         <span class="stat-value">{round(total, 2) if total else 'N/A'}</span>
#                     </div>
#                 </div>
#             </div>
#             '''
        
#         return f'''
#         <div class="analysis-page">
#             <div class="page-header">
#                 <h2 class="page-title">📈 Data Analysis Summary</h2>
#                 <div class="page-divider"></div>
#             </div>
            
#             <div class="analysis-grid">
#                 <div class="dataset-stats">
#                     <h3 class="section-title">📋 Dataset Statistics</h3>
#                     <div class="stats-container">
#                         <div class="stat-card">
#                             <div class="stat-number-large">{analysis.get('total_rows', 0):,}</div>
#                             <div class="stat-label-large">Total Records</div>
#                         </div>
#                         <div class="stat-card">
#                             <div class="stat-number-large">{analysis.get('total_columns', 0)}</div>
#                             <div class="stat-label-large">Columns</div>
#                         </div>
#                     </div>
#                 </div>
                
#                 <div class="data-quality">
#                     <h3 class="section-title warning">⚠️ Data Quality</h3>
#                     <p class="quality-note">
#                         Check for missing values and data consistency before making decisions based on this data.
#                     </p>
#                 </div>
#             </div>
            
#             <div class="section-container">
#                 <h3 class="section-title">📊 Column Overview</h3>
#                 <div class="table-responsive">
#                     <table class="column-table">
#                         <thead>
#                             <tr>
#                                 <th class="table-header">Column Name</th>
#                                 <th class="table-header">Data Type</th>
#                                 <th class="table-header">Unique Values</th>
#                                 <th class="table-header">Empty Values</th>
#                             </tr>
#                         </thead>
#                         <tbody>
#                             {columns_html}
#                         </tbody>
#                     </table>
#                 </div>
#             </div>
            
#             {numeric_html if numeric_html else ''}
            
#             <div class="tips-section">
#                 <h4 class="tips-title">💡 Tips for Better CSV Files</h4>
#                 <ul class="tips-list">
#                     <li>Use consistent date formats (YYYY-MM-DD recommended)</li>
#                     <li>Avoid special characters in column names</li>
#                     <li>Keep file size under 10MB for optimal processing</li>
#                     <li>Remove empty rows before uploading</li>
#                     <li>Use CSV format with proper UTF-8 encoding</li>
#                 </ul>
#             </div>
#         </div>
#         '''
    
#     def generate_data_tables(self, data: List[Dict], page_title: str = "Data Table") -> str:
#         """Generate paginated data tables"""
#         if not data:
#             return '<div class="empty-data"><p>No data available</p></div>'
        
#         columns = list(data[0].keys())
        
#         # Create table rows
#         rows_html = ""
#         for i, row in enumerate(data):
#             row_class = "even-row" if i % 2 == 0 else "odd-row"
#             cells_html = ""
            
#             for col in columns:
#                 value = row.get(col, "")
#                 # Format value for display
#                 display_value = str(value)
#                 if len(display_value) > 100:
#                     display_value = display_value[:100] + "..."
                
#                 cells_html += f'<td class="data-cell">{display_value}</td>'
            
#             rows_html += f'''
#             <tr class="data-row {row_class}">
#                 <td class="row-number">{i+1}</td>
#                 {cells_html}
#             </tr>
#             '''
        
#         # Create column headers
#         headers_html = ""
#         for col in columns:
#             headers_html += f'<th class="column-header">{col}</th>'
        
#         return f'''
#         <div class="data-page">
#             <div class="page-header">
#                 <h3 class="page-title">📋 {page_title}</h3>
#                 <div class="page-info">
#                     Showing {len(data):,} records • {datetime.now().strftime('%Y-%m-%d %H:%M')}
#                 </div>
#             </div>
            
#             <div class="table-container">
#                 <table class="data-table">
#                     <thead>
#                         <tr>
#                             <th class="row-header">#</th>
#                             {headers_html}
#                         </tr>
#                     </thead>
#                     <tbody>
#                         {rows_html}
#                     </tbody>
#                 </table>
#             </div>
#         </div>
#         '''
    
#     def generate_pdf(self, data_dict: Dict, output_path: str, 
#                     report_title: str = "Data Report", 
#                     client_name: str = "Client",
#                     logo_path: str = None,
#                     include_analysis: bool = True):
#         """Generate complete PDF with all sections"""
        
#         print(f"[Dynamic PDF] Generating PDF: {report_title}")
        
#         # Extract data
#         data = data_dict.get("data", [])
#         analysis = data_dict.get("analysis", {})
#         summary = data_dict.get("summary", {})
        
#         # Load CSS template
#         css_path = os.path.join(self.template_dir, "dynamic_styles.css")
#         if os.path.exists(css_path):
#             with open(css_path, 'r') as f:
#                 css_content = f.read()
#         else:
#             # Fallback CSS
#             css_content = """
#             body { font-family: Arial, sans-serif; }
#             .cover-page { padding: 50px; }
#             """
        
#         # Generate cover page
#         cover_html = self.generate_cover_page(
#             report_title, client_name,
#             analysis.get("total_columns", 0),
#             analysis.get("total_rows", 0),
#             logo_path
#         )
        
#         # Generate analysis page if requested
#         analysis_html = ""
#         if include_analysis and analysis:
#             analysis_html = self.generate_analysis_page(analysis, summary)
        
#         # Generate data tables (limit for large files)
#         max_records_to_show = 1000  # Limit to prevent huge PDFs
#         if len(data) > max_records_to_show:
#             print(f"⚠️ Large file detected: Showing first {max_records_to_show:,} of {len(data):,} records")
#             data = data[:max_records_to_show]
        
#         records_per_page = 50
#         data_chunks = [data[i:i + records_per_page] 
#                       for i in range(0, len(data), records_per_page)]
        
#         data_html = ""
#         for i, chunk in enumerate(data_chunks):
#             page_num = i + 1
#             total_pages = len(data_chunks)
#             page_title = f"Data Records (Page {page_num} of {total_pages})"
#             data_html += self.generate_data_tables(chunk, page_title)
        
#         # Combine all HTML with CSS
#         full_html = f'''
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <meta charset="UTF-8">
#             <style>
#                 {css_content}
#             </style>
#         </head>
#         <body>
#             {cover_html}
#             {analysis_html}
#             {data_html}
#         </body>
#         </html>
#         '''
        
#         # Generate PDF
#         os.makedirs(os.path.dirname(output_path), exist_ok=True)
#         HTML(string=full_html).write_pdf(output_path)
        
#         print(f"[Dynamic PDF] PDF generated: {output_path}")
#         return output_path
    
#     # ALIAS for backward compatibility
#     def generate_full_pdf(self, *args, **kwargs):
#         """Alias for generate_pdf method - FIX FOR YOUR ERROR"""
#         return self.generate_pdf(*args, **kwargs)



from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import base64

class DynamicPDFGenerator:
    """Generate professional PDF with matching app theme"""
    
    def __init__(self, template_dir: str = None):
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
    def _generate_css(self, client_colors: Dict = None, hide_branding: bool = False) -> str:
        """Generate CSS matching the app theme"""
        
        # Default colors matching your app's theme
        primary_color = client_colors.get('primary', '#4361ee') if client_colors else '#4361ee'
        secondary_color = client_colors.get('secondary', '#7209b7') if client_colors else '#7209b7'
        success_color = client_colors.get('success', '#4cc9f0') if client_colors else '#4cc9f0'
        dark_color = client_colors.get('dark', '#212529') if client_colors else '#212529'
        
        return f'''
        /* PDF Styling - Matching App Theme */
        @page {{
            margin: 20mm;
            size: A4;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        }}
        
        body {{
            background: white;
            color: {dark_color};
            font-size: 12pt;
            line-height: 1.5;
        }}
        
        /* Cover Page */
        .cover-page {{
            page-break-after: always;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 50px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            position: relative;
            overflow: hidden;
        }}
        
        .cover-background {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            opacity: 0.05;
        }}
        
        .logo-container {{
            text-align: center;
            margin-bottom: 40px;
            z-index: 1;
        }}
        
        .logo-img {{
            max-height: 100px;
            max-width: 300px;
            object-fit: contain;
        }}
        
        .cover-content {{
            text-align: center;
            max-width: 600px;
            z-index: 1;
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        }}
        
        .cover-title {{
            color: {primary_color};
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .report-period {{
            color: {secondary_color};
            font-size: 18px;
            margin-bottom: 30px;
            font-weight: 600;
        }}
        
        .client-name {{
            color: {dark_color};
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .generation-date {{
            color: #6c757d;
            font-size: 14px;
            margin-bottom: 40px;
        }}
        
        .cover-footer {{
            margin-top: 40px;
            color: #95a5a6;
            font-size: 12px;
            border-top: 1px solid #e9ecef;
            padding-top: 20px;
            width: 100%;
        }}
        
        /* Insights Page */
        .insights-page {{
            page-break-after: always;
            padding: 40px;
        }}
        
        .page-title {{
            color: {primary_color};
            font-size: 24px;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid {primary_color};
            font-weight: 600;
        }}
        
        .insights-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .insight-card {{
            flex: 1;
            min-width: 250px;
            background: #f8f9ff;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid {primary_color};
            margin-bottom: 20px;
        }}
        
        .insight-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .insight-icon {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
        }}
        
        .insight-title {{
            font-size: 18px;
            font-weight: 600;
            color: {dark_color};
        }}
        
        .insight-content {{
            color: #495057;
            font-size: 14px;
            line-height: 1.6;
        }}
        
        .insight-list {{
            margin: 15px 0;
            padding-left: 20px;
        }}
        
        .insight-list li {{
            margin-bottom: 8px;
            color: #495057;
        }}
        
        /* Summary Stats */
        .summary-stats {{
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
        }}
        
        .summary-title {{
            font-size: 20px;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        
        .stats-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: space-between;
        }}
        
        .stat-item {{
            text-align: center;
            flex: 1;
            min-width: 120px;
        }}
        
        .stat-number {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 12px;
            opacity: 0.9;
        }}
        
        /* Data Tables */
        .data-page {{
            page-break-after: always;
            padding: 30px;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
        }}
        
        .table-header {{
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }}
        
        .data-row td {{
            padding: 8px 10px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .even-row {{
            background: #f8f9fa;
        }}
        
        /* Branding Section */
        .branding-footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
            font-size: 11px;
        }}
        
        /* Print Optimizations */
        @media print {{
            .cover-page {{
                min-height: 297mm;
            }}
        }}
        '''
    
    def generate_cover_page(self, report_title: str, client_name: str, 
                          report_period: str, logo_base64: str = None,
                          client_colors: Dict = None) -> str:
        """Generate professional cover page matching app theme"""
        
        logo_html = ""
        if logo_base64:
            logo_html = f'''
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_base64}" class="logo-img">
            </div>
            '''
        
        return f'''
        <div class="cover-page">
            <div class="cover-background"></div>
            {logo_html}
            
            <div class="cover-content">
                <h1 class="cover-title">{report_title}</h1>
                <div class="report-period">Report Period: {report_period}</div>
                
                <div class="client-info">
                    <h2 class="client-name">{client_name}</h2>
                    <p class="generation-date">
                        Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                    </p>
                </div>
                
                <div class="cover-footer">
                    <p class="footer-note">
                        Professional Report • Confidential
                    </p>
                </div>
            </div>
        </div>
        '''
    
    def generate_insights_page(self, data: List[Dict], summary_stats: Dict) -> str:
        """Generate insights and summary page with rule-based analysis"""
        
        # Generate simple insights from data
        insights = self._generate_simple_insights(data, summary_stats)
        
        # Create insights HTML
        insights_html = ""
        for insight in insights[:4]:  # Show max 4 insights
            insights_html += f'''
            <div class="insight-card">
                <div class="insight-header">
                    <div class="insight-icon">
                        <i>{insight.get('icon', '📊')}</i>
                    </div>
                    <h3 class="insight-title">{insight.get('title', 'Insight')}</h3>
                </div>
                <div class="insight-content">
                    {insight.get('content', '')}
                </div>
            </div>
            '''
        
        # Summary stats HTML
        summary_html = ""
        if summary_stats:
            summary_html = f'''
            <div class="summary-stats">
                <h3 class="summary-title">📈 Key Performance Indicators</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-number">{summary_stats.get('total_records', 0):,}</div>
                        <div class="stat-label">Total Records</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{summary_stats.get('total_columns', 0)}</div>
                        <div class="stat-label">Data Columns</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{summary_stats.get('completion_rate', 'N/A')}</div>
                        <div class="stat-label">Completion Rate</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${summary_stats.get('total_revenue', 0):,.2f}</div>
                        <div class="stat-label">Total Revenue</div>
                    </div>
                </div>
            </div>
            '''
        
        return f'''
        <div class="insights-page">
            <h2 class="page-title">💡 Insights & Summary</h2>
            
            <div class="insights-grid">
                {insights_html}
            </div>
            
            {summary_html}
            
            <div class="insight-card">
                <div class="insight-header">
                    <div class="insight-icon">
                        <i>📋</i>
                    </div>
                    <h3 class="insight-title">Recommendations</h3>
                </div>
                <div class="insight-content">
                    <ul class="insight-list">
                        <li>Review data quality for better decision making</li>
                        <li>Monitor key metrics weekly for performance tracking</li>
                        <li>Consider seasonal trends in your analysis</li>
                        <li>Regular data backups are recommended</li>
                    </ul>
                </div>
            </div>
        </div>
        '''
    
    def _generate_simple_insights(self, data: List[Dict], summary_stats: Dict) -> List[Dict]:
        """Generate simple rule-based insights from data"""
        
        insights = []
        
        if not data:
            return insights
        
        # Insight 1: Revenue analysis
        revenue_fields = ['revenue', 'amount', 'price', 'total', 'income', 'sales']
        revenue_sum = 0
        for row in data:
            for key, value in row.items():
                if any(field in key.lower() for field in revenue_fields):
                    try:
                        clean_val = str(value).replace(',', '').replace('$', '').replace('£', '').replace('€', '').strip()
                        if clean_val:
                            revenue_sum += float(clean_val)
                    except:
                        pass
        
        if revenue_sum > 0:
            insights.append({
                'icon': '💰',
                'title': 'Revenue Overview',
                'content': f'Total revenue generated: ${revenue_sum:,.2f}. Consider focusing on high-performing segments.'
            })
        
        # Insight 2: Completion rate if available
        completion_fields = ['complete', 'finished', 'done', 'completed']
        completion_count = 0
        total_count = len(data)
        
        for row in data:
            for key, value in row.items():
                if any(field in key.lower() for field in completion_fields):
                    if str(value).lower() in ['yes', 'true', '1', 'completed', 'finished']:
                        completion_count += 1
        
        if total_count > 0:
            completion_rate = (completion_count / total_count) * 100
            if completion_rate > 80:
                insights.append({
                    'icon': '✅',
                    'title': 'High Completion Rate',
                    'content': f'Excellent completion rate of {completion_rate:.1f}%. Maintain this performance level.'
                })
            elif completion_rate < 60:
                insights.append({
                    'icon': '⚠️',
                    'title': 'Improvement Needed',
                    'content': f'Completion rate ({completion_rate:.1f}%) needs attention. Review processes.'
                })
        
        # Insight 3: Data quality
        total_cells = len(data) * len(data[0].keys()) if data else 0
        if total_cells > 0:
            insights.append({
                'icon': '📊',
                'title': 'Data Quality',
                'content': f'Dataset contains {len(data):,} records across {len(data[0].keys())} columns.'
            })
        
        # Insight 4: Date analysis
        date_fields = [key for key in data[0].keys() if any(x in key.lower() for x in ['date', 'time', 'day', 'month', 'year'])]
        if date_fields:
            insights.append({
                'icon': '📅',
                'title': 'Time Analysis',
                'content': f'Time-based data detected in {len(date_fields)} column(s). Consider analyzing trends over time periods.'
            })
        
        return insights
    
    def generate_data_tables(self, data: List[Dict], page_title: str = "Detailed Data") -> str:
        """Generate paginated data tables"""
        if not data:
            return '<div class="empty-data"><p>No data available</p></div>'
        
        columns = list(data[0].keys())
        
        # Create table rows
        rows_html = ""
        for i, row in enumerate(data):
            row_class = "even-row" if i % 2 == 0 else ""
            cells_html = ""
            
            for col in columns:
                value = row.get(col, "")
                display_value = str(value)
                if len(display_value) > 100:
                    display_value = display_value[:100] + "..."
                
                cells_html += f'<td>{display_value}</td>'
            
            rows_html += f'''
            <tr class="data-row {row_class}">
                <td>{i+1}</td>
                {cells_html}
            </tr>
            '''
        
        # Create column headers
        headers_html = ""
        for col in columns:
            headers_html += f'<th class="table-header">{col}</th>'
        
        return f'''
        <div class="data-page">
            <h3 class="page-title">{page_title}</h3>
            
            <table class="data-table">
                <thead>
                    <tr>
                        <th class="table-header">#</th>
                        {headers_html}
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        '''
    
    # FIXED METHOD - CORRECT PARAMETER NAMES
    def generate_pdf(self, data_dict: Dict, output_path: str, 
                    report_title: str = "Data Report", 
                    client_name: str = "Client",
                    include_analysis: bool = True,  # Changed from 'include_insights'
                    report_period: str = None,
                    logo_path: str = None,
                    hide_branding: bool = False,
                    client_colors: Dict = None):
        """Generate complete PDF with all new features"""
        
        print(f"[Professional PDF] Generating PDF: {report_title}")
        
        # Extract data
        data = data_dict.get("data", [])
        analysis = data_dict.get("analysis", {})
        summary = data_dict.get("summary", {})
        
        # Generate report period if not provided
        if not report_period:
            report_period = datetime.now().strftime("%B %Y")
        
        # Convert logo to base64 if exists
        logo_base64 = None
        if logo_path and os.path.exists(logo_path):
            try:
                with open(logo_path, "rb") as img_file:
                    logo_base64 = base64.b64encode(img_file.read()).decode()
            except Exception as e:
                print(f"Warning: Could not load logo: {e}")
        
        # Generate CSS with client colors
        css_content = self._generate_css(client_colors, hide_branding)
        
        # Generate cover page
        cover_html = self.generate_cover_page(
            report_title, client_name, report_period, 
            logo_base64, client_colors
        )
        
        # Generate insights page if requested
        insights_html = ""
        if include_analysis and data:  # Changed from 'include_insights'
            # Prepare summary stats
            summary_stats = {
                'total_records': len(data),
                'total_columns': len(data[0].keys()) if data else 0,
                'total_revenue': 0,
                'completion_rate': None
            }
            
            # Calculate revenue
            revenue_fields = ['revenue', 'amount', 'price', 'total']
            for row in data:
                for key, value in row.items():
                    if any(field in key.lower() for field in revenue_fields):
                        try:
                            clean_val = str(value).replace(',', '').replace('$', '').strip()
                            if clean_val:
                                summary_stats['total_revenue'] += float(clean_val)
                        except:
                            pass
            
            insights_html = self.generate_insights_page(data, summary_stats)
        
        # Generate data tables (limit for large files)
        max_records_to_show = 1000
        if len(data) > max_records_to_show:
            print(f"⚠️ Large file detected: Showing first {max_records_to_show:,} of {len(data):,} records")
            data = data[:max_records_to_show]
        
        records_per_page = 50
        data_chunks = [data[i:i + records_per_page] 
                      for i in range(0, len(data), records_per_page)]
        
        data_html = ""
        for i, chunk in enumerate(data_chunks):
            page_num = i + 1
            total_pages = len(data_chunks)
            page_title = f"Detailed Data (Page {page_num} of {total_pages})"
            data_html += self.generate_data_tables(chunk, page_title)
        
        # Branding footer
        branding_html = ""
        if not hide_branding:
            branding_html = '''
            <div class="branding-footer">
                <p>Generated by Report System • Professional Data Analysis</p>
            </div>
            '''
        
        # Combine all HTML with CSS
        full_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{report_title}</title>
            <style>
                {css_content}
            </style>
        </head>
        <body>
            {cover_html}
            {insights_html}
            {data_html}
            {branding_html}
        </body>
        </html>
        '''
        
        # Generate PDF
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        HTML(string=full_html).write_pdf(output_path)
        
        print(f"[Professional PDF] PDF generated: {output_path}")
        return output_path
    
    # ALIAS for backward compatibility - WITH CORRECT PARAMETERS
    def generate_full_pdf(self, data_dict: Dict, output_path: str, 
                         report_title: str = "Data Report", 
                         client_name: str = "Client",
                         include_analysis: bool = True,  # Changed parameter name
                         **kwargs):
        """Alias for generate_pdf method with correct parameter mapping"""
        # Map parameters from old method call
        report_period = kwargs.get('report_period')
        logo_path = kwargs.get('logo_path')
        hide_branding = kwargs.get('hide_branding', False)
        client_colors = kwargs.get('client_colors')
        
        return self.generate_pdf(
            data_dict=data_dict,
            output_path=output_path,
            report_title=report_title,
            client_name=client_name,
            include_analysis=include_analysis,  # Pass correct parameter
            report_period=report_period,
            logo_path=logo_path,
            hide_branding=hide_branding,
            client_colors=client_colors
        )