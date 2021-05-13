import os
import requests
from flask import Flask, json, jsonify, Request, Response, request
from bs4 import BeautifulSoup

app = Flask(__name__, static_url_path='')
app.config['JSON_SORT_KEYS'] = False

@app.route('/fiibasic')
def get_fii_info():
    param_ticker = str(request.args.get('ticker', default='', type=str))
    fii = {
        'ticker': '',
        'name': '',
        'cnpj': ''
    }

    out = {
        'status_code': 0,
        'msg': None,
        'error': None,
        'data': [],
    }

    if param_ticker == '':
        out['status_code'] = 400
        out['msg'] = 'Ticker not provided'
        out['error'] = True
        resp = jsonify(out)
        resp.status_code = 400
        return resp
        

    url = f'https://www.fundsexplorer.com.br/funds/{param_ticker.upper()}'
    parser = 'html.parser'

    # Get the html
    html = requests.get(url)

    if html.status_code != 200:
        out['status_code'] = html.status_code
        out['msg'] = f'Error retrieving the ticker {param_ticker}'
        out['error'] = True
        resp = jsonify(out)
        resp.status_code = html.status_code
        return resp

    # Create the BS4 object
    soup = BeautifulSoup(html.content, parser)

    # Use CSS selector to the the DIV with ID basic-infos
    basic_div = soup.select_one('#basic-infos')
    if basic_div is None:
        out['status_code'] = 400
        out['msg'] = f'Error retrieving the basic info of the ticker {param_ticker} from {url}'
        out['error'] = True
        resp = jsonify(out)
        resp.status_code = 400
        return resp

    # Look for the name of the FII
    name_span = basic_div.find('span', text='Razão Social')
    name_span_value = name_span.find_next('span', {'class': 'description'}).get_text().strip()
    
    # Look for the span with text CNPJ
    cnpj_span = basic_div.find('span', text='CNPJ')
    # The next element will be the description one
    cnpj_span_value = cnpj_span.find_next('span', {'class': 'description'}).get_text().strip()

    fii['ticker'] = param_ticker.upper()
    fii['name'] = name_span_value.upper()
    fii['cnpj'] = cnpj_span_value

    out['status_code'] = 200
    out['msg'] = 'ok'
    out['error'] = False
    out['data'].append(fii)

    resp = jsonify(out)
    resp.status_code = 200
    return resp

def test_yf():
    url = 'https://yfstocks.herokuapp.com/quote/CSMG3?format=JSON&debug=0'
    resp = requests.get(url)
    return resp.json()

@app.route('/')
def Hello():
    print('Request for /')
    return test_yf()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f'Server running on http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, threaded=True)

# https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=19&s=0&l=10&o%5B0%5D%5BdataEntrega%5D=desc&tipoFundo=1&idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&situacao=A&_=1620694438745
# https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=20&s=50&l=1&tipoFundo=1&idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&situacao=A
# https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=24&s=0&l=10&o%5B0%5D%5BdataEntrega%5D=desc&tipoFundo=1&cnpjFundo=22219335000138&idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&situacao=A&_=1620695190350
#basic-infos > div > div > div.section-body > div > div:nth-child(2) > ul > li:nth-child(1) > div.text-wrapper > span.description
# //*[@id="basic-infos"]/div/div/div[2]/div/div[2]/ul/li[1]/div[2]/span[2]
# //*[@id="basic-infos"]/div/div/div[2]/div/div[2]/ul/li[1]/div[2]/span[1]
# //*[@id="basic-infos"]