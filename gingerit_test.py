from gingerit.gingerit import GingerIt

text = 'The smelt of fliwers bring back memories.'

# This is the maximum text the API can accepto
text_docs = "The Portenta H7 simultaneously runs high level code along with real time tasks, since it includes two processors that can run tasks in parallel. For example, it is possible to execute Arduino compiled code along with MicroPython one and have both cores to communicate with one another. The Portenta functionality is two-fold, it can either be running like any other embedded microcontroller board or as the main processor of an embedded computer. For instance, use the Portenta Vision Shield to transform your H7 into an industrial camera capable of performing real-time machine learning algorithms."

parser = GingerIt()
print(parser.parse(text_docs))