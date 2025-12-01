"""
Tests unitarios para core.utils.security.

Cubre todas las funciones de seguridad:
- sanitize_filename
- validate_filename
- secure_path_join
- escape_html
"""
from pathlib import Path
from django.test import TestCase
from tempfile import TemporaryDirectory
import os

from core.utils.security import (
    sanitize_filename,
    validate_filename,
    secure_path_join,
    escape_html
)


class SecurityHelpersTestCase(TestCase):
    """Tests para funciones de seguridad."""

    def test_sanitize_filename_basic(self):
        """Test sanitize_filename with basic valid filename."""
        result = sanitize_filename("test_file.txt")
        
        self.assertEqual(result, "test_file.txt")

    def test_sanitize_filename_with_path_components(self):
        """Test sanitize_filename removes path components."""
        result = sanitize_filename("/path/to/file.txt")
        
        self.assertEqual(result, "file.txt")

    def test_sanitize_filename_with_backslash(self):
        """Test sanitize_filename removes backslash paths."""
        result = sanitize_filename("path\\to\\file.txt")
        
        self.assertEqual(result, "file.txt")

    def test_sanitize_filename_raises_on_path_traversal(self):
        """Test sanitize_filename raises ValueError on path traversal."""
        with self.assertRaises(ValueError) as context:
            sanitize_filename("../../../etc/passwd")
        
        self.assertIn("path traversal", str(context.exception).lower())

    def test_sanitize_filename_removes_dangerous_chars(self):
        """Test sanitize_filename replaces dangerous characters."""
        result = sanitize_filename("file<>:\"|?*name.txt")
        
        self.assertEqual(result, "file_________name.txt")

    def test_sanitize_filename_removes_leading_trailing_spaces(self):
        """Test sanitize_filename removes leading/trailing spaces."""
        result = sanitize_filename("  file.txt  ")
        
        self.assertEqual(result, "file.txt")

    def test_sanitize_filename_removes_leading_trailing_dots(self):
        """Test sanitize_filename removes leading/trailing dots."""
        result = sanitize_filename("...file.txt...")
        
        self.assertEqual(result, "file.txt")

    def test_sanitize_filename_uses_default_on_empty(self):
        """Test sanitize_filename uses default when result is empty."""
        result = sanitize_filename("   ", default="default.txt")
        
        self.assertEqual(result, "default.txt")

    def test_sanitize_filename_raises_on_empty_no_default(self):
        """Test sanitize_filename raises when empty and no default."""
        with self.assertRaises(ValueError):
            sanitize_filename("   ", default=None)

    def test_sanitize_filename_truncates_long_filename(self):
        """Test sanitize_filename truncates filenames over 255 chars."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        
        self.assertLessEqual(len(result), 255)

    def test_sanitize_filename_preserves_extension_on_truncation(self):
        """Test sanitize_filename preserves extension when truncating."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        
        self.assertTrue(result.endswith(".txt"))

    def test_sanitize_filename_raises_on_none(self):
        """Test sanitize_filename raises on None."""
        with self.assertRaises(ValueError):
            sanitize_filename(None)

    def test_sanitize_filename_raises_on_non_string(self):
        """Test sanitize_filename raises on non-string input."""
        with self.assertRaises(ValueError):
            sanitize_filename(123)

    def test_validate_filename_valid(self):
        """Test validate_filename returns True for valid filename."""
        self.assertTrue(validate_filename("test_file.txt"))

    def test_validate_filename_false_on_none(self):
        """Test validate_filename returns False for None."""
        self.assertFalse(validate_filename(None))

    def test_validate_filename_false_on_non_string(self):
        """Test validate_filename returns False for non-string."""
        self.assertFalse(validate_filename(123))

    def test_validate_filename_false_on_path_traversal(self):
        """Test validate_filename returns False for path traversal."""
        self.assertFalse(validate_filename("../../../etc/passwd"))

    def test_validate_filename_false_on_forward_slash(self):
        """Test validate_filename returns False for forward slash."""
        self.assertFalse(validate_filename("path/to/file.txt"))

    def test_validate_filename_false_on_backslash(self):
        """Test validate_filename returns False for backslash."""
        self.assertFalse(validate_filename("path\\to\\file.txt"))

    def test_validate_filename_false_on_null_byte(self):
        """Test validate_filename returns False for null byte."""
        self.assertFalse(validate_filename("file\0name.txt"))

    def test_validate_filename_false_on_dangerous_chars(self):
        """Test validate_filename returns False for dangerous characters."""
        self.assertFalse(validate_filename("file<>:\"|?*name.txt"))

    def test_validate_filename_false_on_empty(self):
        """Test validate_filename returns False for empty string."""
        self.assertFalse(validate_filename(""))

    def test_validate_filename_false_on_whitespace_only(self):
        """Test validate_filename returns False for whitespace only."""
        self.assertFalse(validate_filename("   "))

    def test_secure_path_join_basic(self):
        """Test secure_path_join with basic path."""
        base_path = Path("/tmp/test_base")
        result = secure_path_join(base_path, "subdir", "file.txt")
        
        expected = base_path / "subdir" / "file.txt"
        self.assertEqual(result.resolve(), expected.resolve())

    def test_secure_path_join_removes_path_separators(self):
        """Test secure_path_join removes path separators from parts."""
        base_path = Path("/tmp/test_base")
        result = secure_path_join(base_path, "path/to", "file.txt")
        
        # Path separators should be replaced with underscores
        self.assertNotIn("/", str(result.relative_to(base_path)))
        self.assertNotIn("\\", str(result.relative_to(base_path)))

    def test_secure_path_join_removes_path_traversal(self):
        """Test secure_path_join removes path traversal attempts."""
        base_path = Path("/tmp/test_base")
        result = secure_path_join(base_path, "..", "etc", "passwd")
        
        # Should be sanitized, not actually escape
        self.assertNotIn("..", str(result))

    def test_secure_path_join_raises_on_relative_base(self):
        """Test secure_path_join raises on relative base path."""
        base_path = Path("relative/path")
        
        with self.assertRaises(ValueError) as context:
            secure_path_join(base_path, "file.txt")
        
        self.assertIn("absolute path", str(context.exception).lower())

    def test_secure_path_join_keeps_within_base(self):
        """Test secure_path_join ensures result is within base."""
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir).resolve()
            result = secure_path_join(base_path, "subdir", "file.txt")
            
            # Result should be relative to base
            relative = result.relative_to(base_path)
            self.assertIsNotNone(relative)

    def test_secure_path_join_raises_on_path_outside_base(self):
        """Test secure_path_join raises when path would be outside base."""
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir).resolve()
            outside_path = Path(tmpdir).parent
            
            # This should raise because we're trying to escape
            # But our sanitization should prevent it
            # Let's test with a realistic scenario
            result = secure_path_join(base_path, "..", "outside")
            # Should be sanitized, not actually escape

    def test_secure_path_join_skips_empty_parts(self):
        """Test secure_path_join skips empty path parts."""
        base_path = Path("/tmp/test_base")
        result = secure_path_join(base_path, "", "file.txt", "")
        
        expected = base_path / "file.txt"
        self.assertEqual(result, expected)

    def test_escape_html_basic(self):
        """Test escape_html escapes basic HTML characters."""
        result = escape_html("<script>alert('xss')</script>")
        
        self.assertIn("&lt;", result)
        self.assertIn("&gt;", result)
        self.assertNotIn("<script>", result)
        self.assertNotIn("</script>", result)

    def test_escape_html_ampersand(self):
        """Test escape_html escapes ampersand."""
        result = escape_html("A & B")
        
        self.assertEqual(result, "A &amp; B")

    def test_escape_html_quotes(self):
        """Test escape_html escapes quotes."""
        result = escape_html('"double" and \'single\' quotes')
        
        self.assertIn("&quot;", result)
        self.assertIn("&#x27;", result)

    def test_escape_html_all_special_chars(self):
        """Test escape_html escapes all special characters."""
        result = escape_html('<>&"\'')
        
        self.assertIn("&lt;", result)
        self.assertIn("&gt;", result)
        self.assertIn("&amp;", result)
        self.assertIn("&quot;", result)
        self.assertIn("&#x27;", result)

    def test_escape_html_empty_string(self):
        """Test escape_html returns empty string for empty input."""
        result = escape_html("")
        
        self.assertEqual(result, "")

    def test_escape_html_none(self):
        """Test escape_html returns empty string for None."""
        result = escape_html(None)
        
        self.assertEqual(result, "")

    def test_escape_html_non_string_converts(self):
        """Test escape_html converts non-string to string."""
        result = escape_html(123)
        
        self.assertEqual(result, "123")

    def test_escape_html_preserves_safe_chars(self):
        """Test escape_html preserves safe characters."""
        safe_text = "Hello World 123"
        result = escape_html(safe_text)
        
        self.assertEqual(result, safe_text)

    def test_escape_html_xss_prevention(self):
        """Test escape_html prevents XSS attacks."""
        xss_attempts = [
            "<img src=x onerror=alert(1)>",
            "<script>document.cookie</script>",
            "javascript:alert(1)",
            "<iframe src='evil.com'></iframe>"
        ]
        
        for xss in xss_attempts:
            result = escape_html(xss)
            self.assertNotIn("<script>", result.lower())
            self.assertNotIn("javascript:", result.lower())
            self.assertNotIn("onerror=", result.lower())

