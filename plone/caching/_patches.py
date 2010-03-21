# XXX: Remove this - we want to push this down into Zope

# For ZPublisher.interfaces

from zope.interface import Interface, Attribute

class IPubBeforeStreaming(Interface):
    """Event fired just before a streaming response is initiated, i.e. when
    something calls response.write() for the first time. Note that this is
    carries a reference to the *response*, not the request.
    """
    
    response = Attribute(u"The current HTTP response")

import ZPublisher.interfaces
setattr(ZPublisher.interfaces, 'IPubBeforeStreaming', IPubBeforeStreaming)

# For ZPublisher.pubevents

from zope.interface import implements

class PubBeforeStreaming(object):
    """Notified immediately before streaming via response.write() commences
    """
    implements(IPubBeforeStreaming)
    
    def __init__(self, response):
        self.response = response

import ZPublisher.pubevents
setattr(ZPublisher.pubevents, 'PubBeforeStreaming', PubBeforeStreaming)

# Patch for ZPublisher.HTTPResponse

from zope.event import notify

def ZPublisher_HTTPResponse_write(self, data):
    if not self._wrote:
        
        notify(PubBeforeStreaming(self))
        
        self.outputBody()
        self._wrote = 1
        self.stdout.flush()

    self.stdout.write(data)

# Patch for ZServer.HTTPResponse

# from zope.event import notify
import tempfile
import thread
from ZServer.Producers import file_part_producer

def ZServer_ZServerHTTPResponse_write(self,data):
    if type(data) != type(''):
        raise TypeError('Value must be a string')

    stdout=self.stdout

    if not self._wrote:
        
        notify(PubBeforeStreaming(self))
        
        l=self.headers.get('content-length', None)
        if l is not None:
            try:
                if type(l) is type(''): l=int(l)
                if l > 128000:
                    self._tempfile=tempfile.TemporaryFile()
                    self._templock=thread.allocate_lock()
            except: pass

        self._streaming=1
        stdout.write(str(self))
        self._wrote=1

    if not data: return

    if self._chunking:
        data = '%x\r\n%s\r\n' % (len(data),data)

    l=len(data)

    t=self._tempfile
    if t is None or l<200:
        stdout.write(data)
    else:
        b=self._tempstart
        e=b+l
        self._templock.acquire()
        try:
            t.seek(b)
            t.write(data)
        finally:
            self._templock.release()
        self._tempstart=e
        stdout.write(file_part_producer(t,self._templock,b,e), l)
