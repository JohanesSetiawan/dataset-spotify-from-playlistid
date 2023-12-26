import base64
import requests
import json
import csv

playlistID = ""

datasetOne = []
datasetTwo = []
datasetThree = []


def getTokenSpotify():
    auth_string = clientID + ":" + clientSecret

    # Encode to base64
    encoded = base64.b64encode(auth_string.encode('utf-8'))

    # url to get token
    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + encoded.decode('utf-8'),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # data to take token from guideline spotify
    dataGetToken = {'grant_type': 'client_credentials'}

    # request POST to Spotify
    reqResult = requests.post(url, headers=headers, data=dataGetToken)

    # parse to json
    jsonResult = json.loads(reqResult.content)
    token = jsonResult['access_token']

    return token


def getAuthHeader(token):
    headers = {
        "Authorization": "Bearer " + token
    }
    return headers


def getUserProfileSpotify(token):
    endpointURL = "https://api.spotify.com/v1/me"
    headers = getAuthHeader(token)
    results = requests.get(endpointURL, headers=headers)
    jsonResult = json.loads(results.content)
    print(jsonResult)


def getAudioFeatureExtraction(token, trackID):  # get audio feature extraction
    endpointURL = "https://api.spotify.com/v1/audio-features/" + trackID
    headers = getAuthHeader(token)
    results = requests.get(endpointURL, headers=headers)
    jsonResult = json.loads(results.content)

    dataAudioFeatures = [
        jsonResult['acousticness'],
        jsonResult['danceability'],
        jsonResult['duration_ms'],
        jsonResult['energy'],
        jsonResult['instrumentalness'],
        jsonResult['key'],
        jsonResult['liveness'],
        jsonResult['loudness'],
        jsonResult['mode'],
        jsonResult['speechiness'],
        jsonResult['tempo'],
        jsonResult['time_signature'],
        jsonResult['valence'],
    ]

    createDataset = datasetTwo.append(dataAudioFeatures)


def getPlaylistName(token, playlistID):
    endpointURL = "https://api.spotify.com/v1/playlists/" + playlistID
    market = '?market=ID'
    fields = '&fields=name'
    url = endpointURL + '?' + market + fields
    headers = getAuthHeader(token)
    results = requests.get(url, headers=headers)
    jsonResult = json.loads(results.content)

    playlistName = jsonResult['name']
    print("\n\nPlaylist Name: " + playlistName)

    return playlistName, playlistID


def getPlaylistItems(token, playlistID):
    endpointURL = "https://api.spotify.com/v1/playlists/" + playlistID + "/tracks"
    limit = '&limit=1'
    market = '?market=ID'
    fields = '&fields=items(track(id,name,artists,popularity,duration_ms,album(name,release_date)))'
    url = endpointURL + '?' + market + fields + limit
    headers = getAuthHeader(token)
    results = requests.get(url, headers=headers)
    jsonResult = json.loads(results.content)

    print(json.dumps(jsonResult, indent=4, sort_keys=True))  # without \n

    print("\n\ncreate dataset, please wait...")

    for i in range(len(jsonResult['items'])):
        playlistItemsDataset = []
        playlistItemsDataset.append(jsonResult['items'][i]['track']['id'])
        playlistItemsDataset.append(
            jsonResult['items'][i]['track']['name'].encode('utf-8'))
        playlistItemsDataset.append(
            jsonResult['items'][i]['track']['artists'][0]['name'].encode('utf-8'))
        playlistItemsDataset.append(
            jsonResult['items'][i]['track']['popularity'])
        playlistItemsDataset.append(
            jsonResult['items'][i]['track']['duration_ms'])
        playlistItemsDataset.append(
            int(jsonResult['items'][i]['track']['album']['release_date'][:4]))
        datasetOne.append(playlistItemsDataset)

    for i in range(len(datasetOne)):
        getAudioFeatureExtraction(token, datasetOne[i][0])

    for i in range(len(datasetOne)):
        datasetThree.append(datasetOne[i] + datasetTwo[i])

    # convert to csv
    with open('datasetSpotify.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "artists", "popularity", "duration_ms", "release_date", "acousticness",
                         "danceability", "duration_ms", "energy", "instrumentalness", "key", "liveness", "loudness",
                         "mode", "speechiness", "tempo", "time_signature", "valence"])
        writer.writerows(datasetThree)

    # create a loading with message "dataset created"
    print("\ndataset created")


# ...
clientID = input("Input clientID Spotify Developer: ")
clientSecret = input("Input clientSecret Spotify Developer: ")
getTokenSpotify()
playlistID = input("\nEnter Playlist ID: ")
getAuthHeader(getTokenSpotify())
getPlaylistName(getTokenSpotify(), playlistID)
getPlaylistItems(getTokenSpotify(), playlistID)
