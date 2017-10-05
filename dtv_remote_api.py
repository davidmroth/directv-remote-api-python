import re
import json
import urllib

'''
More details:
    http://www.sbcatest.com/DTV-MD-0058-DIRECTVSet-topInformationforInstallers-V2.2.pdf
'''

'''
# Valid commands
'FA81', // Standby
'FA82', // Active
'FA83', // GetPrimaryStatus
'FA84', // GetCommandVersion
'FA87', // GetCurrentChannel
'FA90', // GetSignalQuality
'FA91', // GetCurrentTime
'FA92', // GetUserCommand
'FA93', // EnableUserEntry
'FA94', // DisableUserEntry
'FA95', // GetReturnValue
'FA96', // Reboot
'FAA5', // SendUserCommand
'FAA6', // OpenUserChannel
'FA9A', // GetTuner
'FA8A', // GetPrimaryStatusMT
'FA8B', // GetCurrentChannelMT
'FA9D', // GetSignalQualityMT
'FA9F', // OpenUserChannelMT

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
'''


class DTV_Remote:
    def __init__(self, ipAddress):
        self.ipAddress = ipAddress
        valid = self.__validate()

        if not valid[0]:
            raise Exception(valid[1])

    def __defaultCallback(self, result):
        #print result
        #print
        return result

    def __validate(self, options = {}):
        '''
        Validate the `ipAddress` configured with this DirecTV.Remote
        instance.  This is done first by using a regular expression to
        validate that the `ipAddress` is a valid IPv4 IP address.  If that
        succeeds, we will then try to contact the DirecTV set-top-box.
        '''
        path = '/info/getOptions'
        options = options if bool(options) else {}

        # Validate IP Address
        if not re.match("^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$", self.ipAddress):
            self.__defaultCallback({
                'status' : {
                    'code'          : 405,
                    'commandResult' : 1,
                    'msg'           : 'Not a valid IP address',
                    'query'         : path
                }
            })

            return (False, "Not a valid IP address.")

        def callback(data = False):
            if data and 'options' in data:
                # We got a valid response.
                return (True, 'Host not appears to be a DirecTV set-top-box')

            else:
                return (False, 'Host does not appear to be a DirecTV set-top-box')

        #Fire the callback with our customized response
        options['callback'] = callback

        #TODO: Build dynamic functions base on reply from '/info/getOptions'
        return self.makeRequest({
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
        try:
            return requestOptions['options']['callback'](urllib.urlopen(requestUrl + requestQuery).read())
        except:
            return (False, 'Host error!')

    def getTuned(self, options = {}):
        '''
        Retrieves the current program information for the currently tuned
        channel.
        '''
        return self.makeRequest({
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

        return self.makeRequest({
            'path':       '/tv/tune',
            'options':    options
        })

    def getLocations(self, options = {}):
        '''
        Retrieve the list of DirecTV set-top-box locations the set-top-box
        is aware of.
        '''
        return self.makeRequest({
            'path'    : '/info/getLocations',
            'options' : options
        })

    def getVersion(self, options = {}):
        '''
        Retrieve the current software version information for the DirecTV
        set-top-box.
        '''
        return self.makeRequest({
            'path'    : '/info/getVersion',
            'options' : options,
        })

    def getMode(self, options = {}):
        '''
        Retrieve the operating mode the DirecTV set-top-box is currently
        operating in.
        '''
        return self.makeRequest({
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
        documentation. * See valid keys above *
        '''
        if options and not options['key']:
            raise Exception('options. key is not optional.')

        return self.makeRequest({
            'path'    : '/remote/processKey',
            'options' : options
        })

    def processCommand(self, options = {}):
        '''
        Sends a serial command request to the DirecTV set-top-box.  The
        `cmd` option is required and must be valid.  For available commands
        see the [available commands](#commands) portion of the documentaiton.
        * See valid commands above *
        '''
        if options and not options['cmd']:
            raise Exception('options.cmd is not optional.')

        return self.makeRequest({
            'path'    : '/serial/processCommand',
            'options' : options
        })

    def getOptions(self, options = {}):
        ''' Retrieve the list of available APIs the DirecTV set-top-box supports. '''
        return self.makeRequest({
            'path'    : '/info/getOptions',
            'options' : options
        })

    def getProgInfo(self, options = {}):
        '''
        Retrieve the current program information for the channel given.  The
        `major` option is required and corresponds to the channel you want to
        get programming information for.
        '''
        if options and not options['major']:
            raise Exception('options.major is not optional.')

        return self.makeRequest({
            'path'    : '/tv/getProgInfo',
            'options' : options
        })


# Example
# remote = DTV_Remote("192.168.86.51")

'''
print remote.getOptions()
print remote.getProgInfo({'major': '202'})
print remote.processKey({'key':'power'})
print remote.getTuned()
print remote.tune()
'''
