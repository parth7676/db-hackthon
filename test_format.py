#!/usr/bin/env python3

def _format_ai_review(ai_content: str) -> str:
    """
    Format the AI review content to be simple, readable and developer-friendly.
    
    Args:
        ai_content: Raw AI review content
        
    Returns:
        Formatted review content
    """
    if not ai_content:
        return "❌ No AI review content available"
    
    # Simple, clean formatting
    formatted_parts = []
    
    # Extract basic vulnerability info
    if "Path Traversal Vulnerability" in ai_content:
        formatted_parts.append("## 🚨 Security Issue: Path Traversal")
        formatted_parts.append("")
    
    # Extract location
    location = ""
    for line in ai_content.split('\n'):
        if "File:" in line:
            location = line.replace("File:", "").strip()
            break
    
    if location:
        formatted_parts.append(f"**File:** {location}")
    
    # Extract severity
    severity = "High"
    for line in ai_content.split('\n'):
        if "Severity:" in line:
            severity = line.replace("Severity:", "").strip()
            break
    
    formatted_parts.append(f"**Severity:** {severity}")
    formatted_parts.append("")
    
    # Extract CWE
    cwe = ""
    for line in ai_content.split('\n'):
        if "CWE-ID:" in line:
            cwe = line.replace("CWE-ID:", "").strip()
            break
    
    if cwe:
        formatted_parts.append(f"**CWE:** {cwe}")
        formatted_parts.append("")
    
    # Extract description (first meaningful paragraph)
    description = ""
    lines = ai_content.split('\n')
    for i, line in enumerate(lines):
        if "Vulnerability Description:" in line:
            # Get the next meaningful line
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].strip().startswith('###'):
                    description = lines[j].strip()
                    break
            break
    
    if description:
        formatted_parts.append("**Issue:** " + description)
        formatted_parts.append("")
    
    # Extract vulnerable code
    vulnerable_code = ""
    start_idx = ai_content.find("```python")
    if start_idx != -1:
        end_idx = ai_content.find("```", start_idx + 9)
        if end_idx != -1:
            vulnerable_code = ai_content[start_idx:end_idx + 3]
    
    if vulnerable_code:
        formatted_parts.append("**Vulnerable Code:**")
        formatted_parts.append(vulnerable_code)
        formatted_parts.append("")
    
    # Extract secure code
    secure_code = ""
    secure_start = ai_content.find("Secure Code:")
    if secure_start != -1:
        start_idx = ai_content.find("```python", secure_start)
        if start_idx != -1:
            end_idx = ai_content.find("```", start_idx + 9)
            if end_idx != -1:
                secure_code = ai_content[start_idx:end_idx + 3]
    
    if secure_code:
        formatted_parts.append("**Secure Code:**")
        formatted_parts.append(secure_code)
        formatted_parts.append("")
    
    # Extract key recommendations
    recommendations = []
    in_recs = False
    for line in ai_content.split('\n'):
        if "Recommendations:" in line:
            in_recs = True
            continue
        elif in_recs and line.strip().startswith('###'):
            break
        elif in_recs and line.strip().startswith('1.') or line.strip().startswith('-'):
            rec = line.strip()
            if rec.startswith('1.'):
                rec = rec[2:].strip()
            elif rec.startswith('-'):
                rec = rec[1:].strip()
            if rec and len(rec) > 10:
                recommendations.append(rec)
    
    if recommendations:
        formatted_parts.append("**Key Fixes:**")
        for i, rec in enumerate(recommendations[:3], 1):  # Limit to 3
            formatted_parts.append(f"{i}. {rec}")
        formatted_parts.append("")
    
    # If no structured content found, provide a simple summary
    if len(formatted_parts) <= 3:
        formatted_parts = []
        formatted_parts.append("## 🔍 AI Security Review")
        formatted_parts.append("")
        formatted_parts.append("The AI has analyzed your code changes and identified potential security considerations.")
        formatted_parts.append("")
        formatted_parts.append("**Recommendation:** Review the changes for security best practices and ensure proper input validation.")
    
    return '\n'.join(formatted_parts)

# Test with the actual Databricks response
ai_response = """{'messages': [{'role': 'assistant', 'content': '## 🔴 Path Traversal Vulnerability

### **Vector DB Context:**
Based on the vector database search, this vulnerability is related to the lack of proper input validation and path manipulation. The vulnerable code allows an attacker to traverse the directory structure by manipulating the filename.

### **Location:**
- File: `Path_Traversal_bad.py`
- Line: 2-5
- Function/Method: `read_file_vulnerable()`

### **Vulnerability Description:**
The `read_file_vulnerable` function is vulnerable to path traversal attacks because it directly concatenates the user-provided filename to the base directory path without proper validation. This allows an attacker to access files outside the intended directory by providing a filename with relative path traversals (e.g., `../../../etc/passwd`).

### **CWE Reference:**
- **CWE-ID:** CWE-23
- **Category:** Path Traversal
- **Related CVEs:** Various CVEs related to path traversal vulnerabilities

### **Risk Assessment:**
- **Severity:** High
- **Impact:** An attacker could access sensitive files on the system, potentially leading to information disclosure or further exploitation.
- **Likelihood:** High, as the vulnerability is easily exploitable with crafted input.

### **Attack Scenario:**
An attacker could exploit this vulnerability by providing a specially crafted filename that includes relative path traversals, allowing them to read sensitive files outside the intended directory.

### **Vulnerable Code:**
```python
def read_file_vulnerable(filename):
    file_path = "/var/uploads/" + filename
    with open(file_path, \'r\') as f:
        return f.read()
```

### **Secure Code:**
```python
import os

def read_file_secure(filename):
    base_dir = "/var/uploads/"
    if ".." in filename or "/" in filename or "\\\\" in filename:
        raise ValueError("Invalid filename")
    file_path = os.path.join(base_dir, filename)
    if not os.path.isfile(file_path):
        raise FileNotFoundError("File not found")
    try:
        with open(file_path, \'r\') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
```

### **Recommendations:**
1. Validate user input to prevent directory traversal attacks.
2. Use `os.path.join` to construct file paths securely.
3. Check if the file exists and is a regular file before attempting to read it.

### **Additional Recommendations:**
- Implement additional security measures, such as input sanitization and secure file handling practices.
- Consider using a web application firewall (WAF) to detect and prevent common web attacks, including path traversal attempts.
- Regularly update and patch your system and applications to protect against known vulnerabilities.', 'id': 'run--b33f81b4-ab13-420b-9b4f-eb28d4d61432-0'}], 'id': 'b68cf68b-4630-4f10-b7cb-05505070650d'}"""

# Extract the content from the response
import json
response_data = json.loads(ai_response)
ai_content = response_data['messages'][0]['content']

# Format and display the markdown
formatted_markdown = _format_ai_review(ai_content)
print("=" * 80)
print("ACTUAL MARKDOWN OUTPUT FOR PR COMMENT:")
print("=" * 80)
print(formatted_markdown)
print("=" * 80) 