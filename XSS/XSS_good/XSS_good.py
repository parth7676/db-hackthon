import html

def display_comment_secure(comment):
    try:
        # Escape the comment to prevent XSS attacks
        escaped_comment = html.escape(comment)
        
        # Create the HTML with the escaped comment
        html = f"<div class='comment'>{escaped_comment}</div>"
        
        return html
    
    except Exception as e:
        print(f"Error: {e}")
        return None