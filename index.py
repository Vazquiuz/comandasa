import tkinter as tk
import sqlite3
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import filedialog
import time
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime
import pandas as pd
import os

configuracion_restaurante = {"nombre": "Mi Restaurante", "datos_facturacion": "Datos de Facturación"}
informacion_comanda = {"numero_mesa": "", "nombre_mesero": "", "comentarios": ""}

def abrir_ventana_configuracion():
    ventana_config = tk.Toplevel()
    ventana_config.title("Configuración del Restaurante")

    tk.Label(ventana_config, text="Nombre del Restaurante:").pack()
    entry_nombre_restaurante = tk.Entry(ventana_config)
    entry_nombre_restaurante.insert(0, configuracion_restaurante["nombre"])
    entry_nombre_restaurante.pack()

    tk.Label(ventana_config, text="Datos de Facturación:").pack()
    entry_datos_facturacion = tk.Entry(ventana_config)
    entry_datos_facturacion.insert(0, configuracion_restaurante["datos_facturacion"])
    entry_datos_facturacion.pack()

    def guardar_configuracion():
        configuracion_restaurante["nombre"] = entry_nombre_restaurante.get()
        configuracion_restaurante["datos_facturacion"] = entry_datos_facturacion.get()
        ventana_config.destroy()

    tk.Button(ventana_config, text="Guardar Configuración", command=guardar_configuracion).pack()

def guardar_informacion_comanda(numero_mesa, nombre_mesero, comentarios):
    informacion_comanda['numero_mesa'] = numero_mesa
    informacion_comanda['nombre_mesero'] = nombre_mesero
    informacion_comanda['comentarios'] = comentarios

def inicializar_db():
    conexion = sqlite3.connect('restaurante.db')
    cursor = conexion.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS platillos (id INTEGER PRIMARY KEY, nombre TEXT, precio REAL)''')
    conexion.commit()
    conexion.close()

inicializar_db()

def agregar_platillo(nombre, precio):
    conexion = sqlite3.connect('restaurante.db')
    cursor = conexion.cursor()
    cursor.execute('INSERT INTO platillos (nombre, precio) VALUES (?, ?)', (nombre, precio))
    conexion.commit()
    conexion.close()

def modificar_platillo(id, nombre, precio):
    conexion = sqlite3.connect('restaurante.db')
    cursor = conexion.cursor()
    cursor.execute('UPDATE platillos SET nombre = ?, precio = ? WHERE id = ?', (nombre, precio, id))
    conexion.commit()
    conexion.close()

def eliminar_platillo(id):
    conexion = sqlite3.connect('restaurante.db')
    cursor = conexion.cursor()
    cursor.execute('DELETE FROM platillos WHERE id = ?', (id,))
    conexion.commit()
    conexion.close()

def agregar_platillo_interfaz():
    def guardar_platillo():
        nombre = entry_nombre.get()
        precio = float(entry_precio.get())
        agregar_platillo(nombre, precio)
        ventana_agregar.destroy()

    ventana_agregar = tk.Toplevel()
    ventana_agregar.title("Añadir Platillo")

    tk.Label(ventana_agregar, text="Nombre:").pack()
    entry_nombre = tk.Entry(ventana_agregar)
    entry_nombre.pack()

    tk.Label(ventana_agregar, text="Precio:").pack()
    entry_precio = tk.Entry(ventana_agregar)
    entry_precio.pack()

    tk.Button(ventana_agregar, text="Guardar Platillo", command=guardar_platillo).pack()

def actualizar_lista_platillos(lista_platillos):
    lista_platillos.delete(0, tk.END)
    conexion = sqlite3.connect('restaurante.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre FROM platillos")
    for platillo in cursor.fetchall():
        lista_platillos.insert(tk.END, f"{platillo[0]} - {platillo[1]}")
    conexion.close()

def abrir_formulario_modificacion(lista_platillos):
    id_platillo = obtener_id_platillo_seleccionado(lista_platillos)
    if id_platillo:
        conexion = sqlite3.connect('restaurante.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, precio FROM platillos WHERE id = ?", (id_platillo,))
        platillo = cursor.fetchone()
        conexion.close()

        if platillo:
            ventana_modificar = tk.Toplevel()
            ventana_modificar.title("Modificar Platillo")

            tk.Label(ventana_modificar, text="Nombre:").pack()
            entry_nombre = tk.Entry(ventana_modificar)
            entry_nombre.insert(0, platillo[0])
            entry_nombre.pack()

            tk.Label(ventana_modificar, text="Precio:").pack()
            entry_precio = tk.Entry(ventana_modificar)
            entry_precio.insert(0, platillo[1])
            entry_precio.pack()

            def guardar_cambios():
                nombre = entry_nombre.get()
                precio = entry_precio.get()
                modificar_platillo(id_platillo, nombre, float(precio))
                ventana_modificar.destroy()
                actualizar_lista_platillos(lista_platillos)

            tk.Button(ventana_modificar, text="Guardar Cambios", command=guardar_cambios).pack()

def obtener_id_platillo_seleccionado(lista_platillos):
    seleccion = lista_platillos.curselection()
    if not seleccion:
        return None
    return lista_platillos.get(seleccion[0]).split(' - ')[0]

def eliminar_platillo_seleccionado(lista_platillos):
    id_platillo = obtener_id_platillo_seleccionado(lista_platillos)
    if id_platillo and messagebox.askyesno("Confirmar", "¿Eliminar este platillo?"):
        eliminar_platillo(id_platillo)
        actualizar_lista_platillos(lista_platillos)

def agregar_informacion_comanda():
    ventana_info = tk.Toplevel()
    ventana_info.title("Información de la Comanda")

    tk.Label(ventana_info, text="Número de Mesa:").pack()
    entry_numero_mesa = tk.Entry(ventana_info)
    entry_numero_mesa.pack()

    tk.Label(ventana_info, text="Nombre del Mesero:").pack()
    entry_nombre_mesero = tk.Entry(ventana_info)
    entry_nombre_mesero.pack()

    tk.Label(ventana_info, text="Comentarios para Cocineros:").pack()
    entry_comentarios = tk.Text(ventana_info, height=5)
    entry_comentarios.pack()

    def guardar_info_comanda():
        informacion_comanda["numero_mesa"] = entry_numero_mesa.get()
        informacion_comanda["nombre_mesero"] = entry_nombre_mesero.get()
        informacion_comanda["comentarios"] = entry_comentarios.get("1.0", tk.END)
        ventana_info.destroy()

    tk.Button(ventana_info, text="Guardar Información", command=guardar_info_comanda).pack()

def generar_comanda_pdf(platillos, nombre_archivo, configuracion, informacion):
    ancho_ticket, alto_ticket = 3 * inch, 11 * inch
    c = canvas.Canvas(nombre_archivo, pagesize=(ancho_ticket, alto_ticket))

    # Configuración de la comanda
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(ancho_ticket / 2, alto_ticket - 20, configuracion_restaurante["nombre"])

    # Numeración de la comanda y fecha/hora
    numero_comanda = int(datetime.now().timestamp())
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.setFont("Helvetica", 8)  # Reducir tamaño de la fuente
    c.drawString(10, alto_ticket - 35, f"Comanda N° {numero_comanda}")  # Posición modificada para el número de comanda
    c.drawString(10, alto_ticket - 45, f"Fecha/Hora: {fecha_hora_actual}")  # Posición modificada para fecha/hora

    c.line(10, alto_ticket - 55, ancho_ticket - 10, alto_ticket - 55)  # Línea separadora ajustada
    y_actual = alto_ticket - 75  # Ajustar posición inicial del contenido

    # Información de la mesa y del mesero
    if 'numero_mesa' in informacion_comanda and 'nombre_mesero' in informacion_comanda:
        c.drawString(10, y_actual, f"Mesa: {informacion_comanda['numero_mesa']} - Mesero: {informacion_comanda['nombre_mesero']}")
        y_actual -= 20
        c.line(10, y_actual, ancho_ticket - 10, y_actual)
        y_actual -= 10

    # Listado de platillos
    for platillo in platillos:
        c.drawString(10, y_actual, f"{platillo['nombre']} - ${platillo['precio']}")
        y_actual -= 15

    # Comentarios
    if 'comentarios' in informacion_comanda:
        y_actual -= 5
        c.line(10, y_actual, ancho_ticket - 10, y_actual)
        y_actual -= 15
        c.drawString(10, y_actual, "Comentarios:")
        y_actual -= 15
        comentarios = informacion_comanda['comentarios'].split('\n')
        for linea in comentarios:
            c.drawString(10, y_actual, linea)
            y_actual -= 15

    # Datos de facturación
    c.line(10, 50, ancho_ticket - 10, 50)
    c.drawString(10, 40, configuracion_restaurante["datos_facturacion"])

    c.save()

def recopilar_platillos_para_comanda(lista_platillos):
    platillos_seleccionados = []
    indices_seleccionados = lista_platillos.curselection()
    conexion = sqlite3.connect('restaurante.db')
    cursor = conexion.cursor()
    for indice in indices_seleccionados:
        id_platillo = lista_platillos.get(indice).split(' - ')[0]
        cursor.execute("SELECT nombre, precio FROM platillos WHERE id = ?", (id_platillo,))
        platillo = cursor.fetchone()
        platillos_seleccionados.append({'nombre': platillo[0], 'precio': platillo[1]})
    conexion.close()
    return platillos_seleccionados

def guardar_comanda_en_excel(informacion_comanda, platillos_seleccionados, ruta_archivo="ventas.xlsx"):
    if not os.path.exists(ruta_archivo):
        df = pd.DataFrame(columns=["Número Comanda", "Fecha", "Mesero", "Mesa", "Platillo", "Cantidad", "Precio Unitario", "Total"])
    else:
        df = pd.read_excel(ruta_archivo)

    numero_comanda = int(datetime.now().timestamp())
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for platillo in platillos_seleccionados:
        total = platillo['precio']
        nueva_fila = pd.DataFrame([{
            "Número Comanda": numero_comanda,
            "Fecha": fecha,
            "Mesero": informacion_comanda["nombre_mesero"],
            "Mesa": informacion_comanda["numero_mesa"],
            "Platillo": platillo["nombre"],
            "Cantidad": 1,
            "Precio Unitario": platillo["precio"],
            "Total": total
        }])
        df = pd.concat([df, nueva_fila], ignore_index=True)

    df.to_excel(ruta_archivo, index=False)

def main():
    ventana = tk.Tk()
    ventana.title("Sistema de Gestión de Restaurante")
    ventana.geometry("800x600")

    lista_platillos = tk.Listbox(ventana, selectmode=tk.MULTIPLE)
    lista_platillos.pack()
    actualizar_lista_platillos(lista_platillos)
    def generar_comanda_y_guardar(informacion_comanda, lista_platillos, nombre_archivo_pdf="comanda.pdf", nombre_archivo_excel="ventas.xlsx"):
       platillos_seleccionados = recopilar_platillos_para_comanda(lista_platillos)
       generar_comanda_pdf(platillos_seleccionados, nombre_archivo_pdf, configuracion_restaurante, informacion_comanda)
       guardar_comanda_en_excel(informacion_comanda, platillos_seleccionados, nombre_archivo_excel)

    tk.Button(ventana, text="Generar Comanda y Guardar en Excel", command=lambda: generar_comanda_y_guardar(informacion_comanda, lista_platillos)).pack()
    tk.Button(ventana, text="Añadir Platillo", command=agregar_platillo_interfaz).pack()
    tk.Button(ventana, text="Modificar Platillo", command=lambda: abrir_formulario_modificacion(lista_platillos)).pack()
    tk.Button(ventana, text="Eliminar Platillo", command=lambda: eliminar_platillo_seleccionado(lista_platillos)).pack()
    tk.Button(ventana, text="Añadir Información de Comanda", command=agregar_informacion_comanda).pack()
    tk.Button(ventana, text="Configuración del Restaurante", command=abrir_ventana_configuracion).pack()

    ventana.mainloop()

if __name__ == "__main__":
    main()
