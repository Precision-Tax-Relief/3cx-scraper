import logging

import segment.analytics as analytics
analytics.write_key = 'flhj7cmD6zKS8RVq0arL4PMkI9psUQO2'
analytics.debug = True
analytics.send = True
seg_logger = logging.getLogger('segment')
seg_logger.setLevel(logging.DEBUG)
seg_logger.addHandler(logging.StreamHandler())

analytics.identify(user_id='747b512e-91d9-43ad-915c-1a318959b0ba', traits={
    'phone_number': '9709488141'
})
analytics.shutdown()
