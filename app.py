from datetime import datetime, date
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Calculadora de Diárias - Defesa Civil SC</title>
    <style>
        body {
            font-family: sans-serif;
            background-color: #f8fafc;
            margin: 0;
            padding: 40px;
        }
        .container {
            max-width: 800px;
            margin: auto;
            background-color: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
        }
        h2 {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 24px;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 4px;
            font-weight: 500;
        }
        input[type="date"],
        input[type="time"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
        }
        button {
            background-color: #0f172a;
            color: white;
            padding: 12px;
            width: 100%;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
        }
        .resultado {
            margin-top: 30px;
            background-color: #f1fdf7;
            padding: 20px;
            border-radius: 8px;
        }
        .resultado p {
            margin: 6px 0;
        }
        .resultado strong {
            font-size: 1.2rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Calculadora de Diárias - Defesa Civil SC</h2>
        <form method="POST">
            <div class="grid">
                <div>
                    <label>Data de Saída:</label>
                    <input type="date" name="data_saida" required>
                    <label>Hora de Saída:</label>
                    <input type="time" name="hora_saida" required>
                </div>
                <div>
                    <label>Data de Retorno:</label>
                    <input type="date" name="data_retorno" required>
                    <label>Hora de Retorno:</label>
                    <input type="time" name="hora_retorno" required>
                </div>
            </div>
            <button type="submit">Calcular</button>
        </form>

        {% if resultado %}
            <div class="resultado">
                <p>Pernoites: {{ resultado['pernoites'] }} (R$ {{ "%.2f" % resultado['valor_pernoites'] }})</p>
                <p>Diárias: {{ resultado['diarias'] }} (R$ {{ "%.2f" % resultado['valor_diarias'] }})</p>
                <p><strong>Total: R$ {{ "%.2f" % resultado['total'] }}</strong></p>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

# Função de cálculo permanece a mesma

def calcular_diarias(data_saida_str, hora_saida_str, data_retorno_str, hora_retorno_str):
    VALOR_MEIA_DIARIA = 55.00
    VALOR_DIARIA_INTEIRA = 110.00
    VALOR_PERNOITE = 220.00

    data_hora_saida = datetime.strptime(f"{data_saida_str} {hora_saida_str}", "%Y-%m-%d %H:%M")
    data_hora_retorno = datetime.strptime(f"{data_retorno_str} {hora_retorno_str}", "%Y-%m-%d %H:%M")

    pernoites = (data_hora_retorno.date() - data_hora_saida.date()).days
    valor_pernoites = pernoites * VALOR_PERNOITE

    diarias = 0
    valor_diarias = 0

    if pernoites == 0:
        duracao_horas = (data_hora_retorno - data_hora_saida).total_seconds() / 3600
        if duracao_horas >= 12:
            diarias = 1
            valor_diarias = VALOR_DIARIA_INTEIRA
        elif duracao_horas > 0:
            diarias = 0.5
            valor_diarias = VALOR_MEIA_DIARIA
    else:
        mesma_janela = data_hora_retorno.time() >= data_hora_saida.time()
        if mesma_janela:
            base_hora_retorno = datetime.combine(data_hora_retorno.date(), data_hora_saida.time())
            duracao_retorno = (data_hora_retorno - base_hora_retorno).total_seconds() / 3600
            if duracao_retorno >= 12:
                diarias = 1
                valor_diarias = VALOR_DIARIA_INTEIRA
            elif duracao_retorno > 0:
                diarias = 0.5
                valor_diarias = VALOR_MEIA_DIARIA

    total = valor_pernoites + valor_diarias

    return {
        "pernoites": pernoites,
        "valor_pernoites": valor_pernoites,
        "diarias": diarias,
        "valor_diarias": valor_diarias,
        "total": total
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        data_saida = request.form['data_saida']
        hora_saida = request.form['hora_saida']
        data_retorno = request.form['data_retorno']
        hora_retorno = request.form['hora_retorno']
        resultado = calcular_diarias(data_saida, hora_saida, data_retorno, hora_retorno)
    return render_template_string(HTML, resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)
