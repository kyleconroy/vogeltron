"""
Author: RogueDarkJedi and Derferman
Desc: Updates a sidebar for a subreddit with the
newest Baseball data!
Usage: In the sidebar description, add the tags [](/statsstart) and 
[](/statsend) where you want the table to go.
"""
import os
import logging

SUBREDDIT = os.environ.get("SUBREDDIT", "SFGiants")
LEAGUE = os.environ.get("MLB_LEAGUE", "NL")
DIVISION = os.environ.get("MLB_DIVISION", "WEST")
USERNAME = os.environ.get("REDDIT_USERNAME", "")
PASSOWRD = os.environ.get("REDDIT_PASSWORD", "")

class RedditSidebar():
  def __init__(self, login, password, subName):
    # Don't really need to, but I'm going to save these anyways
    self._loginName=login
    self._loginPass=password

    # Save the subreddit name and the user's modhash
    self._subredditName=subName
    self._userHash=""

    print("Initializing Network Settings")
    # Setting up the network to make requests to Reddit
    self.cookieJar = http.cookiejar.CookieJar()
    authKeeper = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookieJar))
    authKeeper.addheaders = [('User-agent', 'Reddit Dynamic Sidebar Bot by /u/RogueDarkJedi')]
    urllib.request.install_opener(authKeeper)

    # Default subreddit settings
    self._ds={}
    self.description=""
    self._ds.setdefault("name", self._subredditName)

    # Login time go!
    print("Logging in....")
    loginParams = {"user": self._loginName, "passwd": self._loginPass}

    response = self.makeRequest("http://www.reddit.com/api/login/%s" % self._loginName, loginParams)
    jsonResponse = json.loads(response.decode('utf-8'), None)["json"]
    # Save the modhash
    self._userHash = jsonResponse["data"]["modhash"]
    print("Logged in!")

  def makeRequest(self, url, params=None, useJSON=True, overrideAll=False):
    if overrideAll:
      request = urllib.request.urlopen(url)
      return request.read()

    if params == None:
      params = {}

    # Some may not require the api type to be set
    if useJSON:
      params.setdefault("api_type", "json")

    # Always send the modhash unless we are logging in  
    if self._userHash != "":
      params.setdefault("uh", self._userHash)

    # Encode the parameters!
    if params: 
      params = urllib.parse.urlencode(params).encode('utf-8')

    # This script has no real error handling.
    request = urllib.request.urlopen(url, params)
    return request.read()

  def pullSubredditData(self):
    print("Pulling config from sidebar")
    response = self.makeRequest("http://www.reddit.com/r/%s/about/edit/.json" % self._subredditName, None, True, True)
    print("Got Subreddit Data!")
    jsonData = json.loads(response.decode('utf-8'), None)
    data = jsonData["data"]

    # Why did I do this by hand, that was dumb.
    self._ds.setdefault("title", data["title"])
    self._ds.setdefault("header-title", data["header_hover_text"])
    if data["domain"]:
      self._ds.setdefault("domain", data["domain"])
    self._ds.setdefault("sr", data["subreddit_id"])
    self._ds.setdefault("lang", data["language"])
    self._ds.setdefault("over_18", data["over_18"])
    self._ds.setdefault("allow_top", data["default_set"])
    self._ds.setdefault("show_media", data["show_media"])
    self._ds.setdefault("type", data["subreddit_type"])
    self._ds.setdefault("link_type", data["content_options"])
    self._ds.setdefault("css_on_cname", data["domain_css"])
    self._ds.setdefault("sponsorship-text", "")
    self._ds.setdefault("sponsorship-name", "")
    self._ds.setdefault("sponsorship-url", "")
    # And now the most important part
    self.description = data["description"]
    print("Config created!")

  # This takes a string of sports data and then puts it into the description
  # It does not send it out.
  def injectSportsData(self, data):
    print("Injecting Sports Data")
    # Okay, so we have the description, we now just need to modify it to insert the table
    tempDesc = self.description
    splitter = tempDesc.split("[](/statsstart")
    stringBefore = splitter[0]
    stringAfter = splitter[1].rsplit("[](/statsend")[1]
    self.description = stringBefore + "[](/statsstart)\n\n\n" + data + "\n[](/statsend" + stringAfter 
    print("Injection Complete.")
    return

  def updateSidebar(self):
    print("Update Cycle Started")
    self.pullSubredditData()
    self.injectSportsData(sportsData)
    print("Pushing out new description...")
    # Update the description
    self._ds.setdefault("description", self.description)
    self.makeRequest("http://www.reddit.com/api/site_admin", self._ds, False)
    print("Description pushed!")

def parseSportsInfo(responseData):
    global sportsData

    if len(responseData) <= 1:
      print("ERROR! DATA WAS INVALID, ZOMG!")
      return

    # If the following comments are cursey, it's because lxml 
    # didn't want to build on my machine and I wasted like 2
    # hours trying to fix it. Then I gave up and used BeautifulSoup,
    # which is a billion times better damnit.

    colString=""

    soup = BeautifulSoup(responseData)
    # Get the goddamn table
    tableInfo = soup.find_all(id=regionStandingsId)[0]
    # Now we have the dedicated table, find how many columns there are
    colNum = str(tableInfo.find("col").contents[0]).count("<col>")
    # For the number of colNumbers, format the sidebar tag
    for i in range(colNum):
      colString += "---"
      if i != colNum:
        colString += "|"

    colString += "---\n"
    # Next, do the header rows
    headers = tableInfo.find_all("th")
    # Grab the heaers for the tables, this would be looped, but they insert arbitrary tags in places
    headerData = str(headers[0].contents[0]) + "|Abbr|" + str(headers[2].contents[0]) + "|" + str(headers[3].contents[0]) + "|" + str(headers[4].nobr.contents[0]) + "|" + str(headers[5].contents[0]) + "\n"

    # Append it to the sports data
    sportsData += headerData + colString

    # Next it's time to do the body
    teamsInfo = tableInfo.find("tbody").find_all("tr")
    # Loop through each team info thingy
    for teamInfo in teamsInfo:
      teamData = teamInfo.find_all("td")
      # Get all the info for a team
      teamName = str(teamData[0].a.contents[0])
      teamAbbr = str(teamData[1].contents[0])
      teamWins = str(teamData[2].contents[0])
      teamLosses = str(teamData[3].contents[0])
      teamWinLoss = str(teamData[4].contents[0])
      teamidk = str(teamData[5].contents[0])
      # Format the string
      teamLine = ("{0}|{1}|{2}|{3}|{4}|{5}\n").format(teamName, teamAbbr, teamWins, teamLosses, teamWinLoss, teamidk)
      sportsData += teamLine

    print(sportsData)

def pullSportsInfo():
    # Jump into the baseball data website
    print("Opening network for baseball stats")
    rObj = urllib.request.build_opener()
    rObj.addheaders = [('User-agent', fakeUserAgent)]
    print("Making Request")
    response = rObj.open(dataURL)

    # Okay, we should have the data now.
    responseData = response.read()
    parseSportsInfo(responseData)

def __init__():
  print("Bot started")
  # Grab that silly sports information
  pullSportsInfo()

  # Initiate a reddit session
  r = RedditSidebar(login, password, subredditName)

  # Update the sidebar!
  r.updateSidebar()

  # done.
  print("Done.")

__init__()
