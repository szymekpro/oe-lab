"""
Unit tests for the two real-valued mutation operators introduced in P2:
    1. UniformRealMutation  (mutacja równomierna)
    2. GaussianMutation     (mutacja Gaussa)

Theory — why mutation in real encoding differs from binary:
    In binary encoding mutation flips individual bits — a local change in
    the binary representation that can translate to a large jump in the
    decoded real value.  In real encoding, mutation acts directly on the
    real-valued gene:

    • Uniform mutation replaces a gene with a fresh random value drawn
      uniformly from the domain.  This is a global exploration move — it
      can jump anywhere in [a, b] regardless of the current value.

    • Gaussian mutation adds small normally-distributed noise to the current
      gene value.  This is a local exploitation move — the offspring stays
      near the parent.  The standard deviation σ controls the step size.
      Together these two operators balance global exploration (uniform) and
      local exploitation (Gaussian), similar to the role of temperature in
      simulated annealing.
"""
import pytest
from models.real_chromosome import RealChromosome
from models.real_individual import RealIndividual
from operators.real_mutation import UniformRealMutation, GaussianMutation

DOMAIN = (-5.0, 5.0)


def _ind(values: list) -> RealIndividual:
    chroms = [RealChromosome(DOMAIN, v) for v in values]
    return RealIndividual(len(values), chroms)


def _all_in_domain(individual: RealIndividual) -> bool:
    a, b = DOMAIN
    return all(a <= ch.value <= b for ch in individual.chromosomes)


# ---------------------------------------------------------------------------
# UniformRealMutation
# ---------------------------------------------------------------------------

class TestUniformRealMutation:

    def test_probability_zero_individual_unchanged(self):
        """
        WHAT: Mutate with probability=0.0.
        EXPECTED: Returned individual has the same gene values as the original.
        THEORY: With probability=0 no gene should ever be mutated.  This is
                used to deactivate mutation during experiments and to verify
                that the probability gate is correctly implemented.
        """
        mut = UniformRealMutation()
        original = _ind([1.0, 2.0, 3.0])
        result = mut.mutate(original, probability=0.0)
        assert result.get_decoded_values() == original.get_decoded_values()

    def test_probability_one_all_genes_within_domain(self):
        """
        WHAT: Mutate with probability=1.0, 100 times.
        EXPECTED: All genes of every mutated individual remain in [-5, 5].
        THEORY: The operator samples from U(a, b) so no generated value can
                ever lie outside [a, b].  The domain constraint is
                automatically satisfied.
        """
        mut = UniformRealMutation()
        ind = _ind([0.0, 0.0, 0.0])
        for _ in range(100):
            result = mut.mutate(ind, probability=1.0)
            assert _all_in_domain(result)

    def test_mutated_individual_is_a_new_object(self):
        """
        WHAT: Mutate an individual and compare object identities.
        EXPECTED: result is not original (new individual object is returned).
        THEORY: Mutation must not modify the individual in-place.  The parent
                individual might still be referenced in the parents_pool or
                by the elitism module for the current generation.
        """
        mut = UniformRealMutation()
        original = _ind([1.0])
        result = mut.mutate(original, probability=1.0)
        assert result is not original

    def test_original_individual_is_not_modified(self):
        """
        WHAT: Mutate with probability=1.0 and inspect the original.
        EXPECTED: Original's chromosome values are unchanged.
        THEORY: Mutation operates on copies, not references.  Modifying the
                original would corrupt the parents_pool, potentially causing
                the algorithm to lose track of good solutions carried over
                by elitism.
        """
        mut = UniformRealMutation()
        original = _ind([2.5, -1.5])
        _ = mut.mutate(original, probability=1.0)
        assert original.chromosomes[0].value == 2.5
        assert original.chromosomes[1].value == -1.5

    def test_probability_one_can_change_gene_values(self):
        """
        WHAT: Mutate a fixed individual 100 times with probability=1.0.
        EXPECTED: At least one mutation changes at least one gene value.
        THEORY: Uniform mutation replaces the value with a fresh sample from
                U(a, b).  Since the domain has non-zero measure, the chance
                of sampling exactly the original value is zero.  After 100
                independent samples it is practically impossible that all
                values are unchanged.
        """
        mut = UniformRealMutation()
        original_values = [0.0, 0.0]
        at_least_one_changed = False
        for _ in range(100):
            result = mut.mutate(_ind(original_values), probability=1.0)
            if result.get_decoded_values() != original_values:
                at_least_one_changed = True
                break
        assert at_least_one_changed


# ---------------------------------------------------------------------------
# GaussianMutation
# ---------------------------------------------------------------------------

class TestGaussianMutation:

    def test_probability_zero_individual_unchanged(self):
        """
        WHAT: Mutate with probability=0.0.
        EXPECTED: Gene values are preserved exactly.
        THEORY: Same reasoning as uniform mutation — the probability gate must
                be respected regardless of the mutation strategy.
        """
        mut = GaussianMutation(sigma=0.5)
        original = _ind([1.0, -2.0])
        result = mut.mutate(original, probability=0.0)
        assert result.get_decoded_values() == original.get_decoded_values()

    def test_values_clamped_to_domain(self):
        """
        WHAT: Start at a domain boundary (value = 5.0), mutate 500 times
              with a very large sigma to guarantee attempted exceedance.
        EXPECTED: All mutated values remain in [-5, 5].
        THEORY: Adding Gaussian noise can push the gene beyond [a, b].
                The implementation must clamp the result: v = clip(v + N(0,σ), a, b).
                Without clamping, the individual would encode a value outside
                the test function's domain.
        """
        mut = GaussianMutation(sigma=5.0, relative=False)
        ind = _ind([5.0, -5.0])
        for _ in range(500):
            result = mut.mutate(ind, probability=1.0)
            assert _all_in_domain(result)

    def test_sigma_zero_raises_value_error(self):
        """
        WHAT: Construct GaussianMutation with sigma=0.
        EXPECTED: ValueError is raised.
        THEORY: A sigma of zero produces a degenerate Gaussian — every sample
                would equal the mean, so mutation would have no effect.
                Requiring sigma > 0 prevents silent no-op bugs.
        """
        with pytest.raises(ValueError, match="sigma"):
            GaussianMutation(sigma=0)

    def test_relative_sigma_scales_with_domain_width(self):
        """
        WHAT: Use relative=True with sigma=1.0 (100 % of domain width).
              Domain is (-5, 5) so effective sigma = 1.0 * 10 = 10.0.
              Start at 0.0 and mutate 500 times.
        EXPECTED: At least some results are far from 0.0 (> 2.0 in absolute
                  value), demonstrating that the effective sigma was large.
        THEORY: relative=True scales sigma by (b - a), making the noise
                magnitude proportional to the domain width.  This makes
                the operator self-adaptive across domains of different scales
                (e.g., x ∈ [-1,1] vs. x ∈ [-1000, 1000]).
        """
        mut = GaussianMutation(sigma=1.0, relative=True)
        ind = _ind([0.0])
        far_from_zero = 0
        for _ in range(500):
            result = mut.mutate(ind, probability=1.0)
            if abs(result.chromosomes[0].value) > 2.0:
                far_from_zero += 1
        assert far_from_zero > 50, (
            "Expected many large steps with sigma=1.0 relative to domain width 10"
        )

    def test_absolute_sigma_does_not_scale(self):
        """
        WHAT: Use relative=False with sigma=0.01 (tiny absolute step).
              Start at 0.0 and mutate 100 times.
        EXPECTED: All results stay very close to 0.0 (within ±0.1).
        THEORY: With relative=False the effective sigma is exactly sigma,
                not multiplied by domain width.  A small absolute sigma
                produces only local perturbations regardless of domain.
        """
        mut = GaussianMutation(sigma=0.01, relative=False)
        ind = _ind([0.0])
        for _ in range(100):
            result = mut.mutate(ind, probability=1.0)
            assert abs(result.chromosomes[0].value) <= 0.1

    def test_mutated_individual_is_new_object(self):
        """
        WHAT: Compare identity of original and mutated individual.
        EXPECTED: result is not original.
        THEORY: Same immutability requirement as uniform mutation.
        """
        mut = GaussianMutation(sigma=0.1)
        original = _ind([1.0])
        result = mut.mutate(original, probability=1.0)
        assert result is not original

    def test_fitness_is_reset_to_none_after_mutation(self):
        """
        WHAT: Set fitness=10.0, then mutate the individual.
        EXPECTED: Returned individual has fitness=None.
        THEORY: A mutated individual has a new genotype and therefore an
                unknown fitness.  Carrying over the parent's fitness would
                be incorrect — the algorithm would use a stale value and
                potentially skip evaluating the new genotype.
        """
        mut = GaussianMutation(sigma=0.1)
        ind = _ind([1.0, 2.0])
        ind.fitness = 10.0
        result = mut.mutate(ind, probability=1.0)
        assert result.fitness is None
