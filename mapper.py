from wifi import Cell

def Search():
    network_list = []

    networks = Cell.all('wlan0')

    for network in networks:
        network_list.append(network)

    return network_list

if __name__ == '__main__':
    for cell in Search():
        print(cell.ssid + " " + str(cell.signal))