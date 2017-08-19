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
	print(res)
	res = json.dumps(res, indent=4)
	
	r = make_response(res)
	r.headers['Content-Type'] = 'application/json'
	return r


def processRequest(req):
	if req.get("result").get("action") == "TopNumber":
		print("Top number detected")
		a = HackerNews.googleLookupIntent(req)
		print( " ---------------------------")
		return a
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
				  "textToSpeech":"Thank you for using Hacker News.  Hope to see you back soon!",
				  "displayText":"Thank you for using Hacker News.  Hope to see you back soon!"
			   }
			}
		 ],
		 "suggestions": []
		  }
	   }
	}
	return {
		"speech": "Thank you for using Hacker News.  Hope to see you back soon!",
		"displayText": "Thank you for using Hacker News.  Hope to see you back soon!",
		"data": data,
		"contextOut": {},
		"source": "webhook"
	}
		
test = {
  "id": "dcaa7b6e-2fe8-47ed-baa5-5fad6cedc2af",
  "timestamp": "2017-08-19T06:06:24.822Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "top 3",
    "action": "TopNumber",
    "actionIncomplete": False,
    "parameters": {
      "top_number": "3"
    },
    "contexts": [],
    "metadata": {
      "intentId": "9ebff9ef-5b6d-4e1c-924d-5697481fa443",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 1148,
      "intentName": "Top Intent"
    },
    "fulfillment": {
      "speech": "",
      "messages": [
        {
          "type": 0,
          "speech": ""
        }
      ]
    },
    "score": 1
  },
  "status": {
    "code": 206,
    "errorType": "partial_content",
    "errorDetails": "Webhook call failed. Error: Webhook response was empty."
  },
  "sessionId": "c849e9e7-3c08-45c4-9df6-4a438214aeb9"
}
print(processRequest(test))
# if __name__ == '__main__':
# 	port = int(os.getenv('PORT', 5000))

# 	print("Starting app on port %d" % port)

# 	app.run(debug=False, port=port, host='0.0.0.0')
