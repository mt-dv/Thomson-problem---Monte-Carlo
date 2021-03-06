import numpy
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
import click

# return a random configuration of n particles over a unitary sphere
def random_configuration(n):
    points = numpy.random.normal(size=(n, 3))
    norms = numpy.linalg.norm(points, axis=1)
    points = numpy.array([points[i] / norms[i] for i in range(n)])
    norms = numpy.linalg.norm(points, axis=1)
    assert numpy.allclose(norms, numpy.ones_like(norms))
    return points


def local_potential_energy(index, positions):
    assert (index < len(positions))
    norms = numpy.linalg.norm(positions - positions[index], axis=1)
    norms = norms[norms != 0.0]
    return numpy.sum(1.0 / norms)


def potential_energy(positions):
    energy = 0.0
    for i in range(len(positions)):
        energy += local_potential_energy(i, positions)
    return 0.5 * energy


def new_position_in_vicinity(position, sigma):
    new_position = position + sigma * numpy.random.normal(size=3)
    new_position /= numpy.linalg.norm(new_position)
    return new_position


def metropolis(index, positions, sigma, T):
    old_position = positions[index].copy()
    old_energy = local_potential_energy(index, positions)

    positions[index] = new_position_in_vicinity(positions[index], sigma)
    new_energy = local_potential_energy(index, positions)

    delta_enery = new_energy - old_energy

    if delta_enery > 0 and numpy.random.uniform() > numpy.exp(-delta_enery / T):
        positions[index] = old_position
        return False

    return True 


def MC(positions, sigma, T=0.000001):
    for _ in range(len(positions)):
        index = numpy.random.randint(0, len(positions))
        metropolis(index, positions, sigma, T)



@click.command()
@click.option("-n", default=12)
@click.option("-mcs", default=1000)
@click.option("-sigma", default=0.01)
def main(n, mcs, sigma):
    positions = random_configuration(n)
    # plot_configuration(positions)

    energy = []
    for _ in range(mcs):
        MC(positions, sigma)
        energy.append(potential_energy(positions))


    # plot_configuration(positions, charge_center=True, show=False, out="new.pdf")

    print(numpy.mean(positions, axis=0))
    print(potential_energy(positions), sigma)

    pyplot.figure()
    pyplot.plot(range(1, mcs + 1), energy, "-r")
    pyplot.grid()
    pyplot.xlabel(r"$time \ \rm [MCS]$", fontsize=20)
    pyplot.ylabel(r"$U \ \rm [adim.]$", fontsize=20)
    pyplot.title(r"$\sigma = %s$" % sigma)
    pyplot.tight_layout()
    pyplot.savefig("energy_vs_time.pdf")
    pyplot.close()

    minimum = {}
    for i, p1 in enumerate(positions):
        dists = []
        for j, p2 in enumerate(positions):
            if (i != j):
                dists.append(numpy.linalg.norm(p1 - p2))
        minimum[i] = min(dists)


    epsilon = 1e-2
    lines = []
    for i, p1 in enumerate(positions):
        min_dist = minimum[i]
        for j, p2 in enumerate(positions):
            if (i != j):
                dist = numpy.linalg.norm(p1 - p2)
                if dist <= (1.4 * min_dist):
                    lines.append((i, j))

    x, y, z = positions.T
    fig = pyplot.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(x, y, z, color="crimson", s=20)
    for i, j in lines:
        xl = positions[i][0], positions[j][0]
        yl = positions[i][1], positions[j][1]
        zl = positions[i][2], positions[j][2]
        ax.plot(xl, yl, zl, "-k")
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.set_aspect("equal")
    pyplot.show()
    pyplot.close()


if __name__ == '__main__':
    main()