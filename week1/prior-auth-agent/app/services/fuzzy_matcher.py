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

        FIX: Enhanced algorithm combines token-based (word order independent)
        and sequence-based (character-level) similarity for better matching.
        This handles cases like "MRI Brain" vs "Brain MRI" effectively.
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

        # Calculate token-based similarity (Jaccard index - word order independent)
        tokens1 = set(normalized1.split())
        tokens2 = set(normalized2.split())

        if not tokens1 or not tokens2:
            # Fallback to sequence similarity if no tokens
            distance = self.levenshtein_distance(normalized1, normalized2)
            max_length = max(len(normalized1), len(normalized2))
            return 1.0 - (distance / max_length)

        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        token_similarity = len(intersection) / len(union) if union else 0.0

        # Calculate sequence similarity (Levenshtein - character-level)
        distance = self.levenshtein_distance(normalized1, normalized2)
        max_length = max(len(normalized1), len(normalized2))
        sequence_similarity = 1.0 - (distance / max_length)

        # Weighted average: 60% token-based (better for word reordering), 40% sequence-based
        score = (0.6 * token_similarity) + (0.4 * sequence_similarity)

        logger.debug(
            f"Fuzzy match: '{text1[:50]}...' vs '{text2[:50]}...' = {score:.3f} "
            f"(token={token_similarity:.3f}, sequence={sequence_similarity:.3f})"
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
