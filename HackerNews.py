import requests
import datetime

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Top Hacker News.  Just tell me how many items you want to hear."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Say something like 'Give me the top 5'"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using Top Hacker News. " \
                    "Have a nice day "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# --------------- Intents ------------------




def updateContext(contexts, name, lifespan, parameters):
    updated = False
    for i in range(len(contexts)):
        if contexts[i].get("name", "").lower() == name.lower():
            contexts[i]["lifespan"] = lifespan
            contexts[i]["parameters"] = parameters
            updated = True
    if updated == False:
        contexts.append({"name":name.lower(),"lifespan":lifespan, "parameters":parameters})

def addSuggestions(speech = "", suggestions = [], userResponse = True, items = []):
    suggestionsTitles = []
    for item in suggestions:
        suggestionsTitles.append({"title":item})
    itemList = []
    for item in items:
        a = {}
        a["title"] = item[0]
        a["optionInfo"] = {
                'key': item[1],
                'synonyms': []
              }
        itemList.append(a)
          
    return {
  'google': {
    'expectUserResponse': True,
    'isSsml': False,
    'noInputPrompts': [],
    'richResponse': {
      'items': [
        {
          'simpleResponse': {
            'textToSpeech': speech,
            'displayText': speech
          }
        }
      ],
      'suggestions': suggestionsTitles
    },
    'systemIntent': {
      'intent': 'actions.intent.OPTION',
      'data': {
        '@type': 'type.googleapis.com/google.actions.v2.OptionValueSpec',
        'listSelect': {
          'items': itemList
        }
      }
    }
  }
}

def lookupItem(item):
    headers = {"X-Mashape-Key":"QnME8qXj33mshqT4yltM7QQk1Kfjp1vX7zJjsnoN87jXS0bYCf","Accept":"application/json"}
    r = requests.get("https://community-hacker-news-v1.p.mashape.com/item/{}.json".format(item), headers=headers)
    results = r.json()
    results["title"] = filterAsciiText(results["title"])
    return results
    # itemTitle = results.get("title", "")
    # return itemTitle

def filterAsciiText(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def getListString(listName, function = None, conjunction = "and"):
    output = ""
    if len(listName) == 0:
        return ""
    if len(listName) == 1:
        if function is not None:
            return "{}.".format(function(listName[0]))
        else:
            return "{}.".format(listName[0])
    for i in range(len(listName)):
        if i == len(listName) - 1:
            if function is not None:
                output += "{} {}.".format(conjunction, function(listName[i]))
            else:
                output += "{} {}.".format(conjunction, listName[i])
        else:
            if function is not None:
                output += "{}, ".format(function(listName[i]))
            else:
                output += "{}, ".format(listName[i])
    return output

def googleLookupIntent(req):
    print("Reached intent")
    speech =  "Lookup Top Hackernews"
    contexts = req.get("result").get("contexts")
    parameters = req.get("result").get("parameters")
    suggestions = []

    topNumber = parameters.get("top_number", 5)
    listItems = []
    speech = lookupItems(topNumber, contexts, listItems)
    # suggestions += ["Suggestion 1", "Suggestion 2","Suggestion 3"]

    print("----------- Final response -------------")
    print(filterAsciiText(speech))
    data = addSuggestions(speech, suggestions, True, listItems)
    # print(data)
    return {
    "speech": speech,
    "displayText": speech,
    "data": data,
    "contextOut": contexts,
    "source": "webhook"
    }

def lookupItems(number, contexts = [], listItems = []):
    headers = {"X-Mashape-Key":"QnME8qXj33mshqT4yltM7QQk1Kfjp1vX7zJjsnoN87jXS0bYCf","Accept":"application/json"}
    r = requests.get("https://community-hacker-news-v1.p.mashape.com/topstories.json", headers=headers)
    result = r.json()

    resultArr = []
    for count in range(int(number)):
        item = lookupItem(result[count])
        # print(item)
        resultArr.append(item)
        print(filterAsciiText("Found Item {} / {}, - {}".format(count + 1, number, item)))
    updateContext(contexts, "itemsContext", 5, resultArr)
    for i in resultArr:
        listItems.append([filterAsciiText(i["title"]), i["id"]])
    def a(b):
        return filterAsciiText(b.get("title", ""))

    speechResult = "Here is the top {} items.  {}".format(number, getListString(resultArr, a))
    print(speechResult)
    return speechResult

# lookupItems(3)
# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    r = requests.get("http://google.com")
    
    # Dispatch to your skill's intent handlers
    if intent_name == "GetTop":
        print("Get information intent detected")
        return handleLookupIntent(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session. 

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


test = {
  "id": "c899d56b-9cb4-462b-a647-693820e4df26",
  "timestamp": "2017-08-19T03:23:28.828Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "top 1",
    "action": "TopNumber",
    "actionIncomplete": False,
    "parameters": {
      "top_number": "1"
    },
    "contexts": [],
    "metadata": {
      "intentId": "9ebff9ef-5b6d-4e1c-924d-5697481fa443",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 338,
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
googleLookupIntent(test)

