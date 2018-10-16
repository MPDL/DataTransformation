import requests # a python package for url web communication interfaces
import json

def loginRequest(namePass):
    # namePass should be a string in form of "name:password"
    url = 'https://dev.inge.mpdl.mpg.de/rest/login'
    response = requests.post(url, data=namePass)
    if response.ok:
        return response.headers['Token']
    else:
        response.raise_for_status()

def affRequest(name, ouID_MPI):
    name = name.lower()
    for symb in "?/;:!~[]":
        name = name.replace(symb,'')
    name = name.replace(',',' ').replace('-',' ')
    name_part = name.split()
    # print("target name: %s" % name)
    # for i in range(int(len(name_part))):
    #     name_part[i]
    internalFlag = False
    if "mpi" in name_part:
        # print("internal aff")
        internalFlag = True
        # name = name + "Max Planck Institute "
        name_part.append("Max Planck Institute")
        name_part[0] += "^2"
        name = " ".join(name_part)
    elif (sum(["max" in p for p in name_part]) and sum(["planck" in p for p in name_part]) and sum(["institut" in p for p in name_part])):
        # print("internal aff")
        internalFlag = True
        # name = name + "MPI "
        name_part.append("MPI")
        name_part[0] += "^2"
        name = " ".join(name_part)
    else:
        name = " AND ".join(name_part)
    queryText = name
    # print(queryText)
    query_string = {"fields": ["metadata.name", "name", "alternativeNames", "parentAffailiations"], "query": queryText}
    data = {"query": {"query_string":query_string},"size" : "5"}
    # print(json.dumps(data))
    # -------- send url request to search for the ouId --------
    if ('xxx' not in ouID_MPI) and internalFlag:
        return ouID_MPI
    else:
        url = 'https://dev.inge.mpdl.mpg.de/rest/ous/search' 
        response = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
        if response.ok:
            jData = (response.json())
            if 'records' in jData.keys():
                ouId = jData['records'][0]['data']['objectId']
                # print(jData['records'][0]['data']['name'])
            elif internalFlag:
                ouId = 'ou_persistent13'
            else:
                # print("external affa")
                ouId = 'ou_persistent22'
            # print(ouId)
            return ouId
        else:
        # If response code is not ok (200), print the bad request
            # print(json.dumps(data))
            response.raise_for_status()

def upfileRequest(Token, filePath, filename):
    # Token: Authorization Token got in the login process
    # filename: the name without extension of the file wanted to upload
    url = 'https://dev.inge.mpdl.mpg.de/rest/staging/' + filename 
    headers = {'Authorization' : Token}
    try: 
        files = {'file': open(filePath, 'rb')}
    except FileNotFoundError: # deal with the case that the corresponding pdf does not exist
        return "No PDF"
    res = requests.post(url, files = files, headers = headers) 
    if res.ok:
        return res.text
    else:
        res.raise_for_status()

def itemsRequest(Token, jsonfile):
    url = 'https://dev.inge.mpdl.mpg.de/rest/items' 
    headers = {'Authorization' : Token, 'Content-Type' : 'application/json'}
    res = requests.post(url, data = jsonfile, headers = headers)
    if not res.ok:
        res.raise_for_status()