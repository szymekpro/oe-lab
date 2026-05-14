"""
Unit tests for all five real-valued crossover operators introduced in P2:
    1. ArithmeticCrossover  (krzyżowanie arytmetyczne)
    2. LinearCrossover      (krzyżowanie liniowe)
    3. BlendAlphaCrossover  (BLX-α)
    4. BlendAlphaBetaCrossover (BLX-α-β)
    5. AveragingCrossover   (krzyżowanie uśredniające)

Theory — why crossover in real encoding differs from binary:
    Binary crossover swaps sub-strings of bits.  For real chromosomes the
    genome is a vector of floats, so "recombination" means combining the
    parent values arithmetically.  Real crossover operators can exploit the
    metric structure of ℝⁿ (distances, convex combinations) and thus produce
    offspring that are semantically "between" or "around" their parents —
    something binary operators can only approximate.
"""
import pytest
from models.real_chromosome import RealChromosome
from models.real_individual import RealIndividual
from operators.real_crossover import (
    ArithmeticCrossover,
    LinearCrossover,
    BlendAlphaCrossover,
    BlendAlphaBetaCrossover,
    AveragingCrossover,
)
from engine.functions import Hypersphere

DOMAIN = (-5.0, 5.0)


def _ind(values: list) -> RealIndividual:
    chroms = [RealChromosome(DOMAIN, v) for v in values]
    return RealIndividual(len(values), chroms)


def _all_in_domain(individual: RealIndividual) -> bool:
    a, b = DOMAIN
    return all(a <= ch.value <= b for ch in individual.chromosomes)


# ---------------------------------------------------------------------------
# ArithmeticCrossover
# ---------------------------------------------------------------------------

class TestArithmeticCrossover:

    def test_children_values_are_within_domain(self):
        """
        WHAT: Cross two parents with extreme values (-5, -5) and (5, 5).
        EXPECTED: Both children have all genes in [-5, 5].
        THEORY: c1 = alpha*p1 + (1-alpha)*p2 is a convex combination when
                alpha ∈ [0,1].  A convex combination of two points in a
                convex set (a closed interval) always lies inside that set.
                No clamping should be needed, but it is applied defensively.
        """
        cx = ArithmeticCrossover()
        p1, p2 = _ind([-5.0, -5.0]), _ind([5.0, 5.0])
        for _ in range(50):
            c1, c2 = cx.crossover(p1, p2, probability=1.0)
            assert _all_in_domain(c1)
            assert _all_in_domain(c2)

    def test_child_is_convex_combination_of_parents(self):
        """
        WHAT: Cross p1=[2.0, -1.0] and p2=[4.0, 3.0] 100 times.
        EXPECTED: Every child gene lies in [min(p1_i, p2_i), max(p1_i, p2_i)].
        THEORY: alpha ∈ [0,1] ⟹ c1_i = alpha*p1_i + (1-alpha)*p2_i ∈
                [min(p1_i,p2_i), max(p1_i,p2_i)].  This is the defining
                property of a convex combination.
        """
        cx = ArithmeticCrossover()
        p1, p2 = _ind([2.0, -1.0]), _ind([4.0, 3.0])
        for _ in range(100):
            c1, c2 = cx.crossover(p1, p2, probability=1.0)
            for i, (v1, v2) in enumerate(zip(
                p1.get_decoded_values(), p2.get_decoded_values()
            )):
                lo, hi = min(v1, v2), max(v1, v2)
                assert lo <= c1.chromosomes[i].value <= hi
                assert lo <= c2.chromosomes[i].value <= hi

    def test_probability_zero_returns_clones_of_parents(self):
        """
        WHAT: Call crossover with probability=0.0.
        EXPECTED: Children are exact copies of the parents.
        THEORY: When the crossover event does not fire (probability check
                fails), the operator must pass the parent genotypes unchanged
                into the next generation.  This preserves diversity and
                allows independent mutation to act on unmodified parents.
        """
        cx = ArithmeticCrossover()
        p1, p2 = _ind([1.0, 2.0]), _ind([3.0, 4.0])
        c1, c2 = cx.crossover(p1, p2, probability=0.0)
        assert c1.get_decoded_values() == p1.get_decoded_values()
        assert c2.get_decoded_values() == p2.get_decoded_values()

    def test_returns_new_individuals_not_same_objects(self):
        """
        WHAT: Compare identity (is) of parents and children.
        EXPECTED: c1 is not p1, c2 is not p2.
        THEORY: Operators must return new objects.  Modifying a parent
                in-place would corrupt the parents_pool and cause the same
                individual to appear with a different genotype later in the
                same generation.
        """
        cx = ArithmeticCrossover()
        p1, p2 = _ind([1.0]), _ind([2.0])
        c1, c2 = cx.crossover(p1, p2, probability=1.0)
        assert c1 is not p1
        assert c2 is not p2


# ---------------------------------------------------------------------------
# LinearCrossover
# ---------------------------------------------------------------------------

class TestLinearCrossover:

    def test_returns_two_of_three_best_candidates(self):
        """
        WHAT: Cross p1=[1.0] and p2=[3.0] with Hypersphere (min problem).
              Linear crossover generates z1=2.0, z2=0.0 (after clamp: 0.0
              within domain ok), z3=4.0.  Fitnesses: z1=4, z2=0, z3=16.
              Best 2 for minimisation: z2 (0) and z1 (4).
        EXPECTED: Returned children have fitness ≤ worst candidate's fitness.
        THEORY: Linear crossover evaluates all three candidates and returns
                the two with the best fitness.  This is an on-line fitness
                evaluation embedded in the operator, making it more
                computationally expensive but ensuring offspring are at
                least as good as the average of the three candidates.
        """
        fn = Hypersphere()
        cx = LinearCrossover(test_function=fn, is_minimization=True)
        p1, p2 = _ind([1.0]), _ind([3.0])
        c1, c2 = cx.crossover(p1, p2, probability=1.0)

        # Both children must have been evaluated (fitness set by the operator)
        assert c1.fitness is not None
        assert c2.fitness is not None

        worst_candidate_fitness = max(c1.fitness, c2.fitness)
        # The third candidate (worst) was discarded, so the two returned
        # must both be <= the worst of those two
        assert c1.fitness <= worst_candidate_fitness
        assert c2.fitness <= worst_candidate_fitness

    def test_probability_zero_returns_clones(self):
        """
        WHAT: Call linear crossover with probability=0.0.
        EXPECTED: Children are copies of parents.
        THEORY: Same reasoning as arithmetic crossover — no-crossover case
                must preserve the parent genotypes.
        """
        fn = Hypersphere()
        cx = LinearCrossover(test_function=fn, is_minimization=True)
        p1, p2 = _ind([0.5, -0.5]), _ind([1.0, 1.0])
        c1, c2 = cx.crossover(p1, p2, probability=0.0)
        assert c1.get_decoded_values() == p1.get_decoded_values()
        assert c2.get_decoded_values() == p2.get_decoded_values()

    def test_children_within_domain(self):
        """
        WHAT: Cross parents with extreme values 100 times.
        EXPECTED: All returned genes are in [-5, 5].
        THEORY: The linear combinations 1.5*p - 0.5*q and -0.5*p + 1.5*q
                can produce values outside [min(p,q), max(p,q)].  Clamping
                to the domain is required to keep solutions feasible.
        """
        fn = Hypersphere()
        cx = LinearCrossover(test_function=fn, is_minimization=True)
        p1, p2 = _ind([-4.0, 4.0]), _ind([4.0, -4.0])
        for _ in range(50):
            c1, c2 = cx.crossover(p1, p2, probability=1.0)
            assert _all_in_domain(c1)
            assert _all_in_domain(c2)


# ---------------------------------------------------------------------------
# BlendAlphaCrossover (BLX-α)
# ---------------------------------------------------------------------------

class TestBlendAlphaCrossover:

    def test_children_within_domain(self):
        """
        WHAT: Cross extreme parents 200 times with alpha=0.5.
        EXPECTED: All children's genes are in [-5, 5].
        THEORY: BLX-α samples from [min - α·d, max + α·d] which can extend
                outside [a, b].  The implementation must clamp to the domain
                to ensure feasibility.
        """
        cx = BlendAlphaCrossover(alpha=0.5)
        p1, p2 = _ind([-5.0, -5.0]), _ind([5.0, 5.0])
        for _ in range(200):
            c1, c2 = cx.crossover(p1, p2, probability=1.0)
            assert _all_in_domain(c1)
            assert _all_in_domain(c2)

    def test_alpha_zero_children_stay_within_parent_range(self):
        """
        WHAT: Cross p1=[1.0] and p2=[3.0] with alpha=0.0, 100 times.
        EXPECTED: Every child gene is in [1.0, 3.0].
        THEORY: With alpha=0, the sampling interval collapses to
                [min(p1,p2), max(p1,p2)].  The operator becomes equivalent
                to a uniform crossover on the real segment between parents.
        """
        cx = BlendAlphaCrossover(alpha=0.0)
        p1, p2 = _ind([1.0, 2.0]), _ind([3.0, 4.0])
        for _ in range(100):
            c1, c2 = cx.crossover(p1, p2, probability=1.0)
            assert 1.0 <= c1.chromosomes[0].value <= 3.0
            assert 2.0 <= c1.chromosomes[1].value <= 4.0

    def test_negative_alpha_raises(self):
        """
        WHAT: Construct BlendAlphaCrossover with alpha=-0.1.
        EXPECTED: ValueError.
        THEORY: A negative alpha inverts the extension — the sampling
                interval would be narrower than [min, max], which is
                not the intended BLX-α semantics.
        """
        with pytest.raises(ValueError):
            BlendAlphaCrossover(alpha=-0.1)

    def test_probability_zero_returns_clones(self):
        """
        WHAT: Call blend_alpha crossover with probability=0.0.
        EXPECTED: Children are copies of parents.
        """
        cx = BlendAlphaCrossover(alpha=0.5)
        p1, p2 = _ind([1.0, -1.0]), _ind([2.0, -2.0])
        c1, c2 = cx.crossover(p1, p2, probability=0.0)
        assert c1.get_decoded_values() == p1.get_decoded_values()
        assert c2.get_decoded_values() == p2.get_decoded_values()

    def test_two_children_are_independently_sampled(self):
        """
        WHAT: Cross the same parents 100 times with alpha=1.0.
        EXPECTED: At least once c1 and c2 differ (with very high probability).
        THEORY: Each child is sampled independently from the same interval.
                If they were always identical, only half the genetic diversity
                would be produced per crossover event — comparable to
                averaging crossover.
        """
        cx = BlendAlphaCrossover(alpha=1.0)
        p1, p2 = _ind([-3.0]), _ind([3.0])
        seen_different = False
        for _ in range(100):
            c1, c2 = cx.crossover(p1, p2, probability=1.0)
            if c1.chromosomes[0].value != c2.chromosomes[0].value:
                seen_different = True
                break
        assert seen_different, "c1 and c2 were always identical — not independent"


# ---------------------------------------------------------------------------
# BlendAlphaBetaCrossover (BLX-α-β)
# ---------------------------------------------------------------------------

class TestBlendAlphaBetaCrossover:

    def test_children_within_domain(self):
        """
        WHAT: Cross extreme parents 200 times with alpha=0.5, beta=0.3.
        EXPECTED: All genes in [-5, 5].
        THEORY: BLX-α-β samples from [min - β·d, max + α·d].  With large
                alpha or beta, values can go well outside [a, b].  Clamping
                is mandatory.
        """
        cx = BlendAlphaBetaCrossover(alpha=0.5, beta=0.3)
        p1, p2 = _ind([-5.0, -5.0]), _ind([5.0, 5.0])
        for _ in range(200):
            c1, c2 = cx.crossover(p1, p2, probability=1.0)
            assert _all_in_domain(c1)
            assert _all_in_domain(c2)

    def test_asymmetry_alpha_vs_beta(self):
        """
        WHAT: Cross p1=[0.0] and p2=[2.0] with alpha=2.0, beta=0.0, 500 times.
        EXPECTED: Some child genes exceed max(p1, p2) = 2.0 (extension upward
                  from alpha > 0) but none fall below min = 0.0 (beta=0 ⟹
                  no downward extension).
        THEORY: BLX-α-β is asymmetric: alpha extends above the parent range,
                beta extends below.  With beta=0 the lower boundary is exact;
                with alpha>0 the upper boundary is extended.  This allows the
                operator to be biased in one direction — useful when the
                optimal solution is known to lie on one side.
        """
        cx = BlendAlphaBetaCrossover(alpha=2.0, beta=0.0)
        p1, p2 = _ind([0.0]), _ind([2.0])
        exceeded_above = False
        for _ in range(500):
            c1, _ = cx.crossover(p1, p2, probability=1.0)
            v = c1.chromosomes[0].value
            # beta=0 means lower bound == min(p1,p2) = 0.0
            assert v >= 0.0 - 1e-9
            if v > 2.0:
                exceeded_above = True
        assert exceeded_above, "Expected some children above 2.0 with alpha=2.0"

    def test_probability_zero_returns_clones(self):
        cx = BlendAlphaBetaCrossover(alpha=0.5, beta=0.5)
        p1, p2 = _ind([1.0]), _ind([2.0])
        c1, c2 = cx.crossover(p1, p2, probability=0.0)
        assert c1.get_decoded_values() == p1.get_decoded_values()
        assert c2.get_decoded_values() == p2.get_decoded_values()


# ---------------------------------------------------------------------------
# AveragingCrossover
# ---------------------------------------------------------------------------

class TestAveragingCrossover:

    def test_child_gene_equals_mean_of_parents(self):
        """
        WHAT: Cross p1=[2.0, -4.0] and p2=[4.0, 2.0].
        EXPECTED: Each child gene == (p1_i + p2_i) / 2.
        THEORY: Averaging crossover is the most conservative real operator:
                it produces the midpoint between two parents.  This guarantees
                that children are always feasible (convex combination with
                equal weights) but reduces diversity over time — the population
                converges toward the centroid.
        """
        cx = AveragingCrossover()
        p1, p2 = _ind([2.0, -4.0]), _ind([4.0, 2.0])
        c1, c2 = cx.crossover(p1, p2, probability=1.0)
        assert c1.chromosomes[0].value == pytest.approx(3.0)
        assert c1.chromosomes[1].value == pytest.approx(-1.0)

    def test_both_children_are_identical(self):
        """
        WHAT: Cross any two parents and compare children.
        EXPECTED: c1.get_decoded_values() == c2.get_decoded_values().
        THEORY: Averaging produces exactly one unique offspring (the midpoint).
                Both "children" are copies of it so the population size stays
                constant.  This is correct by design.
        """
        cx = AveragingCrossover()
        p1, p2 = _ind([1.0, 2.0, 3.0]), _ind([-1.0, -2.0, -3.0])
        c1, c2 = cx.crossover(p1, p2, probability=1.0)
        assert c1.get_decoded_values() == c2.get_decoded_values()

    def test_child_within_domain(self):
        """
        WHAT: Cross extreme parents.
        EXPECTED: Child genes in [-5, 5].
        THEORY: (a + b)/2 where a,b ∈ [-5,5] always yields a value in [-5,5]
                because the midpoint of two points in a convex set is also
                in that set.
        """
        cx = AveragingCrossover()
        p1, p2 = _ind([-5.0, -5.0]), _ind([5.0, 5.0])
        c1, _ = cx.crossover(p1, p2, probability=1.0)
        assert _all_in_domain(c1)

    def test_probability_zero_returns_clones(self):
        """
        WHAT: Call averaging crossover with probability=0.0.
        EXPECTED: Children are copies of parents (not averages).
        """
        cx = AveragingCrossover()
        p1, p2 = _ind([1.0, -1.0]), _ind([3.0, -3.0])
        c1, c2 = cx.crossover(p1, p2, probability=0.0)
        assert c1.get_decoded_values() == p1.get_decoded_values()
        assert c2.get_decoded_values() == p2.get_decoded_values()
