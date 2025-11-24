"""
CSV Handler for EyeD AI Attendance System

This module provides abstracted CSV operations (read, write, append, filter)
for the attendance repository. This component follows SRP by handling ONLY
CSV-specific operations.

No domain dependencies - pure infrastructure component.
"""

import io
from typing import Any, Dict, List, Optional
import logging
import pandas as pd

from .file_storage import FileStorage

logger = logging.getLogger(__name__)


class CSVHandler:
    """
    CSV handler that provides abstracted CSV operations.
    
    This class handles ONLY CSV-specific operations following the Single
    Responsibility Principle. No business logic, data validation, or
    domain operations are performed here.
    
    All file I/O operations are delegated to FileStorage.
    """
    
    def __init__(self, file_storage: FileStorage):
        """
        Initialize CSV handler.
        
        Args:
            file_storage: Injected file storage handler for file operations
        """
        if not isinstance(file_storage, FileStorage):
            raise TypeError("file_storage must be an instance of FileStorage")
        self.file_storage = file_storage
        logger.debug("CSVHandler initialized")
    
    def read_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Read CSV file and return list of dictionaries.
        
        Each dictionary represents a row with column names as keys.
        Returns empty list if file doesn't exist.
        
        Args:
            file_path: Path to the CSV file to read
            
        Returns:
            List of dictionaries, each representing a row
        """
        if not self.csv_exists(file_path):
            logger.debug(f"CSV file does not exist: {file_path}, returning empty list")
            return []
        
        try:
            # Read file content using FileStorage
            csv_content = self.file_storage.read_text_file(file_path, encoding="utf-8")
            
            # Parse CSV content using pandas
            if not csv_content.strip():
                logger.debug(f"CSV file is empty: {file_path}")
                return []
            
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Convert DataFrame to list of dictionaries
            data = df.to_dict('records')
            
            logger.debug(f"Read {len(data)} rows from CSV: {file_path}")
            return data
            
        except pd.errors.EmptyDataError:
            logger.warning(f"CSV file is empty or has no data: {file_path}")
            return []
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing CSV file: {file_path} - {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error reading CSV file: {file_path} - {e}")
            return []
    
    def write_csv(
        self,
        file_path: str,
        data: List[Dict[str, Any]],
        headers: Optional[List[str]] = None
    ) -> bool:
        """
        Write data to CSV file.
        
        Headers are inferred from data if not provided. If data is empty
        and headers are provided, creates a file with only headers.
        
        Args:
            file_path: Path to the CSV file to write
            data: List of dictionaries to write (each dict is a row)
            headers: Optional list of column names (inferred from data if not provided)
            
        Returns:
            True on success, False on failure
        """
        try:
            # Determine headers
            if headers is None:
                if data:
                    # Infer headers from first row
                    headers = list(data[0].keys())
                else:
                    logger.warning(f"No data and no headers provided for CSV: {file_path}")
                    return False
            
            # Create DataFrame
            if data:
                df = pd.DataFrame(data, columns=headers)
            else:
                # Create empty DataFrame with headers only
                df = pd.DataFrame(columns=headers)
            
            # Convert DataFrame to CSV string
            csv_content = df.to_csv(index=False, lineterminator='\n')
            
            # Write using FileStorage
            success = self.file_storage.write_text_file(
                file_path,
                csv_content,
                encoding="utf-8"
            )
            
            if success:
                logger.debug(f"Wrote {len(data)} rows to CSV: {file_path}")
            else:
                logger.error(f"Failed to write CSV file: {file_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Unexpected error writing CSV file: {file_path} - {e}")
            return False
    
    def append_csv(
        self,
        file_path: str,
        row: Dict[str, Any]
    ) -> bool:
        """
        Append single row to CSV file.
        
        Creates file with headers if it doesn't exist.
        
        Args:
            file_path: Path to the CSV file
            row: Dictionary representing a row to append
            
        Returns:
            True on success, False on failure
        """
        try:
            # Check if file exists
            if not self.csv_exists(file_path):
                # Create new file with headers from the row
                logger.debug(f"CSV file does not exist, creating new file: {file_path}")
                return self.write_csv(file_path, [row], headers=list(row.keys()))
            
            # Read existing data
            existing_data = self.read_csv(file_path)
            
            # Append new row
            existing_data.append(row)
            
            # Get headers (from existing file or from new row)
            headers = self.get_headers(file_path)
            if not headers:
                headers = list(row.keys())
            
            # Write all data back
            return self.write_csv(file_path, existing_data, headers=headers)
            
        except Exception as e:
            logger.error(f"Unexpected error appending to CSV file: {file_path} - {e}")
            return False
    
    def filter_csv(
        self,
        file_path: str,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filter CSV rows based on criteria.
        
        Filters are applied as exact matches. A row matches if all
        specified filter criteria are satisfied.
        
        Args:
            file_path: Path to the CSV file
            filters: Dictionary of column_name: value pairs for filtering
            
        Returns:
            Filtered list of dictionaries
        """
        try:
            # Read all data
            data = self.read_csv(file_path)
            
            if not data or not filters:
                return data
            
            # Filter data
            filtered_data = []
            for row in data:
                match = True
                for column, value in filters.items():
                    if column not in row or row[column] != value:
                        match = False
                        break
                if match:
                    filtered_data.append(row)
            
            logger.debug(
                f"Filtered CSV: {file_path} - {len(filtered_data)} rows match "
                f"filters {filters} out of {len(data)} total rows"
            )
            return filtered_data
            
        except Exception as e:
            logger.error(f"Unexpected error filtering CSV file: {file_path} - {e}")
            return []
    
    def csv_exists(self, file_path: str) -> bool:
        """
        Check if CSV file exists.
        
        Args:
            file_path: Path to the CSV file to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.file_storage.file_exists(file_path)
    
    def get_headers(self, file_path: str) -> List[str]:
        """
        Get CSV column headers.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of header names, empty list if file doesn't exist or is empty
        """
        if not self.csv_exists(file_path):
            logger.debug(f"CSV file does not exist: {file_path}")
            return []
        
        try:
            # Read file content using FileStorage
            csv_content = self.file_storage.read_text_file(file_path, encoding="utf-8")
            
            if not csv_content.strip():
                logger.debug(f"CSV file is empty: {file_path}")
                return []
            
            # Read only first line to get headers
            df = pd.read_csv(io.StringIO(csv_content), nrows=0)
            headers = list(df.columns)
            
            logger.debug(f"Retrieved {len(headers)} headers from CSV: {file_path}")
            return headers
            
        except pd.errors.EmptyDataError:
            logger.warning(f"CSV file is empty or has no headers: {file_path}")
            return []
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing CSV headers: {file_path} - {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error reading CSV headers: {file_path} - {e}")
            return []














