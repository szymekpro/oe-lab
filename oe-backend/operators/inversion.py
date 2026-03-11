import random
from models.individual import Individual
from models.chromosome import Chromosome


class Inversion:
    """Inversion operator: reverses a random bit segment in chromosome."""

    def invert(self, individual: Individual, probability: float) -> Individual:
        new_chroms = []

        for chrom in individual.chromosomes:
            if chrom.size < 2 or random.random() > probability:
                new_chroms.append(Chromosome(chrom.domain, chrom.precision, bits_string=chrom.bits))
                continue

            start, end = sorted(random.sample(range(chrom.size), 2))
            bits = chrom.bits
            inverted = bits[:start] + bits[start:end + 1][::-1] + bits[end + 1:]
            new_chroms.append(Chromosome(chrom.domain, chrom.precision, bits_string=inverted))

        return Individual(individual.num_variables, new_chroms)
