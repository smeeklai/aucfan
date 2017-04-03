import statsmodels.api as sm

class PredictPrice(object):
    def execute(self):
        return sm.version.version.title()

