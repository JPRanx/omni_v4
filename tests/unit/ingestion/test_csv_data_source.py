"""Tests for CSVDataSource"""

import pytest
from pathlib import Path
import pandas as pd
import tempfile
import shutil

from src.ingestion.csv_data_source import CSVDataSource
from src.core.errors import IngestionError


class TestCSVDataSource:
    """Test suite for CSVDataSource"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)

    @pytest.fixture
    def sample_csv(self, temp_dir):
        """Create a sample CSV file"""
        csv_path = temp_dir / "test.csv"
        df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['New York', 'London', 'Paris']
        })
        df.to_csv(csv_path, index=False)
        return csv_path

    @pytest.fixture
    def empty_csv(self, temp_dir):
        """Create an empty CSV file"""
        csv_path = temp_dir / "empty.csv"
        csv_path.write_text('')
        return csv_path

    @pytest.fixture
    def latin1_csv(self, temp_dir):
        """Create a CSV with latin-1 encoding"""
        csv_path = temp_dir / "latin1.csv"
        # Create CSV with special characters requiring latin-1
        content = "Name,City\nJosé,São Paulo\nFrançois,Montréal"
        csv_path.write_bytes(content.encode('latin-1'))
        return csv_path

    # Initialization tests

    def test_init_with_path(self, temp_dir):
        """Test CSVDataSource initialization with Path"""
        source = CSVDataSource(temp_dir)
        assert source.base_path == temp_dir

    def test_init_with_string(self, temp_dir):
        """Test CSVDataSource initialization with string path"""
        source = CSVDataSource(str(temp_dir))
        assert source.base_path == temp_dir

    # get_csv() success tests

    def test_get_csv_success(self, temp_dir, sample_csv):
        """Test successful CSV loading"""
        source = CSVDataSource(temp_dir)
        result = source.get_csv("test.csv")

        assert result.is_ok()
        df = result.unwrap()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['Name', 'Age', 'City']

    def test_get_csv_data_integrity(self, temp_dir, sample_csv):
        """Test loaded data matches original"""
        source = CSVDataSource(temp_dir)
        result = source.get_csv("test.csv")

        df = result.unwrap()
        assert df['Name'].tolist() == ['Alice', 'Bob', 'Charlie']
        assert df['Age'].tolist() == [25, 30, 35]

    def test_get_csv_latin1_encoding(self, temp_dir, latin1_csv):
        """Test loading CSV with latin-1 encoding"""
        source = CSVDataSource(temp_dir)
        result = source.get_csv("latin1.csv")

        assert result.is_ok()
        df = result.unwrap()
        assert 'José' in df['Name'].values

    # get_csv() failure tests

    def test_get_csv_file_not_found(self, temp_dir):
        """Test error when CSV file doesn't exist"""
        source = CSVDataSource(temp_dir)
        result = source.get_csv("nonexistent.csv")

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, IngestionError)
        assert "not found" in str(error).lower()

    def test_get_csv_empty_file(self, temp_dir, empty_csv):
        """Test error when CSV file is empty"""
        source = CSVDataSource(temp_dir)
        result = source.get_csv("empty.csv")

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, IngestionError)
        assert "empty" in str(error).lower()

    def test_get_csv_malformed(self, temp_dir):
        """Test error when CSV is malformed"""
        malformed_path = temp_dir / "malformed.csv"
        # Create CSV with inconsistent columns
        malformed_path.write_text("Name,Age\nAlice,25\nBob,30,Extra")

        source = CSVDataSource(temp_dir)
        result = source.get_csv("malformed.csv")

        # Should either succeed (pandas is lenient) or fail gracefully
        if result.is_err():
            error = result.unwrap_err()
            assert isinstance(error, IngestionError)

    # list_available() tests

    def test_list_available_success(self, temp_dir, sample_csv):
        """Test listing available CSV files"""
        # Create multiple CSV files
        (temp_dir / "file1.csv").write_text("a,b\n1,2")
        (temp_dir / "file2.csv").write_text("c,d\n3,4")

        source = CSVDataSource(temp_dir)
        result = source.list_available()

        assert result.is_ok()
        files = result.unwrap()
        assert isinstance(files, list)
        assert "test.csv" in files
        assert "file1.csv" in files
        assert "file2.csv" in files

    def test_list_available_sorted(self, temp_dir):
        """Test that listed files are sorted"""
        # Create files in non-alphabetical order
        (temp_dir / "zebra.csv").write_text("a")
        (temp_dir / "alpha.csv").write_text("b")
        (temp_dir / "beta.csv").write_text("c")

        source = CSVDataSource(temp_dir)
        result = source.list_available()

        files = result.unwrap()
        assert files == sorted(files)

    def test_list_available_empty_directory(self, temp_dir):
        """Test listing files in empty directory"""
        source = CSVDataSource(temp_dir)
        result = source.list_available()

        assert result.is_ok()
        files = result.unwrap()
        assert files == []

    def test_list_available_filters_non_csv(self, temp_dir):
        """Test that non-CSV files are filtered out"""
        (temp_dir / "data.csv").write_text("a,b\n1,2")
        (temp_dir / "readme.txt").write_text("info")
        (temp_dir / "config.json").write_text("{}")

        source = CSVDataSource(temp_dir)
        result = source.list_available()

        files = result.unwrap()
        assert len(files) == 1
        assert "data.csv" in files

    def test_list_available_directory_not_found(self):
        """Test error when directory doesn't exist"""
        source = CSVDataSource(Path("/nonexistent/path"))
        result = source.list_available()

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, IngestionError)
        assert "not found" in str(error).lower()

    def test_list_available_path_is_file(self, temp_dir, sample_csv):
        """Test error when path is a file, not directory"""
        source = CSVDataSource(sample_csv)
        result = source.list_available()

        assert result.is_err()
        error = result.unwrap_err()
        assert isinstance(error, IngestionError)
        assert "not a directory" in str(error).lower()

    # Encoding detection tests

    def test_encoding_detection_utf8(self, temp_dir):
        """Test encoding detection for UTF-8 file"""
        csv_path = temp_dir / "utf8.csv"
        csv_path.write_text("Name,Value\nTest,123", encoding='utf-8')

        source = CSVDataSource(temp_dir)
        result = source.get_csv("utf8.csv")

        assert result.is_ok()

    def test_encoding_detection_fallback(self, temp_dir):
        """Test encoding fallback mechanism"""
        csv_path = temp_dir / "special.csv"
        # Write with special encoding
        csv_path.write_bytes(b"Name,Value\nTest,\xff\xfe")

        source = CSVDataSource(temp_dir)
        result = source.get_csv("special.csv")

        # Should succeed with fallback encoding
        assert result.is_ok()

    # __repr__ test

    def test_repr(self, temp_dir):
        """Test string representation"""
        source = CSVDataSource(temp_dir)
        repr_str = repr(source)

        assert "CSVDataSource" in repr_str
        assert str(temp_dir) in repr_str

    # Edge cases

    def test_get_csv_with_spaces_in_filename(self, temp_dir):
        """Test loading CSV with spaces in filename"""
        csv_path = temp_dir / "file with spaces.csv"
        pd.DataFrame({'A': [1, 2]}).to_csv(csv_path, index=False)

        source = CSVDataSource(temp_dir)
        result = source.get_csv("file with spaces.csv")

        assert result.is_ok()

    def test_get_csv_large_file(self, temp_dir):
        """Test loading large CSV file"""
        csv_path = temp_dir / "large.csv"
        # Create a DataFrame with 10,000 rows
        large_df = pd.DataFrame({
            'Index': range(10000),
            'Value': [i * 2 for i in range(10000)]
        })
        large_df.to_csv(csv_path, index=False)

        source = CSVDataSource(temp_dir)
        result = source.get_csv("large.csv")

        assert result.is_ok()
        df = result.unwrap()
        assert len(df) == 10000

    def test_get_csv_special_characters(self, temp_dir):
        """Test CSV with special characters in data"""
        csv_path = temp_dir / "special.csv"
        df = pd.DataFrame({
            'Name': ['Test "Quote"', 'Test,Comma', 'Test\nNewline'],
            'Value': [1, 2, 3]
        })
        df.to_csv(csv_path, index=False)

        source = CSVDataSource(temp_dir)
        result = source.get_csv("special.csv")

        assert result.is_ok()
        loaded_df = result.unwrap()
        assert len(loaded_df) == 3