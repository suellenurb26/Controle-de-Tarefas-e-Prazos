from flask import Flask, render_template, request, redirect, url_for import sqlite3 from datetime import datetime

app = Flask(name) DB = 'tarefas.db'

def init_db(): conn = sqlite3.connect(DB) c = conn.cursor() c.execute(''' CREATE TABLE IF NOT EXISTS tarefas ( id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, tipo TEXT, link TEXT, prazo TEXT, status TEXT DEFAULT 'Pendente' ) ''') conn.commit() conn.close()

def get_tarefas(): conn = sqlite3.connect(DB) c = conn.cursor() c.execute('SELECT * FROM tarefas ORDER BY prazo ASC') tarefas = c.fetchall() conn.close() return tarefas

@app.route('/') def index(): tarefas = get_tarefas() hoje = datetime.now().date() return render_template('index.html', tarefas=tarefas, hoje=hoje)

@app.route('/add', methods=['POST']) def add(): titulo = request.form['titulo'] tipo = request.form['tipo'] link = request.form['link'] prazo = request.form['prazo']

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute('INSERT INTO tarefas (titulo, tipo, link, prazo) VALUES (?, ?, ?, ?)',
          (titulo, tipo, link, prazo))
conn.commit()
conn.close()
return redirect(url_for('index'))

@app.route('/done/int:id') def done(id): conn = sqlite3.connect(DB) c = conn.cursor() c.execute("UPDATE tarefas SET status='Concluído' WHERE id=?", (id,)) conn.commit() conn.close() return redirect(url_for('index'))

@app.route('/delete/int:id') def delete(id): conn = sqlite3.connect(DB) c = conn.cursor() c.execute('DELETE FROM tarefas WHERE id=?', (id,)) conn.commit() conn.close() return redirect(url_for('index'))

if name == 'main': init_db() app.run(host='0.0.0.0', port=5000)

templates/index.html

'''

<!DOCTYPE html><html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Controle de Prazos</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
<style>
body { background: #f5f7fa; }
.card { border-radius: 12px; }
.late { background-color: #ffe5e5 !important; }
.today { background-color: #fff3cd !important; }
.done { opacity: 0.6; }
</style>
</head>
<body class="container py-4"><h2 class="mb-4">📋 Controle de Prazos</h2><div class="card p-3 mb-4">
<form method="POST" action="/add" class="row g-2">
    <div class="col-md-3"><input class="form-control" name="titulo" placeholder="Título" required></div>
    <div class="col-md-2"><input class="form-control" name="tipo" placeholder="Tipo"></div>
    <div class="col-md-3"><input class="form-control" name="link" placeholder="Link"></div>
    <div class="col-md-2"><input class="form-control" type="date" name="prazo" required></div>
    <div class="col-md-2"><button class="btn btn-primary w-100">Adicionar</button></div>
</form>
</div><div class="card p-3">
<table class="table table-hover">
<thead>
<tr>
<th>Título</th>
<th>Tipo</th>
<th>Prazo</th>
<th>Status</th>
<th>Ações</th>
</tr>
</thead>
<tbody>
{% for t in tarefas %}
{% set prazo = t[4][:10] %}
{% set prazo_date = prazo|safe %}
<tr class="
{% if t[5]=='Concluído' %}done
{% elif prazo < hoje|string %}late
{% elif prazo == hoje|string %}today
{% endif %}"><td><a href="{{ t[3] }}" target="_blank">{{ t[1] }}</a></td>
<td>{{ t[2] }}</td>
<td>{{ t[4] }}</td>
<td>{{ t[5] }}</td>
<td>
<a href="/done/{{ t[0] }}" class="btn btn-success btn-sm">✔</a>
<button onclick="confirmDelete({{ t[0] }})" class="btn btn-danger btn-sm">🗑</button>
</td>
</tr>
{% endfor %}
</tbody>
</table>
</div><script>
function confirmDelete(id) {
    Swal.fire({
        title: 'Excluir?',
        text: 'Essa ação não pode ser desfeita',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, excluir'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location = '/delete/' + id
        }
    })
}

// ALERTA AUTOMÁTICO DE PRAZOS
window.onload = () => {
    let atrasados = document.querySelectorAll('.late').length
    if (atrasados > 0) {
        Swal.fire({
            icon: 'error',
            title: 'Atenção!',
            text: atrasados + ' tarefa(s) atrasada(s)!'
        })
    }
}
</script></body>
</html>
