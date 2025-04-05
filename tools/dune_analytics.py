# tools/dune_analytics.py - Dune Analytics data processing
from mcp.server.fastmcp import FastMCP, Context
from utils.helpers import format_json_response
import json
import os
import pandas as pd
from typing import Dict, List, Optional, Any

# Cache to store query results
QUERY_CACHE = {}

def register_dune_analytics_tools(mcp: FastMCP):
    """Register all Dune Analytics tools with the MCP server."""
    
    @mcp.tool()
    async def get_dune_data(query_id: int = 3196876, limit: int = 10, page: int = 1, ctx: Context = None) -> str:
        """
        Fetch data from Dune Analytics and return paginated results.
        
        Parameters:
        - query_id: ID of the Dune query to fetch (default: 3196876)
        - limit: Number of results to return per page (default: 10)
        - page: Page number to fetch (default: 1)
        
        Returns:
        - JSON formatted query results
        """
        try:
            import os
            import pandas as pd
            from dotenv import load_dotenv
            
            # Check if we need to import Dune client
            try:
                from dune_client.client import DuneClient
                from dune_client.types import QueryParameter
            except ImportError:
                return format_json_response({
                    "error": "Dune client not installed. Please install with: pip3 install dune-client"
                })
            
            # Load environment variables
            load_dotenv()
            
            if ctx:
                ctx.info(f"Processing Dune Analytics request for query {query_id}")
                await ctx.report_progress(1, 4)
            
            # Get API key from environment
            api_key = os.environ.get("DUNE_API_KEY")
            if not api_key:
                return format_json_response({
                    "error": "DUNE_API_KEY not found in environment variables"
                })
            
            # Check if the query is already in cache
            cache_key = f"query_{query_id}"
            if cache_key not in QUERY_CACHE:
                if ctx:
                    ctx.info("Data not in cache, fetching from Dune Analytics...")
                    await ctx.report_progress(2, 4)
                
                # Initialize the Dune client
                dune = DuneClient(api_key)
                
                # Fetch the latest result from the specified query
                try:
                    query_result = dune.get_latest_result(query_id)
                    
                    # Convert to dataframe
                    df = pd.DataFrame(query_result.result.rows)
                    
                    # Store in cache as a dictionary
                    QUERY_CACHE[cache_key] = {
                        "data": df.to_dict(orient="records"),
                        "columns": list(df.columns),
                        "total_rows": len(df),
                        "query_id": query_id
                    }
                    
                    if ctx:
                        ctx.info(f"Successfully retrieved {len(df)} rows from Dune")
                
                except Exception as e:
                    return format_json_response({
                        "error": f"Failed to fetch data from Dune: {str(e)}"
                    })
            else:
                if ctx:
                    ctx.info("Using cached Dune data")
                    await ctx.report_progress(2, 4)
            
            # Get the cached data
            cached_data = QUERY_CACHE[cache_key]
            
            if ctx:
                ctx.info(f"Processing page {page} with limit {limit}")
                await ctx.report_progress(3, 4)
            
            # Calculate pagination
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            
            # Get the paginated data
            total_rows = cached_data["total_rows"]
            if start_idx >= total_rows:
                return format_json_response({
                    "error": f"Page {page} exceeds available data. Max page is {(total_rows // limit) + 1}"
                })
            
            paginated_data = cached_data["data"][start_idx:end_idx]
            
            # Calculate total pages
            total_pages = (total_rows + limit - 1) // limit  # Ceiling division
            
            if ctx:
                ctx.info("Formatting response")
                await ctx.report_progress(4, 4)
            
            # Prepare the response
            result = {
                "success": True,
                "query_id": query_id,
                "dune_link": f"https://dune.com/queries/{query_id}",
                "total_rows": total_rows,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "next_page": page + 1 if page < total_pages else None,
                "prev_page": page - 1 if page > 1 else None,
                "columns": cached_data["columns"],
                "data": paginated_data
            }
            
            return format_json_response(result)
        
        except Exception as e:
            return format_json_response({
                "error": f"Error processing Dune data: {str(e)}"
            })
    
    @mcp.tool()
    async def search_dune_data(query_id: int = 3196876, search_column: str = None, search_value: str = None, limit: int = 10, ctx: Context = None) -> str:
        """
        Search within Dune Analytics data for specific values.
        
        Parameters:
        - query_id: ID of the Dune query to search in (default: 3196876)
        - search_column: Column to search in (if None, searches all columns)
        - search_value: Value to search for
        - limit: Maximum number of results to return (default: 10)
        
        Returns:
        - JSON formatted search results
        """
        try:
            import os
            import pandas as pd
            from dotenv import load_dotenv
            
            # Check if we need to import Dune client
            try:
                from dune_client.client import DuneClient
                from dune_client.types import QueryParameter
            except ImportError:
                return format_json_response({
                    "error": "Dune client not installed. Please install with: pip3 install dune-client"
                })
            
            if ctx:
                ctx.info(f"Processing Dune Analytics search request")
                await ctx.report_progress(1, 4)
            
            # Check if search value is provided
            if search_value is None:
                return format_json_response({
                    "error": "No search value provided"
                })
            
            # Load environment variables
            load_dotenv()
            
            # Get API key from environment
            api_key = os.environ.get("DUNE_API_KEY")
            if not api_key:
                return format_json_response({
                    "error": "DUNE_API_KEY not found in environment variables"
                })
            
            # Check if the query is already in cache
            cache_key = f"query_{query_id}"
            if cache_key not in QUERY_CACHE:
                if ctx:
                    ctx.info("Data not in cache, fetching from Dune Analytics...")
                    await ctx.report_progress(2, 4)
                
                # Initialize the Dune client
                dune = DuneClient(api_key)
                
                # Fetch the latest result from the specified query
                try:
                    query_result = dune.get_latest_result(query_id)
                    
                    # Convert to dataframe
                    df = pd.DataFrame(query_result.result.rows)
                    
                    # Store in cache as a dictionary
                    QUERY_CACHE[cache_key] = {
                        "data": df.to_dict(orient="records"),
                        "columns": list(df.columns),
                        "total_rows": len(df),
                        "query_id": query_id
                    }
                    
                    if ctx:
                        ctx.info(f"Successfully retrieved {len(df)} rows from Dune")
                
                except Exception as e:
                    return format_json_response({
                        "error": f"Failed to fetch data from Dune: {str(e)}"
                    })
            else:
                if ctx:
                    ctx.info("Using cached Dune data")
                    await ctx.report_progress(2, 4)
            
            # Get the cached data
            cached_data = QUERY_CACHE[cache_key]
            
            if ctx:
                ctx.info(f"Searching for '{search_value}'" + 
                         (f" in column '{search_column}'" if search_column else " in all columns"))
                await ctx.report_progress(3, 4)
            
            # Convert data back to DataFrame for easier searching
            df = pd.DataFrame(cached_data["data"])
            
            # Perform the search
            if search_column and search_column in df.columns:
                # Search in specific column
                matches = df[df[search_column].astype(str).str.contains(search_value, case=False, na=False)]
            else:
                # Search in all columns
                matches = df[df.astype(str).apply(lambda row: row.str.contains(search_value, case=False, na=False).any(), axis=1)]
            
            # Limit the results
            limited_matches = matches.head(limit)
            
            if ctx:
                ctx.info(f"Found {len(matches)} matches, returning up to {limit}")
                await ctx.report_progress(4, 4)
            
            # Prepare the response
            result = {
                "success": True,
                "query_id": query_id,
                "dune_link": f"https://dune.com/queries/{query_id}",
                "search_column": search_column,
                "search_value": search_value,
                "total_matches": len(matches),
                "showing": min(limit, len(matches)),
                "columns": list(df.columns),
                "data": limited_matches.to_dict(orient="records")
            }
            
            return format_json_response(result)
        
        except Exception as e:
            return format_json_response({
                "error": f"Error searching Dune data: {str(e)}"
            })
    
    @mcp.tool()
    async def get_dune_summary(query_id: int = 3196876, ctx: Context = None) -> str:
        """
        Get a summary of Dune Analytics data including column statistics.
        
        Parameters:
        - query_id: ID of the Dune query to summarize (default: 3196876)
        
        Returns:
        - JSON formatted summary statistics
        """
        try:
            import os
            import pandas as pd
            import numpy as np
            from dotenv import load_dotenv
            
            # Check if we need to import Dune client
            try:
                from dune_client.client import DuneClient
                from dune_client.types import QueryParameter
            except ImportError:
                return format_json_response({
                    "error": "Dune client not installed. Please install with: pip3 install dune-client"
                })
            
            if ctx:
                ctx.info(f"Generating summary for Dune query {query_id}")
                await ctx.report_progress(1, 4)
            
            # Load environment variables
            load_dotenv()
            
            # Get API key from environment
            api_key = os.environ.get("DUNE_API_KEY")
            if not api_key:
                return format_json_response({
                    "error": "DUNE_API_KEY not found in environment variables"
                })
            
            # Check if the query is already in cache
            cache_key = f"query_{query_id}"
            if cache_key not in QUERY_CACHE:
                if ctx:
                    ctx.info("Data not in cache, fetching from Dune Analytics...")
                    await ctx.report_progress(2, 4)
                
                # Initialize the Dune client
                dune = DuneClient(api_key)
                
                # Fetch the latest result from the specified query
                try:
                    query_result = dune.get_latest_result(query_id)
                    
                    # Convert to dataframe
                    df = pd.DataFrame(query_result.result.rows)
                    
                    # Store in cache as a dictionary
                    QUERY_CACHE[cache_key] = {
                        "data": df.to_dict(orient="records"),
                        "columns": list(df.columns),
                        "total_rows": len(df),
                        "query_id": query_id
                    }
                    
                    if ctx:
                        ctx.info(f"Successfully retrieved {len(df)} rows from Dune")
                
                except Exception as e:
                    return format_json_response({
                        "error": f"Failed to fetch data from Dune: {str(e)}"
                    })
            else:
                if ctx:
                    ctx.info("Using cached Dune data")
                    await ctx.report_progress(2, 4)
            
            # Get the cached data
            cached_data = QUERY_CACHE[cache_key]
            
            if ctx:
                ctx.info("Calculating summary statistics")
                await ctx.report_progress(3, 4)
            
            # Convert data back to DataFrame for analysis
            df = pd.DataFrame(cached_data["data"])
            
            # Generate summary statistics
            summary = {
                "query_id": query_id,
                "dune_link": f"https://dune.com/queries/{query_id}",
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "column_stats": {}
            }
            
            # Calculate column statistics
            for column in df.columns:
                col_data = df[column]
                col_stats = {
                    "type": str(col_data.dtype),
                    "null_count": col_data.isna().sum(),
                    "null_percentage": round(col_data.isna().mean() * 100, 2)
                }
                
                # Add numeric stats if applicable
                if pd.api.types.is_numeric_dtype(col_data):
                    col_stats.update({
                        "min": col_data.min() if not col_data.isna().all() else None,
                        "max": col_data.max() if not col_data.isna().all() else None,
                        "mean": col_data.mean() if not col_data.isna().all() else None,
                        "median": col_data.median() if not col_data.isna().all() else None
                    })
                
                # Add string stats if applicable
                elif pd.api.types.is_string_dtype(col_data) or pd.api.types.is_object_dtype(col_data):
                    # Convert to string to handle mixed types
                    str_col = col_data.astype(str)
                    col_stats.update({
                        "unique_count": str_col.nunique(),
                        "most_common": str_col.value_counts().head(3).to_dict()
                    })
                
                summary["column_stats"][column] = col_stats
            
            if ctx:
                ctx.info("Summary statistics generated")
                await ctx.report_progress(4, 4)
            
            return format_json_response(summary)
        
        except Exception as e:
            return format_json_response({
                "error": f"Error generating Dune data summary: {str(e)}"
            })
    
    @mcp.tool()
    async def clear_dune_cache(query_id: Optional[int] = None, ctx: Context = None) -> str:
        """
        Clear the Dune Analytics data cache.
        
        Parameters:
        - query_id: Specific query ID to clear from cache (if None, clears all cached queries)
        
        Returns:
        - Confirmation message
        """
        try:
            if ctx:
                ctx.info(f"Clearing Dune cache" + 
                        (f" for query {query_id}" if query_id else " for all queries"))
            
            if query_id:
                # Clear specific query
                cache_key = f"query_{query_id}"
                if cache_key in QUERY_CACHE:
                    del QUERY_CACHE[cache_key]
                    return format_json_response({
                        "success": True,
                        "message": f"Cache cleared for query {query_id}"
                    })
                else:
                    return format_json_response({
                        "success": False,
                        "message": f"Query {query_id} not found in cache"
                    })
            else:
                # Clear all queries
                query_count = len(QUERY_CACHE)
                QUERY_CACHE.clear()
                return format_json_response({
                    "success": True,
                    "message": f"Cache cleared for all {query_count} queries"
                })
        
        except Exception as e:
            return format_json_response({
                "error": f"Error clearing Dune cache: {str(e)}"
            })