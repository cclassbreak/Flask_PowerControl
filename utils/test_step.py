from typing import List
import yaml
import logging

class TestStep():
    def __init__(self) -> None:
        with open('test_step.yaml') as f: 
            self.config = yaml.load(f, Loader=yaml.loader.FullLoader)

    def get_sites(self):
        return list(self.config.keys())
    
    def get_products(self, site=None):
        if site not in self.get_sites():
            logging.error(f'Site not found: {site}')
            raise ValueError(f'{site} info not found!')
        return list(self.config[site].keys())
    
    def get_model(self, site=None, product=None):
        if product not in self.get_products(site):
            logging.error(f'Product not found: {product}')
            raise ValueError('Product info not found!')
        return list(self.config[site][product].keys())
    
    def get_teststeps(self, site=None, product=None, model=None)->List:
        '''
        example:[{'phase': 'ABC', 'voltage': 418, 'frequency': 50}, {'phase': 'ACB', 'voltage': 418, 'frequency': 50}]
        '''
        if model not in self.get_model(site, product):
            logging.error(f'Model not found: {model}')
            raise ValueError('model info not found!')
        return self.config[site][product][model]
        


if __name__ == '__main__':
    ts = TestStep()
    print(ts.get_sites())
    print(ts.get_products(site='CN9B'))
    print(ts.get_model(site='CN9B', product='CT'))
    print(ts.get_teststeps(site='CN9B', product='CT', model='US-Product'))
    a = ts.get_teststeps(site='CN9B', product='CT', model='US-Product')
    print(a[0])