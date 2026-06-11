# Generador de Cupones - La Casa Varietal

## Descripción General

Este proyecto es un software de escritorio nativo, ligero y automatizado diseñado para la emisión, control y exportación a PDF de tarjetas de regalo y cupones de cambio para el local *La Casa Varietal*. Utiliza una arquitectura desacoplada en Python que separa de forma limpia la interfaz gráfica, la persistencia de datos y la capa de diseño mediante plantillas HTML5 dinámicas y gráficos vectoriales nativos.

---

## Características Principales

* **Emisión Rápida:** Formulario intuitivo para registrar el motivo del canje, beneficiario y fecha de vencimiento con selector de almanaque integrado.
* **Numeración Automatizada:** Autoincremento correlativo de los números de cupón (`0001`, `0002`, etc.) sincronizado en tiempo real.
* **Conversión Automática a PDF:** Generación en segundo plano de archivos PDF con las medidas exactas de diseño comercial usando un motor invisible (*Playwright Chromium*), reduciendo la intervención manual.
* **Historial en Tiempo Real:** Tabla interactiva (`Treeview`) para visualizar el estado y vencimiento de todos los cupones emitidos.
* **Acciones de Control Dinámicas:** Botón de acción con lógica de *Toggle* para marcar como "Canjeado" o "Revertir a Activo". El texto del botón muta dinámicamente según la fila seleccionada.
* **Persistencia Local:** Base de datos ligera en formato JSON (`cupones.json`) que no requiere de servidores externos.

## Estructura del Proyecto

```text
Cuponera/
├── main.py                 # Código fuente principal de la aplicación
├── index.html              # Plantilla de diseño y maquetación visual
├── lacasavarietal-logo.svg # Isotipo vectorial original de la marca
├── .gitignore              # Filtro de exclusión para el control de versiones
└── README.md               # Documentación técnica del sistema
```

## Arquitectura del Diseño

El diseño visual del cupón se maneja de forma totalmente desacoplada de la lógica de Python para facilitar su mantenimiento:

* **Plantilla Base:** Archivo `index.html` que funciona como la maqueta CSS (tipografías Serif, proporciones de caja, alineaciones y datos estáticos comerciales).
* **Gráficos Vectoriales:** Isotipo `lacasavarietal-logo.svg` inyectado de forma *inline* en el documento para garantizar la máxima nitidez de impresión en el PDF resultante.

## Tecnologías Utilizadas

* **Python 3.x** y **Tkinter / TTK** para la interfaz gráfica de escritorio.
* **Tkcalendar** para el manejo dinámico de fechas de vencimiento.
* **Playwright (Chromium Headless Shell)** como motor de renderizado invisible de HTML a PDF.
* **JSON** para el almacenamiento y persistencia de datos locales.

## Requisitos Previos

* **Python 3.10+** instalado en el sistema.
* **Conexión a internet** (únicamente para la descarga inicial de los binarios del navegador).

## Instalación y Configuración

Si querés clonar este repositorio y ejecutarlo en modo desarrollo, seguí estos pasos en tu terminal:

1. **Cloná el repositorio:**
   ```bash
   git clone <url_repositorio>
   cd carpeta_raiz
2. **Instala las dependencias requeridas:**
   ```bash
   pip install -r requirements.txt
3. **Descargá los binarios del navegador invisible:**
   ```bash
   python -m playwright install chromium
4. **Ejecutá la aplicación:**
   ```bash
   python main.py