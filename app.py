#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import HackerNews

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/', methods=['GET'])
def loadingPage():
	return "Hello loading page"


@app.route('/webhook', methods=['POST'])
def webhook():
	req = request.get_json(silent=True, force=True)

	print("Request Recieved:")
	# print(json.dumps(req, indent=4))

	res = processRequest(req)
	print("Response: ")
	print(res["speech"])
	res = json.dumps(res, indent=4)
	
	r = make_response(res)
	r.headers['Content-Type'] = 'application/json'
	return r


def processRequest(req):
	# if req.get("result").get("action") == "LookUpClass":
	# 	print("Class Lookup Detected")
	# 	return MITClass.lookupClass(req)
	if req.get("result").get("action") == "EndIntent":
		return endIntent()
	
	return {
		"speech": "Unable to proccess the request.  Try again later please.",
		"displayText": "Unable to proccess the request.  Try again later please.",
		# "data": data,
		"contextOut": [],
		"source": "webhook"
	}

def endIntent():
	data =  {"google":{
	  "expect_user_response":False,
	  "rich_response":{
		 "items":[
			{
			   "simpleResponse":{
				  "textToSpeech":"Thank you for using MIT Information.  Keep us in mind when you need more of your on campus information.",
				  "displayText":"Thank you for using MIT Information.  Keep us in mind when you need more of your on campus information."
			   }
			}
		 ],
		 "suggestions": []
		  }
	   }
	}
	return {
		"speech": "Thank you for using MIT Information.  Keep us in mind when you need more of your on campus information.",
		"displayText": "Thank you for using MIT Information.  Keep us in mind when you need more of your on campus information.",
		"data": data,
		"contextOut": {},
		"source": "webhook"
	}
		


if __name__ == '__main__':
	port = int(os.getenv('PORT', 5000))

	print("Starting app on port %d" % port)

	app.run(debug=False, port=port, host='0.0.0.0')
