from wifi import Cell, Scheme

def Search():
    network_list = []

    networks = Cell.all('wlan0')

    for network in networks:
        network_list.append(network)

    return network_list

if __name__ == '__main__':
    print(Search())