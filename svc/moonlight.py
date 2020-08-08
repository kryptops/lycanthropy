import lycanthropy.dist.builder
from flask import Flask, request, jsonify, make_response, abort, send_from_directory
import threading
import base64

app = Flask(__name__)

#mk random config

@app.errorhandler(400)
def badRequest(e):
    return make_response(jsonify({'error':'bad request'}),400)

@app.route('/ml.srv/receiveBuild/<campaign>')
def receiveBuild(campaign):
    try:
        buildObj = request.json
        buildKey = buildObj['key']
        buildID = buildObj['id']
        buildBatch = int(buildObj['batch'])
    except:
        abort(400)
    decodedKey = base64.b64decode(buildKey).decode('utf-8')
    decodedID = base64.b64decode(buildID).decode('utf-8')
    if 'error' not in lycanthropy.dist.builder.chkBuildAccess(decodedKey,decodedID,campaign):
        if buildBatch > 5:
            buildBatch = 5
        for build in range(1, buildBatch + 1):
            buildThread = threading.Thread(target=lycanthropy.dist.builder.buildAgent, args=(buildKey, buildID,))
            buildThread.run()
        return {'moonlight.srv.status':'staged {} builds for {}'.format(str(buildBatch),campaign)}
    else:
        abort(400)

app.run(host='0.0.0.0',port=56111)
