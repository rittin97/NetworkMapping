#!/usr/bin/python3
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_basicauth import BasicAuth
from json import dumps
import NetworkMappingEdited as NetworkMappingEdited

app = Flask(__name__)
api = Api(app)

app.config['BASIC_AUTH_USERNAME'] = 'password'
app.config['BASIC_AUTH_PASSWORD'] = 'password'

basic_auth = BasicAuth(app)

@app.route('/secret')
class Validate(Resource):
    @basic_auth.required
    def get(self):
        srcIp = request.args.get('srcip')
        dstIp = request.args.get('dstip')
        portName = request.args.get('prtname')
        portNumber = request.args.get('prtnumber')
        resultIsValid = NetworkMappingEdited.validate(srcIp, dstIp, portName, portNumber)
        response = make_response(jsonify(resultIsValid))
        response.headers['content-type'] = 'text/plain'
        return response


api.add_resource(Validate, '/validate')
app.run(host="0.0.0.0",
        port=443)
