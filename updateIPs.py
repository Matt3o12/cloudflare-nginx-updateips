import sys
import requests

BASE_URL = "https://www.cloudflare.com/ips-{}"
DEFAULT_FORWARD_HEADER = "CF-Connecting-IP"


def showHelp(output=None):
    """
    Shows the help page
    """
    if output is None:
        output = sys.stderr

    with open("help.txt", "r") as helpFile:
        for line in helpFile:
            output.write(line)

    if hasattr(output, "flush"):
        output.flush()


def main(args=None):
    """
    Starts the script
    """
    if args is None:
        args = sys.argv

    if "--help" in args:
        showHelp()
        sys.exit(0)

    try:
        parsed = parseArgs(args)
    except IndexError:
        showHelp()
        sys.exit(1)

    ips = fetchResource("v4")
    if not parsed["ipv4Only"]:
        ips.extend(fetchResource("v6"))

    output = None
    closeOuput = False
    try:
        filename = parsed["output"]
        if filename:
            output = open(filename, "w")
            closeOuput = True
        else:
            output = sys.stdout

        template = generateTemplate(ips, parsed["header"])
        output.write(template)
        output.flush()
    finally:
        if closeOuput and output:
            output.close()


def parseArgs(args):
    """
    Parses the arguments.

    It may raise an IndexError if there was an error parsing the args.
    """
    parameters = [
        ["ipv4Only", "--ipv4-only", "--ipv4", "-4"],
        ["header: str", "-h", "--header"],
        ["output: str", "-f", "--file"],  #TODO: Implement properly.
    ]

    parsedArgs = {
        "ipv4Only": False,
        "header": DEFAULT_FORWARD_HEADER,
        "output": "",
    }

    for i, param in enumerate(parameters):
        key = param[0]
        useStr = False
        if ": str" in key:
            useStr = True
            key = key[:-5]

        value = None
        for needle in param[1:]:
            if needle not in args:
                continue

            if useStr:
                value = args[args.index(needle) + 1]
            else:
                value = True

        if value:
            parsedArgs[key] = value

    return parsedArgs


def getURL(name):
    """
    Formats the BASE_URL properly.
    """
    return BASE_URL.format(name)


def fetchResource(name):
    """
    Fetches a resource from the server.
    Many things can go wrong at this point (invalid status code), etc.
    This method may throw all kinds of IO related exceptions.
    """
    response = requests.get(getURL(name))
    response.raise_for_status()
    lines = []
    for line in response.text.split("\n"):
        line = line.strip()
        if line == "":
            continue

        lines.append(line)

    return lines


def generateTemplate(ips, forwardHeader):
    """
    Generates the template using ips (list) and forwardHeader (str)
    """
    text = ""
    template = "set_real_ip_from   {};\n"
    for ip in ips:
        text += template.format(ip)

    text += "real_ip_header     {};\n".format(forwardHeader)

    return text


if "__main__" == __name__:
    main()
