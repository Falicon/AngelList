#######################################################################################
# Python implementation of AngelList OAuth Authorization and API.                     #
#                                                                                     #
# Author: Kevin Marshall                                                              #
# Email : info@falicon.com                                                            #
# Web: http://www.falicon.com                                                         #
#                                                                                     #
#######################################################################################

import hashlib
import urllib, urllib2
import simplejson as json

"""
Provides a Pure Python AngelList API Interface.
"""

class AngelListError(Exception):
  """
  generic exception class; may be thrown by various errors in the OAuth flow
  """
  def __init__(self, value):
    self.parameter = value

  def __str__(self):
    return repr(self.parameter)

class AngelList(object):
    def __init__(self):
        """
        AngelList Base class that simply implements AngelList OAuth Authorization and
        AngelList APIs such as Activity Feeds, Follows, Reviews, Startups,
        Startup Roles, Status Updates, Tags, and Users.

        Please create an application from the link below if you do not have an API key
        and secret key yet.
        - http://angel.co/api/oauth/clients
        """
        # Credientials
        self.URI_SCHEME        = "https"
        self.API_ENDPOINT      = "%s://api.angel.co" % self.URI_SCHEME
        self.OAUTH_ENDPOINT    = "%s://angel.co/api" % self.URI_SCHEME
        self.ACCESS_TOKEN_URL  = "/oauth/token"
        self.AUTHORIZATION_URL = "/oauth/authorize"
        self.client_id         = None
        self.client_secret     = None
        self.access_token      = None

    #############################
    # OAUTH SPECIFIC SECTION
    #############################

    def getAuthorizeURL(self, client_id = None, ):
        self.client_id = client_id and client_id or self.client_id
        if self.client_id is None:
            raise AngelListError("client_id is NULL. Plase set this or pass it as a parameter first.")
        return "%s%s?client_id=%s&response_type=code" % (self.OAUTH_ENDPOINT, self.AUTHORIZATION_URL, self.client_id)

    def getAccessToken(self, client_id = None, client_secret = None, code = None):
      self.client_id = client_id and client_id or self.client_id
      if self.client_id is None:
        raise AngelListError("client_id is NULL. Plase set this or pass it as a parameter first.")

      self.client_secret = client_secret and client_secret or self.client_secret
      if self.client_secret is None:
        raise AngelListError("client_secret is NULL. Plase set this or pass it as a parameter first.")

      if code is None:
        raise AngelListError("code is NULL. Plase pass the REQUEST['code'] angel.co/api/oauth/authorize responeded with as a parameter.")

      url = "%s%s?client_id=%s&client_secret=%s&code=%s&grant_type=authorization_code" % (self.OAUTH_ENDPOINT, self.ACCESS_TOKEN_URL, self.client_id, self.client_secret, code)

      try:
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        params = urllib.urlencode({})
        response = urllib2.urlopen(urllib2.Request(url, params, headers))
        json_data = json.loads(response.read())
        access_token = json_data['access_token']
      except:
        # access token failed to fetch (for any reason); so we'll just return blank
        access_token = ''

      self.access_token = access_token

      return access_token

    #############################
    # GENERAL HELPER FUNCTIONS
    #############################

    def do_get_request(self, url):
      """
      perform a GET request to the supplied url
      """
      response = urllib2.urlopen(url)
      return json.loads(response.read())

    def do_post_request(self, url, data = None):
      """
      perform a POST request to the supplied url with the given fieldvalues
      """
      headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
      params = urllib.urlencode(data)
      response = urllib2.urlopen(urllib2.Request(url, params, headers))
      return json.loads(response.read())

    def do_delete_request(self, url, data = None):
      """
      perform a DELETE request to the supplied url
      """
      opener = urllib2.build_opener(urllib2.HTTPHandler)
      params = urllib.urlencode(data)
      request = urllib2.Request(url, params)
      request.add_header('Content-Type', 'text/plain')
      request.get_method = lambda: 'DELETE'
      response = opener.open(request)
      return json.loads(response.read())

    def check_access_token(self, access_token = None):
      self.access_token = access_token and access_token or self.access_token
      if self.access_token is None:
        raise AngelListError("access_token is Null. Please set it first")
      return

    #############################
    # ANGEL.CO API FUNCTIONS
    #############################

    ##########################################################
    # Activity Feeds (http://angel.co/api/spec/activity_feeds)
    # (GET)    https://api.angel.co/1/feed
    def getFeed(self, access_token = None):
      self.check_access_token(access_token)
      return self.do_get_request('%s/1/feed?access_token=%s' % (self.API_ENDPOINT, self.access_token))

    ##########################################################
    # Follows (http://angel.co/api/spec/follows)
    ### NOT WORKING YET [[DELETE ISSUE]]
    # (DELETE) https://api.angel.co/1/follows [type, id]
    def deleteFollows(self, access_token = None, follow_type = None, follow_id = None):
      """
      follow_type - REQUIRED - 'user' or 'startup'
      id - REQUIRED - the id of the user or startup to stop following
      """
      self.check_access_token(access_token)

      if follow_type is None:
        raise AngelListError("the follow_type param is required for this api call.")

      if follow_id is None:
        raise AngelListError("the follow_id param is required for this api call.")

      data = {'type':follow_type, 'id':follow_id}
      url = "%s/1/follows?access_token=%s" % (self.API_ENDPOINT, self.access_token)
      return self.do_delete_request(url, data)

    # (POST)   https://api.angel.co/1/follows [type, id]
    def addFollows(self, access_token = None, follow_type = None, follow_id = None):
      """
      follow_type - REQUIRED - 'user' or 'startup'
      id - REQUIRED - the id of the user or startup to stop following
      """
      self.check_access_token(access_token)

      if follow_type is None:
        raise AngelListError("the follow_type param is required for this api call.")

      if follow_id is None:
        raise AngelListError("the follow_id param is required for this api call.")

      data = {'type':follow_type, 'id':follow_id}
      url = "%s/1/follows?access_token=%s" % (self.API_ENDPOINT, self.access_token)

      return self.do_post_request(url, data)

    # (GET)    https://api.angel.co/1/users/:id/followers
    def getFollowers(self, access_token = None, user_id = None):
      self.check_access_token(access_token)
      if user_id is None:
        raise AngelListError("the user_id param is required for this api call.")
      return self.do_get_request('%s/1/users/%s/followers?access_token=%s' % (self.API_ENDPOINT, user_id, self.access_token))

    # (GET)    https://api.angel.co/1/users/:id/followers/ids
    def getFollowersIds(self, access_token = None, user_id = None):
      self.check_access_token(access_token)
      if user_id is None:
        raise AngelListError("the user_id param is required for this api call.")
      return self.do_get_request('%s/1/users/%s/followers/ids?access_token=%s' % (self.API_ENDPOINT, user_id, self.access_token))

    # (GET)    https://api.angel.co/1/users/:id/following
    def getFollowing(self, access_token = None, user_id = None):
      self.check_access_token(access_token)
      if user_id is None:
        raise AngelListError("the user_id param is required for this api call.")
      return self.do_get_request('%s/1/users/%s/following?access_token=%s' % (self.API_ENDPOINT, user_id, self.access_token))

    # (GET)    https://api.angel.co/1/users/:id/following/ids
    def getFollowingIds(self, access_token = None, user_id = None):
      self.check_access_token(access_token)
      if user_id is None:
        raise AngelListError("the user_id param is required for this api call.")
      return self.do_get_request('%s/1/users/%s/following/ids?access_token=%s' % (self.API_ENDPOINT, user_id, self.access_token))

    # (GET)    https://api.angel.co/1/startups/:id/followers
    def getStartupsFollowers(self, access_token = None, startup_id = None):
      self.check_access_token(access_token)
      if startup_id is None:
        raise AngelListError("the startup_id param is required for this api call.")
      return self.do_get_request('%s/1/startups/%s/followers?access_token=%s' % (self.API_ENDPOINT, startup_id, self.access_token))

    # (GET)    https://api.angel.co/1/startups/:id/followers/ids
    def getStartupsFollowersIds(self, access_token = None, startup_id = None):
      self.check_access_token(access_token)
      if startup_id is None:
        raise AngelListError("the startup_id param is required for this api call.")
      return self.do_get_request('%s/1/startups/%s/followers/ids?access_token=%s' % (self.API_ENDPOINT, startup_id, self.access_token))

    ##########################################################
    # Reviews (http://angel.co/api/spec/reviews)
    # (GET)    https://api.angel.co/1/reviews
    def getReviews(self, access_token = None, user_id = None):
      """
      user_id - OPTIONAL - id of the user you want reviews on (defaults to auth'ed user)
      """
      self.check_access_token(access_token)
      return self.do_get_request('%s/1/reviews?access_token=%s&user_id=%s' % (self.API_ENDPOINT, self.access_token, user_id))

    ##########################################################
    # Startups (http://angel.co/api/spec/startups)
    # (GET)    https://api.angel.co/1/startups/:id
    def getStartups(self, access_token = None, startup_id = None):
      self.check_access_token(access_token)
      if startup_id is None:
        raise AngelListError("the startup_id param is required for this api call.")
      return self.do_get_request('%s/1/startups/%s?access_token=%s' % (self.API_ENDPOINT, startup_id, self.access_token))

    # (GET)    https://api.angel.co/1/startups/search
    def getStartupsSearch(self, access_token = None, slug = None, domain = None):
      """
      slug - OPTIONAL - the slug for the startup you are searching for
      domain - OPTIONAL - the domain of the startup you are searching for
      """
      self.check_access_token(access_token)
      url = '%s/1/startups/search?access_token=%s' % (self.API_ENDPOINT, self.access_token)
      if slug:
        url = '%s&slug=%s' % (url, slug)
      if domain:
        url = '%s&domain=%s' % (url, domain)
      return self.do_get_request(url)

    # (GET)    https://api.angel.co/1/tags/:id/startups
    def getTagsStartups(self, access_token = None, tag_id = None):
      self.check_access_token(access_token)
      if tag_id is None:
        raise AngelListError("the tag_id param is required for this api call.")
      return self.do_get_request('%s/1/tags/%s/startups?access_token=%s' % (self.API_ENDPOINT, tag_id, self.access_token))

    ##########################################################
    # Startup Roles (http://angel.co/api/spec/startup_roles)
    # (GET)    https://api.angel.co/1/startup_roles
    def getStartupRoles(self, access_token = None, user_id = None, startup_id = None):
      """
      user_id - OPTIONAL - the user who's startup relationships you want to view
      startup_id - OPTIONAL - the startup who's user relationships you want to view
      """
      self.check_access_token(access_token)
      url = '%s/1/startups_roles?access_token=%s' % (self.API_ENDPOINT, self.access_token)
      if user_id:
        url = '%s&user_id=%s' % (url, user_id)
      if startup_id:
        url = '%s&startup_id=%s' % (url, startup_id)
      return self.do_get_request(url)

    ##########################################################
    # Status Updates (http://angel.co/api/spec/status_update)
    # (GET)    https://api.angel.co/1/status_updates
    def getStatusUpdates(self, access_token = None, user_id = None, startup_id = None):
      """
      user_id - OPTIONAL
      startup_id - OPTIONAL
      """
      self.check_access_token(access_token)
      url = '%s/1/startups_updates?access_token=%s' % (self.API_ENDPOINT, self.access_token)
      if user_id:
        url = '%s&user_id=%s' % (url, user_id)
      if startup_id:
        url = '%s&startup_id=%s' % (url, startup_id)
      return self.do_get_request(url)

    # (POST)   https://api.angel.co/1/status_updates
    def postStatusUpdates(self, access_token = None, startup_id = None, message = None):
      """
      startup_id - OPTIONAL - id of the startup you want to updated.
      message - REQUIRED - the status message to post
      """
      self.check_access_token(access_token)
      if message is None:
        raise AngelListError("the message param is required for this api call.")
      data = {'message':message}
      if startup_id:
        data['startup_id'] = startup_id

      url = "%s/1/status_updates?access_token=%s" % (self.API_ENDPOINT, self.access_token)
      return self.do_post_request(url, data)

    # (DELETE) https://api.angel.co/1/status_updates/:id
    def deleteStatusUpdates(self, access_token = None, status_id = None):
      self.check_access_token(access_token)
      if status_id is None:
        raise AngelListError("the status_id param is required for this api call.")
      data = {'id':status_id}
      url = "%s/1/status_updates?access_token=%s" % (self.API_ENDPOINT, self.access_token)
      return self.do_delete_request(url, data)

    ##########################################################
    # Tags (http://angel.co/api/spec/tags)
    # (GET)    https://api.angel.co/1/tags/:id
    def getTags(self, access_token = None, tag_id = None):
      self.check_access_token(access_token)
      if tag_id is None:
        raise AngelListError("the tag_id param is required for this api call.")
      return self.do_get_request('%s/1/tags/%s?access_token=%s' % (self.API_ENDPOINT, tag_id, self.access_token))

    # (GET)    https://api.angel.co/1/tags/:id/children
    def getTagsChildren(self, access_token = None, tag_id = None):
      self.check_access_token(access_token)
      if tag_id is None:
        raise AngelListError("the tag_id param is required for this api call.")
      return self.do_get_request('%s/1/tags/%s/children?access_token=%s' % (self.API_ENDPOINT, tag_id, self.access_token))

    # (GET)    https://api.angel.co/1/tags/:id/parents
    def getTagsParents(self, access_token = None, tag_id = None):
      self.check_access_token(access_token)
      if tag_id is None:
        raise AngelListError("the tag_id param is required for this api call.")
      return self.do_get_request('%s/1/tags/%s/parents?access_token=%s' % (self.API_ENDPOINT, tag_id, self.access_token))

    # (GET)    https://api.angel.co/1/tags/:id/startups
    def getTagsStartups(self, access_token = None, tag_id = None):
      self.check_access_token(access_token)
      if tag_id is None:
        raise AngelListError("the tag_id param is required for this api call.")
      return self.do_get_request('%s/1/tags/%s/startups?access_token=%s' % (self.API_ENDPOINT, tag_id, self.access_token))

    ##########################################################
    # Users (http://angel.co/api/spec/users)
    # (GET)    https://api.angel.co/1/users/:id
    def getUsers(self, access_token = None, user_id = None):
      self.check_access_token(access_token)
      if user_id is None:
        raise AngelListError("the user_id param is required for this api call.")
      return self.do_get_request('%s/1/users/%s?access_token=%s' % (self.API_ENDPOINT, user_id, self.access_token))

    # (GET)    https://api.angel.co/1/users/search
    def getUsersSearch(self, access_token = None, slug = None, email = None):
      self.check_access_token(access_token)
      url = '%s/1/users/search?access_token=%s' % (self.API_ENDPOINT, self.access_token)
      if slug:
        url = '%s&slug=%s' % (url, slug)
      if email:
        md5_hash = hashlib.md5(email).hexdigest()
        url = '%s&md5=%s' % (url, md5_hash)
      try:
        results = self.do_get_request(url)
      except:
        # couldn't find any results so just return an empty object
        results = json.loads('{}')
      return results

    # (GET)    https://api.angel.co/1/me
    def getMe(self, access_token = None):
      self.check_access_token(access_token)
      return self.do_get_request('%s/1/me?access_token=%s' % (self.API_ENDPOINT, self.access_token))
