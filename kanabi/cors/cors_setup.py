import os
import re


def load_domains_from_file():
    """
    Loads domain strings from file and parses the strings for wildcards. Strings containing wildcards are then
    converted into proper regex expressions and then placed into the origin list. This list is then used by CORS
    to allow for Cross-Domain Origin Requests for resources based on the various entries in that list.

    Each line of the 'accepted_domains.ini' file is converted into a regular expression.
    Lines beginning with a '#' are comments and are skipped. Empty lines are also skipped.
    Lines beginning with a '!' are raw regular expressions, and will be passed unmodified (minus the starting '!').

    Successful and unsuccessful CORS requests will still return a 200 OK response. The primary difference is that
    the successful responses will also contain the Access-Control-Allow-Methods, Access-Control-Allow-Headers,
    and Access-Control-Allow-Origin headers. It will not necessarily generate a failure message like browsers do.

    Simulate the cross-domain GET request using:
    $ curl -H "Origin: DOMAIN_NAME" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: X-Requested-With" \
        -X OPTIONS --verbose \
        http://SERVER_IP_ADDRESS:PORTNUM/RESOURCE_PATH/RESOURCE_NAME

    Sample output on successful request
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Content-Type: text/html; charset=utf-8
    < Allow: HEAD, GET, OPTIONS
    < Vary: Origin
    < Access-Control-Allow-Methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
    < Access-Control-Allow-Headers: X-Requested-With
    < Access-Control-Allow-Origin: www.example.com
    < Content-Length: 0
    < Server: Werkzeug/1.0.1 Python/3.5.2
    < Date: Thu, 23 Apr 2020 05:19:17 GMT

    Sample output on unsuccessful request:
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Content-Type: text/html; charset=utf-8
    < Allow: HEAD, GET, OPTIONS
    < Content-Length: 0
    < Server: Werkzeug/1.0.1 Python/3.5.2
    < Date: Thu, 23 Apr 2020 05:19:03 GMT
    """
    origin_list = []

    # Build the relative path to the file
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "accepted_domains.ini")

    # Populate the list of domains
    with open(path) as f:
        raw_list = f.read().splitlines()

    # Skip over comment lines and empty lines, and remove the '!' in front of raw regular expressions
    for line in raw_list:
        if not line:
            continue
        if line[0] == '#':
            continue
        if line[0] == '!':
            origin_list += line[1:]
            continue
    # Parse for special characters and insert the backspace escape character before each one
        line = re.sub(r'(?P<spchar>[^\w\s*.-])', r'\\\g<spchar>', line)
    # Generate a properly formatted regex string that utilizes wildcards and domain formatting
        line = re.sub(r'(?P<protocol>^.*)[.]?\*\.(?P<name>[\w]+$)', '^\g<protocol>.*\.\g<name>$', line.rstrip())
        origin_list += [line]
    return origin_list
