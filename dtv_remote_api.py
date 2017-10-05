import re
import json
import urllib

'''
More details:
    http://www.sbcatest.com/DTV-MD-0058-DIRECTVSet-topInformationforInstallers-V2.2.pdf
'''

# Valid keys
'power'
'poweron'
'poweroff'
'format'
'pause'
'rew'
'replay'
'stop'
'advance'
'ffwd'
'record'
'play'
'guide'
'active'
'list'
'exit'
'back'
'menu'
'info'
'up'
'down'
'left'
'right'
'select'
'red'
'green'
'yellow'
'blue'
'chanup'
'chandown'
'prev'
'0'
'1'
'2'
'3'
'4'
'5'
'6'
'7'
'8'
'9'
'dash'
'enter'

class DTV_Remote:
    def __init__(self, ipAddress):
        self.ipAddress = ipAddress
        self.__validate()

    def __defaultCallback(self, result):
        print result
        print

    def __validate(self, options = {}):
        '''
        Validate the `ipAddress` configured with this DirecTV.Remote
        instance.  This is done first by using a regular expression to
        validate that the `ipAddress` is a valid IPv4 IP address.  If that
        succeeds, we will then try to contact the DirecTV set-top-box.
        '''
        path = '/info/getOptions'
        oldCallback = None
        options = options if bool(options) else {}

        if not 'callback' in options or not callable(options['callback']):
            options['callback'] = self.__defaultCallback

        if not re.match("^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$", self.ipAddress):
            options['callback']({
                'status' : {
                    'code'          : 405,
                    'commandResult' : 1,
                    'msg'           : 'Not a valid IP address',
                    'query'         : path
                }
            })

        # We have to validate the `callback` option here since we have to
        # do some callback juggling so we can deliver customized messages
        # based on the result of the request.
        if not options['callback'] or not callable(options['callback']):
            raise Exception("options['callback'] is not optional and must be a function.")

        # The callback passed in so we can invoke it later with our
        # customized response object.
        oldCallback = options['callback']

        def callback(data):
            if data['options']:
                # We got a valid response.
                response = {
                    'status' : {
                        'code'          : 200,
                        'commandResult' : 0,
                        'msg'           : 'Host is a DirecTV set-top-box',
                        'query'         : path
                    }
                }

            else:
                # We got a valid response but it did not have the expected
                # payload.
                response = {
                    'status' : {
                        'code'          : 404,
                        'commandResult' : 1,
                        'msg'           : 'Host does not appear to be a DirecTV set-top-box',
                        'query'         : path
                    }
                }

            #Fire the callback with our customized response
            options['callback'] = callback
            oldCallback(response);

        self.makeRequest({
            'path'    : path,
            'options' : options
        })

    def makeRequest(self, requestOptions = {}):
        ''' The methods in this section are helper methods. '''
        requestOptions = requestOptions if requestOptions else {}
        requestOptions['options'] = requestOptions['options'] if 'options' in requestOptions else {}

        requestUrl = 'http://' + self.ipAddress + ':8080'
        requestQuery = requestOptions['path']

        knownRequestParams = [
            'clientAddr',
            'cmd',
            'hold',
            'key',
            'major',
            'minor',
            'time',
            'videoWindow',
            'wrapper'
        ]

        # This should never happen but just in case someone uses makeRequest directly in an invalid way...
        if not 'callback' in requestOptions['options'] or not callable(requestOptions['options']['callback']):
            requestOptions['options']['callback'] = self.__defaultCallback

        # This should never happen but just in case someone uses makeRequest directly in an invalid way...
        if not requestOptions['path']:
            raise Exception("requestOptions.path is not optional.")

        # Create query params based on known request options
        for key in requestOptions['options']:
            if key in knownRequestParams > 0:
                requestQuery += '?'

        for i in range(len(knownRequestParams)):
            requestParam = knownRequestParams[i]

            if requestParam in requestOptions['options']:
                if requestQuery[len(requestQuery) - 1] != '?':
                    requestQuery += '&'

                requestQuery += requestParam + '=' + requestOptions['options'][requestParam]
                #print requestQuery

        #Make the call, fire the callback with the results.
        requestOptions['options']['callback'](urllib.urlopen(requestUrl + requestQuery).read());

    def getTuned(self, options = {}):
        '''
        Retrieves the current program information for the currently tuned
        channel.
        '''
        self.makeRequest({
            'path'    : '/tv/getTuned',
            'options' : options
        })

    def tune(self, options = {}):
        '''
        Send a request to tune the DirecTV set-top-box to the channel
        specified.  The `major` option is required and corresponds to the
        channel you wish to tune to.
        '''
        if options and not options['major']:
            raise Exception('options.major is not optional.')

        self.makeRequest({
            'path':       '/tv/tune',
            'options':    options
        })

    def getLocations(self, options = {}):
        '''
        Retrieve the list of DirecTV set-top-box locations the set-top-box
        is aware of.
        '''
        self.makeRequest({
            'path'    : '/info/getLocations',
            'options' : options
        })

    def getVersion(self, options = {}):
        '''
        Retrieve the current software version information for the DirecTV
        set-top-box.
        '''
        self.makeRequest({
            'path'    : '/info/getVersion',
            'options' : options,
        })

    def getMode(self, options = {}):
        '''
        Retrieve the operating mode the DirecTV set-top-box is currently
        operating in.
        '''
        self.makeRequest({
            'path'    : '/info/mode',
            'options' : options
        })

    def processKey(self, options = {}):
        '''
        Send a remote key press request to the DirecTV set-top-box.  The
        `key` option is required and must be valid.  For available keys see
        the [available keys](#keys) portion of the documentaiton.  You can
        also pass in a `hold` option but it is not required.  For available
        holds, see the [available holds](#holds) portion of the
        documentation.
        '''
        if options and not options['key']:
            raise Exception('options.key is not optional.')

        self.makeRequest({
            'path'    : '/remote/processKey',
            'options' : options
        })

    def processCommand(self, options = {}):
        '''
        Sends a serial command request to the DirecTV set-top-box.  The
        `cmd` option is required and must be valid.  For available commands
        see the [available commands](#commands) portion of the documentaiton.
        '''
        if options and not options['cmd']:
            raise Exception('options.cmd is not optional.')

        self.makeRequest({
            'path'    : '/serial/processCommand',
            'options' : options
        })

    def getOptions(self, options = {}):
        ''' Retrieve the list of available APIs the DirecTV set-top-box supports. '''
        self.makeRequest({
            path    : '/info/getOptions',
            options : options
        })

    def getProgInfo(self, options = {}):
        '''
        Retrieve the current program information for the channel given.  The
        `major` option is required and corresponds to the channel you want to
        get programming information for.
        '''
        if options and not options['major']:
            raise Exception('options.major is not optional.')

        self.makeRequest({
            'path'    : '/tv/getProgInfo',
            'options' : options
        })


''' How to use: '''
#remote = DTV_Remote("192.168.xx.xx")
#remote.getProgInfo({'major': '202'})
#remote.processKey({'key':'power'})
#remote.getTuned()
#remote.tune()
