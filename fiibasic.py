import os
import requests
import unicodedata
from flask import Flask, json, jsonify, Request, Response, request
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/fii/<ticker>')
def get_fii_info(ticker):
    param_ticker = ticker

    fii = {
        'ticker': '',
        'name': '',
        'cnpj': ''
    }

    out = {
        'status_code': 0,
        'msg': None,
        'error': None,
        'data': {},
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

    # Create the BS4 object from the HTML
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
    # The next element will be the description one
    name_span_value = name_span.find_next('span', {'class': 'description'}).get_text().strip()
    # Remove the special chars from the FII name
    # TODO: Need to find a better way to do it...
    name_span_value = unicodedata.normalize('NFKD', name_span_value).encode('ASCII', 'ignore').decode('UTF-8')
    
    # Look for the span with text CNPJ
    cnpj_span = basic_div.find('span', text='CNPJ')
    cnpj_span_value = cnpj_span.find_next('span', {'class': 'description'}).get_text().strip()

    fii['ticker'] = param_ticker.upper()
    fii['name'] = name_span_value.upper()
    fii['cnpj'] = cnpj_span_value

    out['status_code'] = 200
    out['msg'] = 'ok'
    out['error'] = False
    out['data'] = fii

    # print(unicodedata.normalize('NFKD', name_span_value).encode('ASCII', 'ignore').decode('UTF-8'))

    resp = jsonify(out)
    resp.status_code = 200
    return resp

@app.route('/testyf')
def test_yf():
    url = 'https://yfstocks.herokuapp.com/quote/CSMG3?format=JSON&debug=0'
    resp = requests.get(url)
    return resp.json()

@app.route('/fii/')
@app.route('/')
def Hello():
    print('Request for /')
    return jsonify({'msg': 'Usage /fii/<TICKER>'})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f'Server running on http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, threaded=True, debug=True)

# https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=19&s=0&l=10&o%5B0%5D%5BdataEntrega%5D=desc&tipoFundo=1&idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&situacao=A&_=1620694438745
# https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=20&s=50&l=1&tipoFundo=1&idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&situacao=A
# https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=24&s=0&l=10&o%5B0%5D%5BdataEntrega%5D=desc&tipoFundo=1&cnpjFundo=22219335000138&idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&situacao=A&_=1620695190350
#basic-infos > div > div > div.section-body > div > div:nth-child(2) > ul > li:nth-child(1) > div.text-wrapper > span.description
# //*[@id="basic-infos"]/div/div/div[2]/div/div[2]/ul/li[1]/div[2]/span[2]
# //*[@id="basic-infos"]/div/div/div[2]/div/div[2]/ul/li[1]/div[2]/span[1]
# //*[@id="basic-infos"]