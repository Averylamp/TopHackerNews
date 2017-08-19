import requests
import datetime



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
                'key': str(item[1]),
                'synonyms': [item[0]]
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
    # updateContext(contexts, "itemsContext", 5, resultArr)
    for i in resultArr:
        listItems.append([filterAsciiText(i["title"]), i["id"]])
    def a(b):
        return filterAsciiText(b.get("title", ""))

    speechResult = "Here is the top {} items.  {}".format(number, getListString(resultArr, a))
    print(speechResult)
    return speechResult

# lookupItems(3)
# --------------- Events ------------------


test = {
  "id": "7035052a-1080-4ff3-9ea2-c4818ffde291",
  "timestamp": "2017-08-19T03:32:55.691Z",
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
      "webhookResponseTime": 779,
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
# googleLookupIntent(test)

