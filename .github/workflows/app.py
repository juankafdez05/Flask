from flask import Flask, render_template, request, abort
import json

app = Flask(__name__)

with open("pokedex.json", encoding="utf-8") as f:
    datos = json.load(f)
    pokemon_data = datos["pokemon"]

# Obtener todos los tipos disponibles
tipos_disponibles = sorted({tipo for p in pokemon_data for tipo in p["type"]})

def obtener_pokemon():
    pokemones = []
    for p in pokemon_data:
        poke = p.copy()
        poke["id_str"] = f'{poke["num"]}_{poke["name"]}'
        # Si tienes stats en otro JSON, aquí se pueden agregar
        pokemones.append(poke)
    return pokemones

@app.route('/')
def portada():
    return render_template("portada.html")

@app.route('/pokemon', methods=["GET", "POST"])
def lista_pokemon():
    lista = []
    nombre_filtro = ""
    tipo_filtro = ""
    orden = ""
    descendente = False
    busqueda_realizada = False

    if request.method == "POST":
        busqueda_realizada = True
        nombre_filtro = request.form.get("nombre", "").strip().lower()
        tipo_filtro = request.form.get("tipo", "").strip()
        orden = request.form.get("orden", "")
        descendente = request.form.get("desc") == "1"

        lista = obtener_pokemon()

        # Filtro por nombre
        if nombre_filtro:
            lista = [p for p in lista if nombre_filtro in p["name"].lower() or nombre_filtro == p["num"]]

        # Filtro por tipo
        if tipo_filtro:
            lista = [p for p in lista if tipo_filtro in p["type"]]

        # Ordenar
        if orden in ["name", "num", "weight", "height"]:
            def clave(p):
                if orden in ["weight", "height"]:
                    return float(p[orden].split(" ")[0])  # "6.9 kg" → 6.9
                return p[orden]
            lista.sort(key=clave, reverse=descendente)

    return render_template("pokemon.html",
                           tipos=tipos_disponibles,
                           pokemones=lista,
                           nombre=nombre_filtro,
                           tipo_seleccionado=tipo_filtro,
                           orden=orden,
                           desc=descendente,
                           busqueda_realizada=busqueda_realizada)

@app.route('/pokemon/<identificador>')
def detalle(identificador):
    for p in obtener_pokemon():
        if p["id_str"] == identificador:
            return render_template("detalle.html", pokemon=p)
    return abort(404)

if __name__ == '__main__':
    app.run("0.0.0.0", 5000, debug=True)
