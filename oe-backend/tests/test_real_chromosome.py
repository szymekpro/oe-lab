"""
Unit tests for RealChromosome — the atomic building block of the real-valued
chromosome representation introduced in Projekt 2.

Theory:
    In the real-valued encoding every decision variable x_i is stored directly
    as a floating-point number within its domain [a, b].  There is no binary
    string: the chromosome IS the value.  This eliminates the quantisation
    error inherent in binary encoding and allows gradient-like operators
    (arithmetic, Gaussian) to work natively on the real line.
"""
import pytest
from models.real_chromosome import RealChromosome


DOMAIN = (-5.0, 5.0)


class TestRealChromosomeInitialization:
    """Tests that a RealChromosome is always in a consistent, valid state."""

    def test_random_value_is_within_domain(self):
        """
        WHAT: Create 200 chromosomes without specifying a value.
        EXPECTED: Every randomly generated value lies in [a, b].
        THEORY: The uniform distribution U(a, b) guarantees that all samples
                are in [a, b].  Testing many samples makes it statistically
                impossible for this to pass by chance if the implementation
                is wrong.
        """
        for _ in range(200):
            chrom = RealChromosome(DOMAIN)
            a, b = DOMAIN
            assert a <= chrom.value <= b, (
                f"Random value {chrom.value} is outside domain {DOMAIN}"
            )

    def test_explicit_value_is_stored_exactly(self):
        """
        WHAT: Construct a chromosome with value=2.5.
        EXPECTED: chrom.value == 2.5 (no rounding or encoding).
        THEORY: Unlike binary encoding, real encoding stores the float as-is.
                There must be no lossy transformation at construction time.
        """
        chrom = RealChromosome(DOMAIN, value=2.5)
        assert chrom.value == 2.5

    def test_boundary_values_are_accepted(self):
        """
        WHAT: Provide exactly a = -5.0 and b = 5.0 as values.
        EXPECTED: No exception; values stored correctly.
        THEORY: Domain boundaries are valid chromosome values (closed interval
                [a, b]).  The check must be inclusive.
        """
        chrom_low = RealChromosome(DOMAIN, value=-5.0)
        chrom_high = RealChromosome(DOMAIN, value=5.0)
        assert chrom_low.value == -5.0
        assert chrom_high.value == 5.0

    def test_value_below_domain_raises_value_error(self):
        """
        WHAT: Provide value = -6.0 (below a = -5.0).
        EXPECTED: ValueError is raised.
        THEORY: A chromosome outside the domain cannot be decoded to a
                meaningful variable, so the constructor should reject it
                immediately rather than silently corrupt the solution.
        """
        with pytest.raises(ValueError, match="out of domain"):
            RealChromosome(DOMAIN, value=-6.0)

    def test_value_above_domain_raises_value_error(self):
        """
        WHAT: Provide value = 10.0 (above b = 5.0).
        EXPECTED: ValueError is raised.
        THEORY: Same as above — the closed-interval constraint must be enforced
                on the upper boundary as well.
        """
        with pytest.raises(ValueError, match="out of domain"):
            RealChromosome(DOMAIN, value=10.0)

    def test_domain_is_stored_on_instance(self):
        """
        WHAT: Check that the domain tuple is accessible after construction.
        EXPECTED: chrom.domain == DOMAIN.
        THEORY: Crossover and mutation operators need the domain to perform
                clamping.  It must be preserved on the chromosome.
        """
        chrom = RealChromosome(DOMAIN, value=1.0)
        assert chrom.domain == DOMAIN


class TestRealChromosomeDecode:
    """Tests for the decode() method."""

    def test_decode_returns_stored_value(self):
        """
        WHAT: Call decode() on a chromosome with a known value.
        EXPECTED: decode() returns the same float that was provided.
        THEORY: In real encoding, decode() is an identity operation.
                This is in contrast to binary encoding where a binary-to-real
                conversion is required.  The method exists so that Individual
                can call decode() on both chromosome types polymorphically.
        """
        chrom = RealChromosome(DOMAIN, value=3.14)
        assert chrom.decode() == 3.14

    def test_decode_is_idempotent(self):
        """
        WHAT: Call decode() twice on the same chromosome.
        EXPECTED: Both calls return the same value.
        THEORY: decode() must be a pure function with no side effects.
                Repeated decoding of the same chromosome must yield the
                same result, otherwise fitness evaluation would be
                non-deterministic.
        """
        chrom = RealChromosome(DOMAIN, value=-2.0)
        assert chrom.decode() == chrom.decode()
