class PegaDocsMapper:
    BASE_URLS = {
        "cdh_upgrade": "https://docs.pega.com/bundle/customer-decision-hub/page/customer-decision-hub/update/cdh-update-intro.html",
        "platform_upgrade": "https://docs.pega.com/bundle/platform/page/platform/update/update-landing.html",
        "deprecated": "https://docs.pega.com/bundle/customer-service/page/customer-service/release-notes/deprecated-withdrawn-features.html",
        "openshift": "https://pegasystems.github.io/pega-helm-charts/docs/Deploying-Pega-on-openshift.html",
        "release_notes": "https://docs.pega.com/bundle/platform/page/platform/release-notes/platform-release-notes.html"
    }
    
    def get_url(self, doc_type):
        return self.BASE_URLS.get(doc_type)
    
    def get_all_urls(self):
        return self.BASE_URLS
