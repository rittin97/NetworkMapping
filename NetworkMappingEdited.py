import socket

import binascii

from netaddr import IPNetwork, IPAddress

import xlrd

import re

from xlutils.copy import copy

#TODO this scripts helps to check if an ip address is contained within a subnet or not

loc = ("DC Matrix.xlsx")  #TODO Give the location of the file

wb = xlrd.open_workbook(loc)  #TODO Open wb as excel sheet

sheet = wb.sheet_by_index(0)  #TODO starts reading from origin


def ip_in_subnetwork(ip_address, subnetwork):
    """

    Returns True if the given IP address belongs to the

    subnetwork expressed in CIDR notation, otherwise False.

    Both parameters are strings.



    Both IPv4 addresses/subnetworks (e.g. "192.168.1.1"

    and "192.168.1.0/24") and IPv6 addresses/subnetworks (e.g.

    "2a02:a448:ddb0::" and "2a02:a448:ddb0::/44") are accepted.

    """
    try:
        (ip_integer, version1) = ip_to_integer(ip_address)

    except:
        return 0

    (ip_lower, ip_upper, version2) = subnetwork_to_ip_range(subnetwork)

    if version1 != version2:
        raise ValueError("incompatible IP versions")

    return (ip_lower <= ip_integer <= ip_upper)


def ip_to_integer(ip_address):
    """

    Converts an IP address expressed as a string to its

    representation as an integer value and returns a tuple

    (ip_integer, version), with version being the IP version

    (either 4 or 6).



    Both IPv4 addresses (e.g. "192.168.1.1") and IPv6 addresses

    (e.g. "2a02:a448:ddb0::") are accepted.

    """

    #TODO try parsing the IP address first as IPv4, then as IPv6

    for version in (socket.AF_INET, socket.AF_INET6):

        try:

            ip_hex = socket.inet_pton(version, ip_address)

            ip_integer = int(binascii.hexlify(ip_hex), 16)

            return (ip_integer, 4 if version == socket.AF_INET else 6)

        except:

            return 0


def subnetwork_to_ip_range(subnetwork):
    """

    Returns a tuple (ip_lower, ip_upper, version) containing the

    integer values of the lower and upper IP addresses respectively

    in a subnetwork expressed in CIDR notation (as a string), with

    version being the subnetwork IP version (either 4 or 6).



    Both IPv4 subnetworks (e.g. "192.168.1.0/24") and IPv6

    subnetworks (e.g. "2a02:a448:ddb0::/44") are accepted.

    """

    try:

        fragments = subnetwork.split('/')

        network_prefix = fragments[0]

        netmask_len = int(fragments[1])

        #todo try parsing the subnetwork first as IPv4, then as IPv6

        for version in (socket.AF_INET, socket.AF_INET6):

            ip_len = 32 if version == socket.AF_INET else 128

            try:

                suffix_mask = (1 << (ip_len - netmask_len)) - 1

                netmask = ((1 << ip_len) - 1) - suffix_mask

                ip_hex = socket.inet_pton(version, network_prefix)

                ip_lower = int(binascii.hexlify(ip_hex), 16) & netmask

                ip_upper = ip_lower + suffix_mask

                return (ip_lower,

                        ip_upper,

                        4 if version == socket.AF_INET else 6)

            except:

                return 0

    except:

        return 0


def ValidateSourceIp(ip_src):
    """
    This function takes the source ip address, goes from top to bottom 1 row at a time and scans for a match.
    If the match is found it stores the row number of that particular zone. Subnets are not allowed. Returns Row Number.
    """

    counter = 1
    RowNumber = 0
    for j in range(2, sheet.nrows):  # todo runs the number of times (total zones)
        endLoop = 0
        cellValues = re.split(r'\s+', sheet.cell_value(j, 0))  # TODO Splits multiple cell values if separated by a white spaces
        counter += 1
        for cell in cellValues:  # TODO Helps break down multiple rows in a cell
            skip = 0
            for chars in cell:
                if chars.isalpha() is True:
                    skip = 1
                    break
                if chars == '(' or chars == ')':
                    skip = 1
                    break
            if skip == 1:
                continue
            if cell == '':
                continue
            if ip_src == '':
                break
            if ip_src != '':
                if '/' in ip_src:
                    if IPNetwork(ip_src) in IPNetwork(cell):  # todo If a subnetwork is populated in the source IP field
                        RowNumber = 0
                        break
                else:  # TODO To check whether given ip is available in a subnet
                    if ip_in_subnetwork(ip_src, cell) is True:
                        RowNumber = counter
                        endLoop = 1
                        break
        if endLoop == 1:
            break
    return RowNumber


def ValidateDestinationIp(ip_dst):
    """
        This function takes the destination ip address, goes from left to right 1 column at a time and scans for a match.
        If the match is found it stores the column number of that particular zone. Subnets are not allowed.
        Returns column Number.
    """
    counter = 0
    ColNumber = 0
    for j in range(1, sheet.ncols):
        endLoop = 0
        cellValues = re.split(r'\s+', sheet.cell_value(1, j))  # TODO Splits multiple cell values if separated by a new line
        counter += 1
        for cell in cellValues:  # TODO Helps break down multiple rows in a cell
            skip = 0
            for chars in cell:
                if chars.isalpha() is True:
                    skip = 1
                    break
                if chars == '(' or chars == ')':
                    skip = 1
                    break
            if skip == 1:
                continue
            if cell == '':
                continue
            if ip_dst == '':
                break
            if ip_dst != '':
                if '/' in ip_dst:
                    if IPNetwork(ip_dst) in IPNetwork(cell):  # todo If a subnetwork is populated in the destination IP field
                        ColNumber = 0
                        break
                else:  # TODO To check whether given ip is available in a subnet
                    if ip_in_subnetwork(ip_dst, cell) is True:
                        ColNumber = counter
                        endLoop = 1
                        break
        if endLoop == 1:
            break
    return ColNumber


def ValidatePort(port_name, port_number, ColNumber):
    """
        Gets the following inputs: port_name, port_number, Column Number. First checks the ColNumber, if 0 then returns
        false, then port name is if invalid then return false otherwise proceed to port number if valid then return true
        else false.
    """
    if ColNumber == 0:
        return False
    if ('-' in str(port_number)) or (',' in str(port_number)) or ('>' in str(port_number)) or ('<' in str(port_number)):
        return False
    portcell_value = sheet.cell_value(0, ColNumber)  #todo port cell value in spreadsheet
    port_cell = re.split(r'\n', portcell_value)     #todo split by a new line
    for values in port_cell:        #todo each row in a port cell
        if port_name in values:
            if '-' in values:
                spaceDelimiter = re.split(r'\s+', values)
                port_value = spaceDelimiter[1]
                dashDelimiter = re.split(r'-', port_value)
                first = dashDelimiter[0]
                second = dashDelimiter[1]
                if int(port_number) in range(int(first), int(second) + 1):
                    return True
            else:
                spaceDelimiter = re.split(r'\s+', values)
                port_value = spaceDelimiter[1]
                if int(port_number) == int(port_value):
                    return True
    return False


def validate(src_ip, dst_ip, port_name, port_number):
    """
        This is the main function which gets all the inputs and passes them to required above functions for validation.
        Checks each condition one by one in the following source ip, destination ip, port name and at last port number
        If all the conditions are true then return true if any of the condition is false then return false.
    """
    RowNumber = ValidateSourceIp(src_ip)
    ColNumber = ValidateDestinationIp(dst_ip)
    port_check = None
    if RowNumber == 0:
        result = False
    elif ColNumber == 0:
        result = False
    else:
        result = True
    firewall_cell_value = sheet.cell_value(RowNumber, ColNumber)
    if firewall_cell_value == 'Not Allowed' or firewall_cell_value == 'Not allowed' or \
            firewall_cell_value == 'n/a' or firewall_cell_value == 'Not allowed to other Tiers':
        result = False
    if result is True:
        port_check = ValidatePort(port_name, port_number, ColNumber)
    if result is True and port_check is True:
        return True
    else:
        return False


def main():
    return None