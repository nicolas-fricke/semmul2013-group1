import glob

jsons = glob.glob('../../data/metadata/*/*/*.json')
print "Currently, there are {0} json files. Keep it coming!".format(len(jsons))
