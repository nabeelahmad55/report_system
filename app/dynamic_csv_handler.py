# app/dynamic_csv_handler.py
import pandas as pd
import csv
from typing import List, Dict, Any
from datetime import datetime

class DynamicCSVHandler:
    """Handle any CSV format with automatic detection"""
    
    @staticmethod
    def detect_delimiter(file_path: str) -> str:
        """Detect CSV delimiter automatically"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sample = file.read(1024)
                file.seek(0)
                
                # Check for common delimiters
                delimiters = [',', ';', '\t', '|']
                delimiter_counts = {}
                
                for delim in delimiters:
                    delimiter_counts[delim] = sample.count(delim)
                
                # Return delimiter with highest count
                best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
                
                # If no delimiter found or too few, default to comma
                if delimiter_counts[best_delimiter] < 3:
                    return ','
                
                return best_delimiter
        except:
            return ','  # Default to comma
    
    @staticmethod
    def read_any_csv(file_path: str) -> List[Dict]:
        """Read any CSV file with automatic delimiter detection"""
        data = []
        try:
            delimiter = DynamicCSVHandler.detect_delimiter(file_path)
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                # Try to read as quoted CSV first (entire lines quoted)
                first_line = file.readline().strip()
                file.seek(0)
                
                if first_line.startswith('"') and first_line.endswith('"'):
                    # Handle quoted CSV format
                    reader = csv.reader(file)
                    
                    # Read and clean headers
                    headers_line = next(reader)[0] if reader else ''
                    headers = [h.strip().strip('"') for h in headers_line[1:-1].split(',')]
                    
                    # Read data rows
                    for row in reader:
                        if row:
                            row_line = row[0]
                            values = [v.strip().strip('"') for v in row_line[1:-1].split(',')]
                            
                            processed_row = {}
                            for i, header in enumerate(headers):
                                if i < len(values):
                                    processed_row[header] = values[i]
                                else:
                                    processed_row[header] = None
                            data.append(processed_row)
                else:
                    # Normal CSV format
                    reader = csv.DictReader(file, delimiter=delimiter)
                    for row in reader:
                        # Clean up keys and values
                        cleaned_row = {}
                        for key, value in row.items():
                            cleaned_key = key.strip().strip('"').strip()
                            cleaned_value = value.strip().strip('"').strip() if value else ''
                            cleaned_row[cleaned_key] = cleaned_value
                        data.append(cleaned_row)
            
            return data
            
        except Exception as e:
            raise ValueError(f"Error reading CSV: {str(e)}")
    
    @staticmethod
    def analyze_csv_structure(data: List[Dict]) -> Dict:
        """Analyze CSV structure and provide metadata"""
        if not data:
            return {}
        
        analysis = {
            "total_rows": len(data),
            "total_columns": 0,
            "columns": [],
            "data_types": {},
            "sample_data": []
        }
        
        if data:
            columns = list(data[0].keys())
            analysis["total_columns"] = len(columns)
            
            for col in columns:
                # Analyze column
                col_values = [row.get(col, '') for row in data]
                
                # Try to determine data type
                col_type = "text"
                numeric_count = 0
                date_count = 0
                
                for value in col_values[:100]:  # Check first 100 values
                    if value:
                        # Check if numeric
                        try:
                            float(str(value).replace(',', ''))
                            numeric_count += 1
                        except:
                            pass
                        
                        # Check if date (common patterns)
                        if '-' in str(value) or '/' in str(value):
                            try:
                                datetime.strptime(str(value)[:10], '%Y-%m-%d')
                                date_count += 1
                            except:
                                try:
                                    datetime.strptime(str(value)[:10], '%m/%d/%Y')
                                    date_count += 1
                                except:
                                    pass
                
                if date_count > len(col_values[:100]) * 0.3:  # 30% look like dates
                    col_type = "date"
                elif numeric_count > len(col_values[:100]) * 0.7:  # 70% look like numbers
                    col_type = "number"
                
                analysis["columns"].append({
                    "name": col,
                    "type": col_type,
                    "sample": str(col_values[0])[:50] if col_values else "",
                    "unique_count": len(set(col_values)),
                    "empty_count": sum(1 for v in col_values if not v or str(v).strip() == '')
                })
            
            # Get sample data (first 3 rows)
            analysis["sample_data"] = data[:3] if len(data) > 3 else data
        
        return analysis
    
    @staticmethod
    def generate_summary_stats(data: List[Dict]) -> Dict:
        """Generate summary statistics from CSV data"""
        if not data:
            return {}
        
        summary = {
            "numeric_columns": {},
            "text_columns": {},
            "date_columns": {},
            "general_stats": {
                "total_rows": len(data),
                "total_columns": len(data[0].keys()) if data else 0,
                "total_cells": len(data) * (len(data[0].keys()) if data else 0)
            }
        }
        
        if data:
            columns = list(data[0].keys())
            
            for col in columns:
                col_values = [row.get(col, '') for row in data if row.get(col, '')]
                
                if col_values:
                    # Check if column is numeric
                    numeric_values = []
                    for val in col_values:
                        try:
                            # Remove commas and currency symbols
                            clean_val = str(val).replace(',', '').replace('$', '').strip()
                            numeric_values.append(float(clean_val))
                        except:
                            pass
                    
                    if len(numeric_values) > len(col_values) * 0.5:  # >50% numeric
                        summary["numeric_columns"][col] = {
                            "min": min(numeric_values) if numeric_values else None,
                            "max": max(numeric_values) if numeric_values else None,
                            "avg": sum(numeric_values)/len(numeric_values) if numeric_values else None,
                            "sum": sum(numeric_values) if numeric_values else None,
                            "count": len(numeric_values)
                        }
                    else:
                        # Text column stats
                        unique_values = len(set(col_values))
                        summary["text_columns"][col] = {
                            "unique_values": unique_values,
                            "most_common": max(set(col_values), key=col_values.count) if col_values else None,
                            "max_length": max(len(str(v)) for v in col_values) if col_values else 0
                        }
        
        return summary