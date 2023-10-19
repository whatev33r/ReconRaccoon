from ReconRaccoon.src.modules.subenum.main import SubEnum

class TestSubEnum:

    def setup_method(self):
        self.sample_wordlist = "resources/sample_wordlist.txt"
        self.sub_enum = SubEnum('google.com', self.sample_wordlist, False, False)

    def test_filter_wordlist(self):
        wordlist = self.sub_enum.filter_wordlist(self.sample_wordlist)
        assert wordlist == ['www', 'blog', 'mail', 'dev', 'test', 'admin', 'api', 'app', 'login', 'ftp', 'support', 'forum', 'shop', 'demo']

    def test_get_wildcard(self):
        wildcard = self.sub_enum.get_wildcard()
        assert wildcard != ''
        
    def test_enumerate_subdomains(self):
        self.sub_enum.enumerate_subdomains()
        assert self.sub_enum.ips != []
        assert self.sub_enum.subs != []
