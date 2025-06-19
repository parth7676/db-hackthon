import ast
import numexpr as ne

def execute_formula_secure(formula):
    try:
        # Use a parsing library to validate the formula
        tree = ast.parse(formula, mode='eval')
        
        # Check if the formula is valid
        if not is_valid_formula(tree):
            raise ValueError("Invalid formula")
        
        # Use a library like numexpr to evaluate the formula
        result = ne.evaluate(formula)
        
        return result
    
    except Exception as e:
        print(f"Error: {e}")
        return None

def is_valid_formula(tree):
    # Check if the formula only contains allowed nodes
    allowed_nodes = (ast.Num, ast.Name, ast.Load, ast.BinOp, ast.UnaryOp)
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            return False
    
    # Check if the formula only contains allowed names
    allowed_names = ('x', 'y', 'z')
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id not in allowed_names:
            return False
    
    return True