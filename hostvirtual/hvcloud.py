'''Python module for the HostVirtual Cloud API'''
import os
import time
import requests


class HVException(RuntimeError):
    '''HostVirtual Custom Exception'''
    pass


class HVCloud(object):
    '''Client for HostVirtual Cloud API'''

    HV_API_ENDPOINT = 'http://bapi.vr.org'

    def __init__(self, api_key=None):
        self._key = api_key
        if self._key is None:
            self._key = os.environ.get('HV_API_KEY', '')
        self._locations = None  # lazy evaluated, cached
        self._packages = None  # lazy evaluated, cached
        self._plans = None  # lazy evaluated, cached
        self._images = None  # lazy evaluated, cached

    @staticmethod
    def _request(op, url, in_query, params):
        kwargs = dict(url=url, timeout=5)
        kwargs['params' if in_query else 'json'] = params
        return requests.request(op, **kwargs)

    @staticmethod
    def _sanitize(params):
        for k in list(params):
            if params[k] is None:
                del params[k]

    def request(self, op, ep, in_query=False, **params):
        '''Issue an API request'''
        self._sanitize(params)
        url = "%s%s?key=%s" % (self.HV_API_ENDPOINT, ep, self._key)
        resp = self._request(op, url, in_query, params)
        if not resp.ok:
            try:
                err = resp.json()['error']['message']
            except:
                err = ''
            msg = 'Failed %s %s - (%s) %s' % (op, ep, resp.status_code, err)
            raise HVException(msg)
        return resp.json()

    def images(self):
        '''List deployable images'''
        # lazy evaluation; cached
        if not self._images:
            self._images = self.request('GET', '/cloud/images')
        return self._images

    def plans(self):
        '''List available billing plans'''
        # lazy evaluation; cached
        if not self._plans:
            self._plans = self.request('GET', '/cloud/sizes')
        return self._plans

    def packages(self):
        '''List all packages'''
        # lazy evaluation; cached
        if not self._packages:
            self._packages = self.request('GET', '/cloud/packages')
        return self._packages

    def available_packages(self):
        '''List unassigned packages'''
        def _is_available(pkg):
            return (pkg.get('package_status') == 'Active' and
                    pkg.get('package') is None and
                    pkg.get('state') is None)
        return [p for p in self.packages() if _is_available(p)]

    def package_buy(self, plan):
        '''Buy a server billing package'''
        self._packages = None  # clear cache
        ep = '/cloud/buy/%s' % (plan,)
        return self.request('GET', ep)

    def package_cancel(self, mbpkgid):
        '''Cancel a server billing package'''
        self._packages = None  # clear cache
        ep = '/cloud/cancel'
        return self.request('POST', ep, mbpkgid=mbpkgid)

    def package_unlink(self, mbpkgid):
        '''Unlink a server billing package from its location'''
        self._packages = None  # clear cache
        ep = '/cloud/unlink'
        return self.request('GET', ep, in_query=True, mbpkgid=mbpkgid)

    def locations(self):
        '''List all locations'''
        # lazy evaluation; cached during self's lifetime
        if not self._locations:
            self._locations = {}
            ret = self.request('GET', '/cloud/locations')
            for k, loc in ret.iteritems():
                code = k.split(' - ', 1)[0].upper()
                self._locations[code] = loc
        return self._locations

    def location_id(self, code):
        '''Return location ID given its letter code'''
        code = code.upper()
        try:
            loc_id = self.locations()[code]['id']
        except KeyError:
            raise HVException('No such location %s' % (code,))
        return loc_id

    def servers(self):
        '''List all servers'''
        return self.request('GET', '/cloud/servers')

    def server_build(self, mbpkgid, fqdn, location, image, **params):
        '''Deploy a server on a given package'''
        loc_id = self.location_id(location)
        ep = "/cloud/server/build/%s" % (mbpkgid,)
        return self.request('POST', ep,
                            fqdn=fqdn, location=loc_id, image=image, **params)

    def server_delete(self, mbpkgid):
        '''Delete (terminate) a server'''
        ep = '/cloud/server/delete/%s' % (mbpkgid,)
        return self.request('POST', ep)

    def server_start(self, mbpkgid):
        '''Server power on'''
        ep = '/cloud/server/start/%s' % (mbpkgid,)
        return self.request('POST', ep)

    def server_shutdown(self, mbpkgid):
        '''Server power off'''
        ep = '/cloud/server/shutdown/%s' % (mbpkgid,)
        return self.request('POST', ep)

    def _server_test_condition(self, mbpkgid, condition_fn):
        try:
            srv = self.request('GET', '/cloud/server/%s' % (mbpkgid,))
        except HVException:
            srv = {}
        return srv if condition_fn(srv) else None

    def server_wait_for(self, mbpkgid, condition_fn):
        '''Wait for server to match a condition'''
        for _ in xrange(60):
            srv = self._server_test_condition(mbpkgid, condition_fn)
            if srv:
                return srv
            time.sleep(5)
        msg = 'Timed out waiting on server (mbpkgid=%s)' % (mbpkgid,)
        raise HVException(msg)

    def server_modify(self, mbpkgid, **params):
        '''Modify server parameters'''
        srv = self.request('GET', '/cloud/server/%s' % (mbpkgid,))
        for p, v in params.iteritems():
            if srv.get(p) != v:
                break
        else:
            return srv  # nothing to modify

        srv.update(params)
        return self.request('PUT', '/cloud/server/%s' % (mbpkgid,), **srv)
