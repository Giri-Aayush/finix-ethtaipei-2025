import os
import pandas as pd
from dune_client.client import DuneClient
from dune_client.types import QueryParameter
import json
from dotenv import load_dotenv

# Load environment variables from .env file (if you have one)
load_dotenv()

def fetch_dune_data(query_id=3196876, api_key=None):
    """
    Fetch data from Dune Analytics using their API client.
    
    Parameters:
    - query_id: ID of the Dune query to execute (default: 3196876)
    - api_key: Your Dune API key, if not provided will look for DUNE_API_KEY env variable
    
    Returns:
    - DataFrame with the query results
    """
    # Make sure .env is loaded 
    load_dotenv()
    
    # Get API key from .env first, then from parameter
    if api_key is None:
        api_key = os.environ.get("DUNE_API_KEY")
        if not api_key:
            raise ValueError("No API key found. Please set DUNE_API_KEY in your .env file.")
    
    # Initialize the Dune client
    dune = DuneClient(api_key)
    
    try:
        # Fetch the latest result from the specified query
        print(f"Fetching results for query ID: {query_id}...")
        query_result = dune.get_latest_result(query_id)
        
        # Convert to dataframe
        df = pd.DataFrame(query_result.result.rows)
        
        print(f"Successfully retrieved {len(df)} rows of data")
        return df
        
    except Exception as e:
        print(f"Error retrieving data: {str(e)}")
        raise

def save_data(df, output_format="csv", filename="dune_data"):
    """
    Save the retrieved data to a file.
    
    Parameters:
    - df: DataFrame to save
    - output_format: Format to save (csv, json, excel)
    - filename: Base filename (without extension)
    """
    if output_format.lower() == "csv":
        df.to_csv(f"{filename}.csv", index=False)
        print(f"Data saved to {filename}.csv")
    
    elif output_format.lower() == "json":
        df.to_json(f"{filename}.json", orient="records")
        print(f"Data saved to {filename}.json")
    
    elif output_format.lower() == "excel":
        df.to_excel(f"{filename}.xlsx", index=False)
        print(f"Data saved to {filename}.xlsx")
    
    else:
        print(f"Unsupported format: {output_format}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch data from Dune Analytics")
    parser.add_argument("--query_id", type=int, default=3196876, 
                        help="Dune query ID to fetch (default: 3196876)")
    parser.add_argument("--api_key", type=str, default=None,
                        help="Dune API key (optional, .env file is preferred)")
    parser.add_argument("--format", type=str, default="csv", choices=["csv", "json", "excel"],
                        help="Output format (csv, json, excel)")
    parser.add_argument("--filename", type=str, default="dune_data",
                        help="Output filename without extension")
    parser.add_argument("--display", action="store_true",
                        help="Display first few rows of the data")
    
    args = parser.parse_args()
    
    # Always try to load from .env first
    load_dotenv()
    api_key = os.environ.get("DUNE_API_KEY")
    
    # Only use command line arg as fallback
    if not api_key and args.api_key:
        api_key = args.api_key
    
    # Fetch the data
    df = fetch_dune_data(args.query_id, api_key)
    
    # Display data sample if requested
    if args.display and not df.empty:
        print("\nData Preview:")
        print(df.head())
        print(f"\nColumns: {list(df.columns)}")
    
    # Save the data
    save_data(df, args.format, args.filename)