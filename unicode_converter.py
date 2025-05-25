import csv
import re
import codecs

def convert_unicode_to_char(text):
    """
    Convert Unicode escape sequences to their corresponding characters.
    For example: '\\u00e9' -> 'é'
    """
    if not isinstance(text, str):
        return text
    
    # Handle both \u and \U escape sequences
    def replace_unicode(match):
        try:
            return chr(int(match.group(1), 16))
        except ValueError:
            return match.group(0)
    
    # Replace \uXXXX and \UXXXXXXXX patterns
    text = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, text)
    text = re.sub(r'\\U([0-9a-fA-F]{8})', replace_unicode, text)
    
    return text

def convert_scientific_chars(text):
    """
    Convert common scientific characters and Greek letters.
    """
    if not isinstance(text, str):
        return text
    
    # Dictionary of common scientific characters and their Unicode representations
    scientific_chars = {
        '\\u03B2': 'β',  # beta
        '\\u03B1': 'α',  # alpha
        '\\u03B3': 'γ',  # gamma
        '\\u03B4': 'δ',  # delta
        '\\u03B5': 'ε',  # epsilon
        '\\u03B8': 'θ',  # theta
        '\\u03BB': 'λ',  # lambda
        '\\u03BC': 'μ',  # mu
        '\\u03C0': 'π',  # pi
        '\\u03C3': 'σ',  # sigma
        '\\u03C9': 'ω',  # omega
        '\\u00B0': '°',  # degree symbol
        '\\u00B1': '±',  # plus-minus sign
        '\\u00B2': '²',  # superscript 2
        '\\u00B3': '³',  # superscript 3
        '\\u221E': '∞',  # infinity
        '\\u2264': '≤',  # less than or equal to
        '\\u2265': '≥',  # greater than or equal to
        '\\u2248': '≈',  # approximately equal to
    }
    
    # Replace each Unicode sequence with its corresponding character
    for unicode_seq, char in scientific_chars.items():
        text = text.replace(unicode_seq, char)
    
    return text

def process_csv_file(input_file, output_file):
    """
    Process a CSV file and convert Unicode escape sequences to their corresponding characters.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to the output CSV file
    """
    try:
        # Read the input file with UTF-8 encoding
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            headers = next(reader)  # Get the headers
            
            # Process all rows
            processed_rows = [headers]  # Start with headers
            for row in reader:
                # Convert each cell in the row
                processed_row = [convert_scientific_chars(convert_unicode_to_char(cell)) for cell in row]
                processed_rows.append(processed_row)
        
        # Write the processed data to the output file
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(processed_rows)
            
        print(f"Successfully processed {input_file}")
        print(f"Output written to {output_file}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    # Example usage
    input_file = "Proposals.csv"
    output_file = "Proposals_processed.csv"
    process_csv_file(input_file, output_file) 