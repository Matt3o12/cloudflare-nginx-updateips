from __future__ import print_function

from updateIPs import generateTemplate, fetchResource, showHelp

import unittest
import updateIPs
import threading

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except:
    from http.server import BaseHTTPRequestHandler, HTTPServer


def startResourceServer():
    httpd = HTTPServer(("localhost", 0), ResourceHandler)

    def start():
        httpd.handle_request()
        httpd.socket.close()

    thread = threading.Thread(target=start)
    thread.daemon = True
    thread.start()

    return httpd, thread


class ResourceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text")
        self.end_headers()

        self.wfile.write(b"10.0.0.1\n")
        self.wfile.write(b"10.0.0.2\n")

    def log_message(self, *args, **kwargs):
        # We really don't care about logs (cause the spam the test output).
        pass


class IntegrationTestCase(unittest.TestCase):
    def assertFetch(self, name):
        ips = updateIPs.fetchResource(name)
        self.assertGreater(len(ips), 1)

    def testDownloadIPv4(self):
        self.assertFetch("v4")

    def testDownloadIPv6(self):
        self.assertFetch("v6")


class TestCase(unittest.TestCase):
    def testFetchResource(self):
        defaultURL = updateIPs.BASE_URL
        httpd, handlerThread = startResourceServer()
        ips = []
        try:
            url = "http://{}:{}/".format(*httpd.server_address) + "{}"
            updateIPs.BASE_URL = url
            ips = updateIPs.fetchResource("v4")
        finally:
            updateIPs.BASE_URL = defaultURL
            handlerThread.join(1)
            if handlerThread.is_alive():
                raise Exception("Handler thread could not be closed")

        self.assertEqual(ips, ["10.0.0.1", "10.0.0.2"])

    def testGenerateTemplate(self):
        ips = ["0.0.0.0", "::1", "hostname.tld"]
        expected = "\n".join([
            "set_real_ip_from   0.0.0.0;",
            "set_real_ip_from   ::1;",
            "set_real_ip_from   hostname.tld;",
            "real_ip_header     Madeup IP header;",
        ]) + "\n"
        self.assertEqual(
            expected, updateIPs.generateTemplate(ips, "Madeup IP header"))

    def assertParse(self, args,
                    header=updateIPs.DEFAULT_FORWARD_HEADER,
                    ipv4=False,
                    output=""):
        expected = {"header": header, "ipv4Only": ipv4, "output": output}
        self.assertEqual(expected, updateIPs.parseArgs(args))

    def testParseDefault(self):
        self.assertParse([])

    def testParseHeader(self):
        self.assertParse(["-h", "test"], header="test")
        self.assertParse(["--header", "hello-world"], header="hello-world")

    def testParseHeaderMissingArg(self):
        with self.assertRaises(IndexError):
            updateIPs.parseArgs(["-h"])

        with self.assertRaises(IndexError):
            updateIPs.parseArgs(["--header"])

    def testParseIPv4(self):
        self.assertParse(["-4"], ipv4=True)
        self.assertParse(["--ipv4"], ipv4=True)
        self.assertParse(["--ipv4-only"], ipv4=True)

    def testParseOutput(self):
        self.assertParse(["-f", "test"], output="test")
        self.assertParse(["--file", "foobar"], output="foobar")

    def testParseOutputMissingArg(self):
        with self.assertRaises(IndexError):
            updateIPs.parseArgs(["test", "-f"])

    def testParseMixed(self):
        params = ["-h", "hello world", "-4", "--file", "ba"]
        self.assertParse(params, "hello world", True, output="ba")

    def testParseInvalidParams(self):
        params = [
            "tesst", "-h", "cloudflare-header", "--ipv4-only", "Hello world",
            "--file", "foobarz", "hello"
        ]
        self.assertParse(params, "cloudflare-header", True, output="foobarz")

    def testHelp(self):
        with open("help.txt", "r") as f:
            expected = f.read()

        stream = StringIO()
        showHelp(stream)
        self.assertEqual(expected, stream.getvalue())

    # def testMainShowHelp(self):
    #     # TODO: Figure out a way to test it without printing
    #     with self.assertRaises(SystemExit):
    #         updateIPs.main("-h")

    # TODO: Add more tests for main (if possible)
