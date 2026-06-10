from datetime import datetime
import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
from tkcalendar import DateEntry
from playwright.sync_api import sync_playwright


# --- LÓGICA DE DATOS (JSON) ---
def obtener_siguiente_numero():
    if not os.path.exists("cupones.json"):
        return 1
    try:
        with open("cupones.json", "r", encoding="utf-8") as f:
            cupones = json.load(f)
            if not cupones:
                return 1
            ultimo_id = max(cupon["id"] for cupon in cupones)
            return ultimo_id + 1
    except Exception:
        return 1


def cargar_todos_los_cupones():
    if not os.path.exists("cupones.json"):
        return []
    try:
        with open("cupones.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def guardar_cupon_json(id_cupon, canje, para, emision, vence):
    nuevo_cupon = {
        "id": id_cupon,
        "codigo": str(id_cupon).zfill(4),
        "canje_por": canje,
        "para": para,
        "fecha_emision": emision,
        "fecha_vencimiento": vence if vence else "Sin vencimiento",
        "canjeado": False,
    }
    cupones = cargar_todos_los_cupones()
    cupones.append(nuevo_cupon)
    with open("cupones.json", "w", encoding="utf-8") as f:
        json.dump(cupones, f, indent=4, ensure_ascii=False)
    return nuevo_cupon


def modificar_estado_canje(codigo_cupon):
    cupones = cargar_todos_los_cupones()
    for cupon in cupones:
        if cupon["codigo"] == codigo_cupon:
            nuevo_estado = not cupon["canjeado"]
            cupon["canjeado"] = nuevo_estado

            with open("cupones.json", "w", encoding="utf-8") as f:
                json.dump(cupones, f, indent=4, ensure_ascii=False)

            return True, nuevo_estado
    return False, None


# --- GENERACIÓN DEL ARCHIVO HTML EMITIDO (INLINE SVG) ---
def generar_html_cupon(cupon_data):
    f_emision = f"/ {cupon_data['fecha_emision'].replace('/', ' / ')} /"
    f_vence = cupon_data["fecha_vencimiento"]
    if "/" in f_vence:
        f_vence = f"/ {f_vence.replace('/', ' / ')} /"

    try:
        with open("index.html", "r", encoding="utf-8") as archivo_html:
            html_content = archivo_html.read()
    except Exception as e:
        messagebox.showerror(
            "Error de lectura",
            f"No se pudo encontrar o leer el archivo index.html:\n{e}",
        )
        return False, ""

    try:
        with open("lacasavarietal-logo.svg", "r", encoding="utf-8") as archivo_svg:
            logo_svg_code = archivo_svg.read()
    except Exception as e:
        print(f"Error de lectura del logo SVG: {e}")
        logo_svg_code = ""

    html_content = html_content.replace(
        "{{canje_por}}", str(cupon_data["canje_por"])
    )
    html_content = html_content.replace("{{para}}", str(cupon_data["para"]))
    html_content = html_content.replace("{{fecha_emision}}", f_emision)
    html_content = html_content.replace("{{fecha_vencimiento}}", f_vence)
    html_content = html_content.replace("{{codigo}}", str(cupon_data["codigo"]))
    html_content = html_content.replace("{{logo_svg}}", logo_svg_code)

    carpeta_destino = "cupones-html"
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    nombre_archivo = f"cupon_{cupon_data['codigo']}.html"
    ruta_final = os.path.join(carpeta_destino, nombre_archivo)

    try:
        with open(ruta_final, "w", encoding="utf-8") as nuevo_archivo:
            nuevo_archivo.write(html_content)
        return True, ruta_final
    except Exception as e:
        messagebox.showerror(
            "Error al guardar", f"No se pudo escribir el archivo final:\n{e}"
        )
        return False, ""


# --- INTERFAZ TKINTER ---
def procesar_formulario():
    canje = entry_canje.get().strip()
    para = entry_para.get().strip()

    if var_tiene_vence.get():
        vence = entry_vence.get()
    else:
        vence = ""

    if not canje or not para:
        messagebox.showwarning(
            "Faltan datos", "Completá 'Canjeable por' y 'Para'."
        )
        return

    id_actual = obtener_siguiente_numero()
    emision_hoy = datetime.now().strftime("%d/%m/%Y")

    cupon = guardar_cupon_json(id_actual, canje, para, emision_hoy, vence)
    exito, ruta_html = generar_html_cupon(cupon)

    if exito:
        # --- NUEVA LÓGICA: Conversión automática a PDF sin clicks manuales ---
        try:
            carpeta_pdf = "cupones-pdf"
            if not os.path.exists(carpeta_pdf):
                os.makedirs(carpeta_pdf)

            nombre_pdf = f"cupon_{cupon['codigo']}.pdf"
            ruta_pdf = os.path.join(carpeta_pdf, nombre_pdf)

            ruta_html_absoluta = os.path.abspath(ruta_html)
            ruta_pdf_absoluta = os.path.abspath(ruta_pdf)

            # Inicializamos Playwright para imprimir el HTML a PDF en segundo plano
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(f"file://{ruta_html_absoluta}")
                
                page.pdf(
                    path=ruta_pdf_absoluta,
                    width="18cm",  # Ajustado al nuevo @page
                    height="11.5cm", # Le da la altura suficiente para que entre todo en una sola hoja
                    print_background=True,
                    margin={
                        "top": "0mm",
                        "right": "0mm",
                        "bottom": "0mm",
                        "left": "0mm"
                    }
                )
                browser.close()

            # Se abre el PDF generado automáticamente en pantalla
            webbrowser.open(f"file://{ruta_pdf_absoluta}")

        except Exception as e:
            messagebox.showerror(
                "Error en generación automatizada",
                f"Se guardó el HTML pero falló el motor de PDF automático:\n{e}\n\nAbriendo HTML de respaldo.",
            )
            webbrowser.open(f"file://{os.path.abspath(ruta_html)}")

        # Limpieza estándar del formulario
        entry_canje.delete(0, tk.END)
        entry_para.delete(0, tk.END)
        var_tiene_vence.set(False)
        conmutar_vencimiento()
        actualizar_proximo_numero()
        actualizar_tabla()


def conmutar_vencimiento():
    if var_tiene_vence.get():
        lbl_sin_vence.grid_remove()
        entry_vence.grid(row=4, column=1, sticky=tk.W, pady=5)
        entry_vence.config(state="readonly")
    else:
        entry_vence.grid_remove()
        lbl_sin_vence.grid(row=4, column=1, sticky=tk.W, pady=5)


def actualizar_texto_boton_canje(event):
    seleccion = tabla.selection()
    if not seleccion:
        btn_canje.config(text="MARCAR COMO CANJEADO")
        return

    valores = tabla.item(seleccion, "values")
    estado_actual = valores[4]

    if "🔴" in estado_actual:
        btn_canje.config(text="REVERTIR A ACTIVO 🟢")
    else:
        btn_canje.config(text="MARCAR COMO CANJEADO 🔴")


def marcar_como_canjeado():
    seleccion = tabla.selection()
    if not seleccion:
        messagebox.showwarning(
            "Selección vacía", "Por favor, seleccioná un cupón del historial."
        )
        return

    valores = tabla.item(seleccion, "values")
    codigo_cupon = valores[0]

    exito, fue_canjeado = modificar_estado_canje(codigo_cupon)

    if exito:
        if fue_canjeado:
            messagebox.showinfo(
                "Éxito", f"Cupón N° {codigo_cupon} marcado como CANJEADO 🔴."
            )
        else:
            messagebox.showinfo(
                "Éxito", f"Cupón N° {codigo_cupon} revertido a ACTIVO 🟢."
            )
        actualizar_tabla()


def abrir_cupon_seleccionado():
    seleccion = tabla.selection()
    if not seleccion:
        messagebox.showwarning(
            "Selección vacía", "Por favor, seleccioná un cupón para abrir."
        )
        return

    valores = tabla.item(seleccion, "values")
    codigo_seleccionado = valores[0]

    # Modificado para abrir el PDF si existe, o el HTML como respaldo
    ruta_pdf = os.path.join("cupones-pdf", f"cupon_{codigo_seleccionado}.pdf")
    ruta_html = os.path.join("cupones-html", f"cupon_{codigo_seleccionado}.html")

    if os.path.exists(ruta_pdf):
        webbrowser.open(f"file://{os.path.abspath(ruta_pdf)}")
    elif os.path.exists(ruta_html):
        webbrowser.open(f"file://{os.path.abspath(ruta_html)}")
    else:
        messagebox.showerror(
            "Archivo no encontrado",
            "No se encontró el archivo del cupón seleccionado.",
        )


def actualizar_proximo_numero():
    lbl_proximo_num.config(text=str(obtener_siguiente_numero()).zfill(4))


def actualizar_tabla():
    for fila in tabla.get_children():
        tabla.delete(fila)
    for c in reversed(cargar_todos_los_cupones()):
        estado = "🔴 CANJEADO" if c["canjeado"] else "🟢 ACTIVO"
        vencimiento = c.get("fecha_vencimiento", "Sin vencimiento")
        tabla.insert(
            "",
            tk.END,
            values=(c["codigo"], c["para"], c["canje_por"], vencimiento, estado),
        )
    btn_canje.config(text="MARCAR COMO CANJEADO")


# --- VENTANA PRINCIPAL ---
root = tk.Tk()
root.title("Gestión de Cupones - La Casa Varietal")

ancho_ventana = 720
alto_ventana = 680

ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()

x = (ancho_pantalla // 2) - (ancho_ventana // 2)
y = (alto_pantalla // 2) - (alto_ventana // 2)

root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

style = ttk.Style()
style.theme_use("clam")

frame_form = ttk.LabelFrame(root, text=" Emisión ", padding="10")
frame_form.pack(fill=tk.X, padx=20, pady=10)

ttk.Label(frame_form, text="Próximo N°:").grid(row=0, column=0, sticky=tk.W)
lbl_proximo_num = ttk.Label(frame_form, text="", font=("Arial", 10, "bold"))
lbl_proximo_num.grid(row=0, column=1, sticky=tk.W)

ttk.Label(frame_form, text="Canjeable por:").grid(
    row=1, column=0, sticky=tk.W, pady=5
)
entry_canje = ttk.Entry(frame_form, width=40)
entry_canje.grid(row=1, column=1, pady=5)

ttk.Label(frame_form, text="Para:").grid(row=2, column=0, sticky=tk.W, pady=5)
entry_para = ttk.Entry(frame_form, width=40)
entry_para.grid(row=2, column=1, pady=5)

ttk.Label(frame_form, text="¿Tiene Vencimiento?:").grid(
    row=3, column=0, sticky=tk.W, pady=5
)

var_tiene_vence = tk.BooleanVar(value=False)
check_vence = ttk.Checkbutton(
    frame_form, variable=var_tiene_vence, command=conmutar_vencimiento
)
check_vence.grid(row=3, column=1, sticky=tk.W, pady=5)

entry_vence = DateEntry(
    frame_form,
    width=19,
    background="darkblue",
    foreground="white",
    borderwidth=2,
    date_pattern="dd/mm/yyyy",
)

lbl_sin_vence = ttk.Label(
    frame_form,
    text="Sin vencimiento",
    font=("Arial", 10, "italic"),
    foreground="black",
)

entry_vence.grid_remove()
lbl_sin_vence.grid(row=4, column=1, sticky=tk.W, pady=5)

btn_gen = ttk.Button(
    frame_form, text="GENERAR Y ABRIR CUPÓN", command=procesar_formulario
)
btn_gen.grid(row=5, column=0, columnspan=2, pady=15)

# Historial / Tabla
frame_hist = ttk.LabelFrame(root, text=" Historial ", padding="10")
frame_hist.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

columnas = ("id", "para", "canje", "vence", "estado")
tabla = ttk.Treeview(frame_hist, columns=columnas, show="headings")
tabla.heading("id", text="N°")
tabla.heading("para", text="Para")
tabla.heading("canje", text="Canje por")
tabla.heading("vence", text="Vencimiento")
tabla.heading("estado", text="Estado")

tabla.column("id", width=50, anchor=tk.CENTER)
tabla.column("para", width=130)
tabla.column("canje", width=180)
tabla.column("vence", width=110, anchor=tk.CENTER)
tabla.column("estado", width=100, anchor=tk.CENTER)
tabla.pack(fill=tk.BOTH, expand=True)

tabla.bind("<<TreeviewSelect>>", actualizar_texto_boton_canje)

# Contenedor inferior para los botones de acción en paralelo
frame_botones = ttk.Frame(root)
frame_botones.pack(pady=15)

btn_canje = ttk.Button(
    frame_botones, text="MARCAR COMO CANJEADO", command=marcar_como_canjeado
)
btn_canje.grid(row=0, column=0, padx=10)

btn_abrir = ttk.Button(
    frame_botones, text="ABRIR CUPÓN SELECCIONADO", command=abrir_cupon_seleccionado
)
btn_abrir.grid(row=0, column=1, padx=10)

actualizar_proximo_numero()
actualizar_tabla()
root.mainloop()