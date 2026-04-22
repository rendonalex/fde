"""Tests for fuzzy matching algorithm [per Claude.md A40]."""
import pytest
from app.services.fuzzy_matcher import FuzzyMatcher


class TestFuzzyMatcher:
    """Test fuzzy string matching algorithm."""

    def setup_method(self):
        """Set up test fixtures."""
        self.matcher = FuzzyMatcher(threshold=0.8)

    def test_exact_match(self):
        """Test exact string match returns score of 1.0."""
        score = self.matcher.fuzzy_match_score("MRI Brain", "MRI Brain")
        assert score == 1.0

    def test_case_insensitive(self):
        """Test matching is case-insensitive."""
        score = self.matcher.fuzzy_match_score("MRI Brain", "mri brain")
        assert score == 1.0

    def test_punctuation_ignored(self):
        """Test punctuation is ignored."""
        score = self.matcher.fuzzy_match_score("MRI Brain with Contrast", "MRI Brain, with Contrast!")
        assert score == 1.0

    def test_similar_strings_high_score(self):
        """Test similar strings return high scores."""
        score = self.matcher.fuzzy_match_score("MRI Brain with Contrast", "Brain MRI with Contrast")
        assert score > 0.8

    def test_different_strings_low_score(self):
        """Test different strings return low scores."""
        score = self.matcher.fuzzy_match_score("MRI Brain", "CT Chest")
        assert score < 0.5

    def test_empty_strings(self):
        """Test empty strings return 0.0."""
        score = self.matcher.fuzzy_match_score("", "MRI Brain")
        assert score == 0.0

    def test_is_match_above_threshold(self):
        """Test is_match returns True for scores above threshold."""
        is_match, score = self.matcher.is_match("MRI Brain with Contrast", "Brain MRI with Contrast")
        assert is_match is True
        assert score > 0.8

    def test_is_match_below_threshold(self):
        """Test is_match returns False for scores below threshold."""
        is_match, score = self.matcher.is_match("MRI Brain", "CT Chest")
        assert is_match is False
        assert score < 0.8

    def test_normalize_text(self):
        """Test text normalization."""
        normalized = FuzzyMatcher.normalize_text("MRI Brain, with Contrast!")
        assert normalized == "mri brain with contrast"

    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculation."""
        distance = FuzzyMatcher.levenshtein_distance("kitten", "sitting")
        assert distance == 3  # 3 substitutions needed
