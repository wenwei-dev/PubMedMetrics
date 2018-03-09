import logging
from altmetric import Altmetric, AltmetricHTTPException

logger = logging.getLogger(__name__)

def queryAltmetric(pmid):
    """
    Check the altmetric journal percentile score of the publication
    """
    a = Altmetric()
    try:
        resp = a.pmid(pmid)
        if resp is None:
            logger.debug("PMID %s. Not found" % pmid)
            return -1
        else:
            if 'context' in resp:
                metric = resp['context']['journal']['pct'] # Percentage attention for this journal
                logger.debug("PMID %s. Metric %s" % (pmid, metric))
                return metric
            logger.debug("PMID %s. Percentage attention not found" % pmid)
            return -2
    except AltmetricHTTPException as e:
        if e.status_code == 403:
            logger.error("You aren't authorized for this call: {}".format(pmid))
        elif e.status_code == 420:
            logger.error('You are being rate limited, currently {}'.format(pmid))
        elif e.status_code == 502:
            logger.error('The API version you are using is currently down for maintenance.')
        elif e.status_code == 404:
            logger.error('Invalid API function')
            logger.error(e.msg)
        logger.warn("PMID %s. Exception %s" % (pmid, e.msg))
        return -3

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    queryAltmetric('29554097')
    queryAltmetric('29545237')
    queryAltmetric('29552423')

