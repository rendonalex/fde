"""Fuzzy matching algorithm for CPT code and service description matching [per Claude.md A40]."""
import re
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """
    Fuzzy string matching using Levenshtein distance.

    Implements the algorithm specified in Claude.md A40 and specs/api-specifications.md.
    """

    def __init__(self, threshold: float = 0.8):
        """
        Initialize fuzzy matcher.

        Args:
            threshold: Minimum similarity score (0.0-1.0) to consider a match.
                      Default 0.8 per Claude.md A40.
        """
        self.threshold = threshold
        logger.info(f"Initialized FuzzyMatcher with threshold {threshold}")

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for comparison.

        - Convert to lowercase
        - Remove punctuation
        - Collapse multiple spaces

        Per Claude.md specs/api-specifications.md fuzzy matching algorithm.
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)

        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings.

        Returns the minimum number of single-character edits required
        to transform s1 into s2.
        """
        if len(s1) < len(s2):
            return FuzzyMatcher.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def fuzzy_match_score(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two texts.

        Returns:
            Float between 0.0 (no match) and 1.0 (exact match).

        Per Claude.md specs/api-specifications.md:
        score = 1.0 - (levenshtein_distance / max_length)
        """
        if not text1 or not text2:
            return 0.0

        # Normalize both texts
        normalized1 = self.normalize_text(text1)
        normalized2 = self.normalize_text(text2)

        if not normalized1 or not normalized2:
            return 0.0

        # Handle exact match
        if normalized1 == normalized2:
            return 1.0

        # Calculate Levenshtein distance
        distance = self.levenshtein_distance(normalized1, normalized2)
        max_length = max(len(normalized1), len(normalized2))

        # Calculate similarity score
        score = 1.0 - (distance / max_length)

        logger.debug(
            f"Fuzzy match: '{text1[:50]}...' vs '{text2[:50]}...' = {score:.3f}"
        )

        return score

    def is_match(self, text1: str, text2: str) -> Tuple[bool, float]:
        """
        Check if two texts match above threshold.

        Returns:
            Tuple of (is_match: bool, score: float)
        """
        score = self.fuzzy_match_score(text1, text2)
        is_match = score >= self.threshold
        return is_match, score
