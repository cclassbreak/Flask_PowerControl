import time
from flask import Flask, render_template, request,redirect,url_for,make_response
from flask_basicauth import BasicAuth
import datetime
from configparser import ConfigParser
from utils import TestStep, PowerSupply
import logging

ts = TestStep()
power_supply = PowerSupply()

config = ConfigParser()
config.read('config.ini')
ACCOUNT = config.get('Website', 'ACCOUNT')
PASSWORD = config.get('Website', 'PASSWORD')
VERSION = config.get('Info', 'VERSION')

app = Flask(__name__)
basic_auth = BasicAuth(app)
app.config['BASIC_AUTH_USERNAME'] = ACCOUNT
app.config['BASIC_AUTH_PASSWORD'] = PASSWORD

@app.route('/')
@basic_auth.required
def home():
    bay_number = request.cookies.get('bay_number')
    if not bay_number:
        return redirect('/setcookie')
    resp = make_response(render_template('select_site.html',sites=ts.get_sites(), bay_number=bay_number, version = VERSION))
    return resp

@app.route('/stop')
@basic_auth.required
def stop():
    power_supply.set_mode('STOP')
    power_supply.mode = None
    power_supply.voltage = None
    power_supply.frequency = None
    resp = redirect('/')
    return resp

@app.route('/select_site/<site>')
@basic_auth.required
def select_product(site):
    bay_number = request.cookies.get('bay_number')
    if not bay_number:
        return redirect('/setcookie')
    products = ts.get_products(site=site)
    resp = make_response(render_template('select_product.html',version = VERSION, sites=ts.get_sites(),site = site, bay_number=bay_number, products=products))
    return resp

@app.route('/select_site/<site>/select_product/<product>')
@basic_auth.required
def select_model(site,product):
    bay_number = request.cookies.get('bay_number')
    if not bay_number:
        return redirect('/setcookie')
    models = ts.get_model(site=site,product=product)
    resp = make_response(render_template('select_model.html',version = VERSION, sites=ts.get_sites(),site = site, bay_number=bay_number, product=product, models=models))
    return resp

@app.route('/select_site/<site>/select_product/<product>/select_model/<model>/test_step/<step>')
@basic_auth.required
def test_step(site,product,model,step):
    bay_number = request.cookies.get('bay_number')
    if not bay_number:
        return redirect('/setcookie')
    test_steps = ts.get_teststeps(site=site, product=product, model=model)
    if step == '0':
        if power_supply.in_use==True:
            return render_template('Occupied.html')
        feedback_mode = power_supply.get_mode()
        time.sleep(.2)
        feedback_voltage, feedback_frequency = power_supply.get_power()
        resp = make_response(render_template('test_step.html',version = VERSION, site = site, bay_number=bay_number, product=product, model=model, step=step, current_mode='准备开始', button_text='开始',
            feedback_mode=feedback_mode, feedback_voltage=feedback_voltage, feedback_frequency=feedback_frequency))
    else:
        step = int(step) - 1
        current_mode=test_steps[int(step)]
        phase, voltage, frequency = current_mode.values()
        if power_supply.mode != phase:
            power_supply.set_mode(mode=phase)
            time.sleep(.2)
        if power_supply.frequency != frequency or power_supply.voltage != frequency:
            power_supply.set_power(volt=voltage, freq=frequency)
            time.sleep(.2)
        feedback_mode = power_supply.get_mode()
        time.sleep(.2)
        feedback_voltage, feedback_frequency = power_supply.get_power()
        button_text = '下一步'
        button_text = '结束' if int(step) == len(test_steps)-1 else button_text
        current_step_text = f'相序:{phase}, 电压{voltage}V, 频率{frequency}Hz'
        resp = make_response(render_template('test_step.html',version = VERSION, site = site, bay_number=bay_number, product=product, model=model, step=int(step)+1, current_mode=current_step_text, button_text=button_text,
            feedback_mode=feedback_mode, feedback_voltage=feedback_voltage, feedback_frequency=feedback_frequency))
    return resp

@app.route('/setcookie', methods = ['POST', 'GET'])
@basic_auth.required
def setcookie():
   if request.method == 'POST':
      bay_number = request.form['number']
      resp = make_response(render_template('select_site.html',version = VERSION, sites = ts.get_sites(), bay_number = bay_number))
      resp.set_cookie('bay_number', bay_number,expires=datetime.datetime.now() + datetime.timedelta(days=900))
   else:
      resp=render_template('setCookie.html')
   return resp


if __name__ == '__main__':
    app.run(debug=False)

