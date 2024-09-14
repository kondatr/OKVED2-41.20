import matplotlib.pyplot as plt

from graphs.revenue import revenue_map, revenue_top10_graph
from graphs.net_profit import growth_years_graph, net_profit_graph
from graphs.EBITDA import EBITDA_graph


def main():

    revenue_map()

    revenue_top10_graph()

    growth_years_graph()

    net_profit_graph()

    EBITDA_graph()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()