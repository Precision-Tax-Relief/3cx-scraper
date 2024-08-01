import logging
import segment.analytics as analytics

seg_logger = logging.getLogger('segment')
seg_logger.setLevel(logging.DEBUG)
seg_logger.addHandler(logging.StreamHandler())

test1 = '8T7p3QOwdfqOi9h5XszVCDZaBU3DmgMi'
analytics.write_key = test1
analytics.debug = True
analytics.identify(anonymous_id='test1', traits={
    'test': '1'
})
test1_client = analytics.default_client
test1_client.flush()
analytics.default_client = None

test2 = 'kCZYPQD8kcjQSc0khgMA8nkaHyr0NVMF'
analytics.write_key = test2
analytics.identify(anonymous_id='test2', traits={
    'test': '2'
})
