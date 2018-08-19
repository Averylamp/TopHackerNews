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
          'title':'Top Hacker News',
          'items': itemList
        }
      }
    }
  }
}

def addSuggestionsCard(speech = "", suggestions = [], userResponse = True, title = "", url = "", author = "author"):
    suggestionsTitles = []
    for item in suggestions:
        suggestionsTitles.append({"title":item})
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
        },
        {
            "basicCard": {
                "title": title,
                "formattedText": "**" + title + "**\n" + "By: " + author,
                "image": {
                    "url": "https://api.letsvalidate.com/v1/thumbs?url=" + url,
                    "accessibilityText": "Website thumbnail"
                },
                "buttons": [
                    {
                        "title":title,
                        "openUrlAction":{
                          "url":url
                        }
                    }
                ]
            }
        }
      ],
      'suggestions': suggestionsTitles
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

def googleLookupNewsIntent(req):
    print("Reached News intent")
    print(req)
    speech =  "Lookup Top Hackernews"
    contexts = req.get("result").get("contexts")
    if contexts is None:
        contexts = []
    parameters = req.get("result").get("parameters")
    suggestions = []
    for context in contexts:
        if context.get("name", "") == "itemscontext":
            itemsContext = context
        if context.get("name", "") == "actions_intent_option":
            actionIntent = context
    if actionIntent == None or itemsContext == None:
        speech = "Unable to look up that article, please try again later."
        return {
        "speech": speech,
        "displayText": speech,
        "data": None,
        "contextOut": contexts,
        "source": "webhook"
        }
    newsNumber = actionIntent.get("parameters", {}).get("OPTION", None)
    if newsNumber == None:
        speech = "Unable to look up that article, please try again later."
        return {
        "speech": speech,
        "displayText": speech,
        "data": None,
        "contextOut": contexts,
        "source": "webhook"
        }
    newsData = lookupItem(newsNumber)
    speech = "Here is the news article {}.  To look up more Top Hacker News ask for a number of top articles again or say cancel.".format(newsData["title"])

    # topNumber = parameters.get("top_number", 5)
    # listItems = []
    # speech = lookupItems(topNumber, contexts, listItems)
    suggestions += ["Top 3", "Top 5","Top 10", "Top 15", "Top 20"]

    print("----------- Final response -------------")
    print(filterAsciiText(speech))
    data = addSuggestionsCard(speech, suggestions, True, newsData.get("title", "title"),newsData.get("url", "URL Not found"),newsData.get("by", "Author"))
    # print(data)
    return {
    "speech": speech,
    "displayText": speech,
    "data": data,
    "contextOut": contexts,
    "source": "webhook"
    }

def googleLookupIntent(req):
    print("Reached intent")
    speech =  "Lookup Top Hacker News"
    contexts = req.get("contexts")
    if contexts is None:
        contexts = []
    parameters = req.get("parameters")
    suggestions = []


    if parameters is not None:
        topNumber = parameters.get("top_number", 5)
        if topNumber == "":
            topNumber = 5
        if int(topNumber) > 20:
            topNumber = 20
        if int(topNumber) <= 0:
            topNumber = 3
    else:
        topNumber = 5

    listItems = []
    speech = lookupItems(topNumber, contexts, listItems)
    suggestions += ["Top 3", "Top 5","Top 10", "Top 15", "Top 20"]
    speech += " To read an option, click on it. To look up more options, say 'Top 5' or however many more you want. To end, say cancel."
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
    contextArr = []
    for count in range(int(number)):
        item = lookupItem(result[count])
        print("ITEM---------")
        print(item)
        print("End----ITEM---------")
        resultArr.append(item)
        contextArr.append({'title': filterAsciiText(item.get("title", "Item Title")), 'id':item['id'], 'url':item.get("url","https://www.apple.com/")})
        # print(filterAsciiText("Found Item {} / {}, - {}".format(count + 1, number, item)))
    print(contextArr)
    print(contexts)
    updateContext(contexts, "itemscontext", 5, {'values':contextArr})
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
  "responseId": "951305e5-4285-4c98-9dd4-eceb622296ff",
  "queryResult": {
    "queryText": "top 5",
    "action": "TopNumber",
    "parameters": {
      "top_number": 5
    },
    "allRequiredParamsPresent": True,
    "fulfillmentMessages": [
      {
        "text": {
          "text": [
            ""
          ]
        }
      }
    ],
    "intent": {
      "name": "projects/hacker-news-224eb/agent/intents/f6b5d4a2-9f09-4843-9bb7-233e36e96586",
      "displayName": "Top Intent"
    },
    "intentDetectionConfidence": 1,
    "languageCode": "en"
  },
  "originalDetectIntentRequest": {
    "payload": {}
  },
  "session": "projects/hacker-news-224eb/agent/sessions/52726685-ac01-c7a1-b620-2388aa144163"
}
googleLookupIntent(test)

