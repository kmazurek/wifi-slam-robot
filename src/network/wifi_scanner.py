from wifi import Cell


def scan(net_interface):
    network_list = []

    networks = Cell.all(str(net_interface))

    for network in networks:
        network_list.append(network)

    return network_list
