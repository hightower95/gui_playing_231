from productivity_app.data_pipeline.reports.compare_house_prices import *
from productivity_app.data_pipeline.registry import registry

r = registry.get_all_reports()
params = r['Compare House Prices Report']['inputs']
for p in params:
    print(f'name={p.name}')
    print(f'title={p.title}')
    print(f'repr={repr(p)}')
    print('---')
