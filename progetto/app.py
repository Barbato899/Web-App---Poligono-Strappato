from flask import Flask, render_template, request
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)

archivio = []


def quadrato_strappato(vertici, profondita):
    if profondita == 0:
        return vertici

    nuovi_punti = []
    numero_vertici = len(vertici)

    for i in range(numero_vertici):
        p1 = vertici[i]
        p2 = vertici[(i + 1) % numero_vertici]

        primo_terzo   = p1 + (p2 - p1) / 3
        secondo_terzo = p1 + (p2 - p1) * 2 / 3

        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        lunghezza = np.sqrt(dx**2 + dy**2)

        normale_x = -dy / lunghezza
        normale_y =  dx / lunghezza

        centro  = (primo_terzo + secondo_terzo) / 2
        altezza = lunghezza / 3
        apice   = centro + np.array([normale_x, normale_y]) * altezza

        nuovi_punti.extend([p1, primo_terzo, apice, secondo_terzo])

    return quadrato_strappato(np.array(nuovi_punti), profondita - 1)


def genera_immagine(vertici, profondita):
    pts = quadrato_strappato(np.array(vertici, dtype=float), profondita)

    xs = np.append(pts[:, 0], pts[0, 0])
    ys = np.append(pts[:, 1], pts[0, 1])

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.grid(True, color='lightgray', linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.fill(xs, ys, color='#4B66FE', zorder=1)
    ax.plot(xs, ys, color='#4B66FE', linewidth=0.5, zorder=2)
    ax.set_title(f'Quadrato Strappato — Livello {profondita}', fontsize=13)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    immagine_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return immagine_base64


@app.route('/')
def home():
    return render_template('teoria.html', title='Quadrato Strappato', immagine=None)


@app.route('/frattale', methods=['GET', 'POST'])
def frattale():
    if request.method == 'GET':
        return render_template('genera_frattale.html', title='Quadrato Strappato', immagine=None)

    x1         = float(request.form.get('x1', 0))
    y1         = float(request.form.get('y1', 1))
    lato       = float(request.form.get('lato', 5))
    profondita = int(request.form.get('profondita', 3))

    vertici = [
        [x1,        y1],
        [x1 + lato, y1],
        [x1 + lato, y1 + lato],
        [x1,        y1 + lato]
    ]

    immagine = genera_immagine(vertici, profondita)

    return render_template('genera_frattale.html',
                           title='Quadrato Strappato',
                           immagine=immagine,
                           lato=lato,
                           profondita=profondita,
                           x1=x1,
                           y1=y1)


# ── Salva in archivio ─────────────────────────────────────────────────────────
@app.route('/salva_archivio', methods=['POST'])
def salva_archivio():
    x1         = float(request.form.get('x1', 0))
    y1         = float(request.form.get('y1', 1))
    lato       = float(request.form.get('lato', 5))
    profondita = int(request.form.get('profondita', 3))

    vertici = [
        [x1,        y1],
        [x1 + lato, y1],
        [x1 + lato, y1 + lato],
        [x1,        y1 + lato]
    ]

    immagine = genera_immagine(vertici, profondita)

    archivio.append({
        'immagine':   immagine,
        'x1':         x1,
        'y1':         y1,
        'lato':       lato,
        'profondita': profondita,
        'data':       datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'id':         len(archivio) 
    })

    return render_template('genera_frattale.html',
                           title='Quadrato Strappato',
                           immagine=immagine,
                           lato=lato,
                           profondita=profondita,
                           x1=x1,
                           y1=y1,
                           salvato=True)


# ── Archivio ──────────────────────────────────────────────────────────────────
@app.route('/archivio')
def pagina_archivio():
    return render_template('archivio.html',
                           title='Archivio Frattali',
                           archivio=archivio)


@app.route('/elimina/<int:id>', methods=['POST'])
def elimina(id):
    global archivio
    archivio = [f for f in archivio if f['id'] != id]
    return render_template('archivio.html',
                           title='Archivio Frattali',
                           archivio=archivio)


@app.route('/teoria')
def teoria():
    return render_template('teoria.html', title='Teoria Generale')


@app.route('/teoria2')
def teoria2():
    return render_template('teoria2.html', title='Poligono Strappato')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')