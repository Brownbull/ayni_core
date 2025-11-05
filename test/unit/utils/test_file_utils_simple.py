"""
Simple test script for file_utils (no pytest required)
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.file_utils import (
    ensure_path_exists,
    ensure_directory,
    path_exists,
    find_matching_dirs,
    save_json,
    load_json,
    get_file_size,
    normalize_path,
)


def test_ensure_directory():
    print("Testing ensure_directory...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create new directory
        new_dir = Path(tmpdir) / 'test_output'
        result = ensure_directory(new_dir)
        assert result.exists()
        assert result.is_dir()

        # Create nested directory
        nested_dir = Path(tmpdir) / 'a' / 'b' / 'c'
        result = ensure_directory(nested_dir, parents=True)
        assert result.exists()
        assert result.is_dir()

        # Existing directory (should not raise)
        result2 = ensure_directory(new_dir)
        assert result2 == new_dir

    print("  [OK] ensure_directory passed")


def test_ensure_path_exists():
    print("Testing ensure_path_exists...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = Path(tmpdir) / 'test.txt'
        test_file.write_text('test content')

        # Existing file
        result = ensure_path_exists(test_file, is_file=True)
        assert result == test_file

        # Existing directory
        result = ensure_path_exists(tmpdir, is_file=False)
        assert result == Path(tmpdir)

        # Missing file should raise
        missing_file = Path(tmpdir) / 'missing.txt'
        try:
            ensure_path_exists(missing_file, is_file=True)
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError as e:
            assert "File not found" in str(e)

    print("  [OK] ensure_path_exists passed")


def test_path_exists():
    print("Testing path_exists...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = Path(tmpdir) / 'test.txt'
        test_file.write_text('test')

        # File exists
        assert path_exists(test_file) is True
        assert path_exists(test_file, is_file=True) is True
        assert path_exists(test_file, is_file=False) is False

        # Directory exists
        assert path_exists(tmpdir) is True
        assert path_exists(tmpdir, is_file=False) is True
        assert path_exists(tmpdir, is_file=True) is False

        # Path doesn't exist
        missing = Path(tmpdir) / 'missing.txt'
        assert path_exists(missing) is False

    print("  [OK] path_exists passed")


def test_find_matching_dirs():
    print("Testing find_matching_dirs...")

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Create some directories
        (base / 'run_001').mkdir()
        (base / 'run_002').mkdir()
        (base / 'run_003').mkdir()
        (base / 'other').mkdir()

        # Find matching
        matches = find_matching_dirs(base, 'run_*')
        assert len(matches) == 3
        assert all('run_' in str(m) for m in matches)

        # No matches
        matches = find_matching_dirs(base, 'missing_*')
        assert len(matches) == 0

    print("  [OK] find_matching_dirs passed")


def test_save_and_load_json():
    print("Testing save_json and load_json...")

    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = Path(tmpdir) / 'test.json'
        test_data = {'name': 'test', 'value': 42, 'items': [1, 2, 3]}

        # Save JSON
        save_json(test_data, json_file)
        assert json_file.exists()

        # Load JSON
        loaded = load_json(json_file)
        assert loaded == test_data

        # Load missing file with default
        missing_file = Path(tmpdir) / 'missing.json'
        result = load_json(missing_file, default={})
        assert result == {}

        # Load missing file without default should raise
        try:
            load_json(missing_file)
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass

    print("  [OK] save_json and load_json passed")


def test_save_json_creates_parent_dirs():
    print("Testing save_json creates parent directories...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Nested path that doesn't exist
        nested_file = Path(tmpdir) / 'a' / 'b' / 'c' / 'test.json'
        test_data = {'nested': True}

        # Should create parent directories
        save_json(test_data, nested_file)
        assert nested_file.exists()

        loaded = load_json(nested_file)
        assert loaded == test_data

    print("  [OK] save_json creates parent dirs passed")


def test_get_file_size():
    print("Testing get_file_size...")

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / 'test.txt'
        content = 'Hello, World!'
        test_file.write_text(content)

        size = get_file_size(test_file)
        assert size == len(content.encode('utf-8'))

    print("  [OK] get_file_size passed")


def test_normalize_path():
    print("Testing normalize_path...")

    # String path
    result = normalize_path('data/file.csv')
    assert isinstance(result, Path)
    assert result.is_absolute()

    # Path object
    result = normalize_path(Path('data/file.csv'))
    assert isinstance(result, Path)
    assert result.is_absolute()

    print("  [OK] normalize_path passed")


def test_persistence_pattern():
    """Test patterns from persistence.py"""
    print("Testing persistence.py patterns...")

    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / 'state'

        # OLD: state_dir.mkdir(parents=True, exist_ok=True)
        # NEW:
        datasets_dir = ensure_directory(state_dir / 'datasets')
        assert datasets_dir.exists()

        # OLD: with open(path, 'w') as f: json.dump(data, f, indent=2)
        # NEW:
        metadata = {'run_id': 'test_123', 'timestamp': '2024-01-01'}
        save_json(metadata, state_dir / 'metadata.json')

        # OLD: with open(path, 'r') as f: data = json.load(f)
        # NEW:
        loaded = load_json(state_dir / 'metadata.json')
        assert loaded == metadata

        # OLD: if not path.exists(): raise FileNotFoundError(...)
        # NEW:
        try:
            ensure_path_exists(state_dir / 'missing.json', is_file=True)
            assert False, "Should raise"
        except FileNotFoundError:
            pass

    print("  [OK] persistence.py patterns passed")


def test_store_pattern():
    """Test patterns from store.py"""
    print("Testing store.py patterns...")

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        model = 'model1'
        feature_name = 'feature_a'

        # OLD: feature_dir = Path(...); feature_dir.mkdir(parents=True, exist_ok=True)
        # NEW:
        feature_dir = ensure_directory(base_path / model / feature_name)
        assert feature_dir.exists()

        # Save feature metadata
        metadata = {
            'feature': feature_name,
            'args': ['in_price', 'in_cost'],
            'type': 'filter'
        }
        save_json(metadata, feature_dir / 'metadata.json')

        # Load feature metadata
        loaded_meta = load_json(feature_dir / 'metadata.json')
        assert loaded_meta == metadata

    print("  [OK] store.py patterns passed")


def main():
    print("=" * 60)
    print("Running file_utils tests...")
    print("=" * 60)

    try:
        test_ensure_directory()
        test_ensure_path_exists()
        test_path_exists()
        test_find_matching_dirs()
        test_save_and_load_json()
        test_save_json_creates_parent_dirs()
        test_get_file_size()
        test_normalize_path()
        test_persistence_pattern()
        test_store_pattern()

        print("=" * 60)
        print("[OK] ALL TESTS PASSED!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
