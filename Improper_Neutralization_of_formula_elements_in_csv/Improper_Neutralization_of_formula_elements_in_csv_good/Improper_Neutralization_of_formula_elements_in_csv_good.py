import csv
import tempfile
import os

def export_csv_secure(data):
    try:
        # Create a temporary file with a unique name
        with tempfile.NamedTemporaryFile(mode='w', delete=False, newline='') as temp_file:
            # Create a secure CSV writer
            writer = csv.writer(temp_file, quoting=csv.QUOTE_ALL)
            # Write the data to the temporary file
            for row in data:
                writer.writerow(row)
            # Return the name of the temporary file
            return temp_file.name
    except Exception as e:
        # Handle any exceptions that occur during the export process
        print(f"Error exporting CSV: {e}")
        return None
    finally:
        # Ensure the temporary file is deleted after it is no longer needed
        try:
            os.remove(temp_file.name)
        except Exception as e:
            # Handle any exceptions that occur during the deletion process
            print(f"Error deleting temporary file: {e}")