# Widget Sidebar

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

> **Gestor avanzado de portapapeles para Windows** - Acceso instantáneo a tus comandos favoritos con un simple click

---

## 📖 Índice

- [¿Qué es Widget Sidebar?](#-qué-es-widget-sidebar)
- [Características Principales](#-características-principales)
- [Descarga e Instalación](#-descarga-e-instalación)
- [Inicio Rápido](#-inicio-rápido)
- [Documentación](#-documentación)
- [Screenshots](#-screenshots)
- [Tecnologías](#-tecnologías)
- [Desarrollo](#-desarrollo)
- [Licencia](#-licencia)

---

## 🎯 ¿Qué es Widget Sidebar?

**Widget Sidebar** es una aplicación de escritorio para Windows que te permite:

- ✅ **Acceder instantáneamente** a tus comandos favoritos (Git, Docker, Python, etc.)
- ✅ **Copiar al portapapeles** con un solo click
- ✅ **Buscar comandos** en tiempo real con filtrado inteligente
- ✅ **Personalizar completamente** categorías e items
- ✅ **Controlar con hotkeys globales** desde cualquier aplicación
- ✅ **Exportar/Importar** configuración para compartir o hacer backup

**Perfect para:** Desarrolladores, DevOps, Sysadmins, y cualquiera que use comandos frecuentemente.

---

## ✨ Características Principales

### 🎨 Interfaz Intuitiva

- **Sidebar persistente** → Siempre visible en el borde derecho
- **Panel expandible** → Se expande al seleccionar categoría
- **Animaciones suaves** → Transiciones fluidas de 250ms
- **Dark theme** → Diseño profesional que no cansa la vista
- **Draggable** → Arrastra y posiciona donde prefieras

### ⚡ Productividad

- **8 categorías predefinidas** → Git, CMD, Docker, Python, NPM, URLs, Snippets, Config
- **86+ comandos útiles** → Listos para usar inmediatamente
- **Copy-on-click** → Click en comando = copiado al portapapeles
- **Feedback visual** → Flash azul confirma la copia
- **Búsqueda en tiempo real** → Encuentra comandos al instante

### ⌨️ Hotkeys Globales

- `Ctrl+Shift+V` → Mostrar/ocultar widget desde cualquier app
- `Ctrl+Shift+1-9` → Acceso directo a categorías (próximamente)

### 🔧 Configuración Completa

- **Editor de categorías** → Crea, edita y elimina categorías
- **Editor de items** → Gestiona comandos con validación
- **Apariencia** → Personaliza tema, opacidad, dimensiones, animaciones
- **Hotkeys** → Visualiza y configura atajos de teclado
- **Export/Import** → Backup y restauración de configuración

### 🎛️ System Tray

- **Minimiza a tray** → No cierra la app, siempre accesible
- **Menú contextual** → Mostrar/Ocultar, Configuración, Salir
- **Notificaciones** → Mensajes informativos cuando es necesario

---

## 📥 Descarga e Instalación

### Opción 1: Ejecutable Portable (Recomendado)

**✅ No requiere Python ni dependencias**

1. Descarga `WidgetSidebar.exe` desde [Releases](dist/WidgetSidebar.exe)
2. Coloca el ejecutable en cualquier carpeta
3. Ejecuta `WidgetSidebar.exe`
4. ¡Listo! 🎉

**Tamaño:** ~15-20 MB
**Sistema:** Windows 10/11

### Opción 2: Desde Código Fuente

**Requiere Python 3.10+**

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/widget-sidebar.git
cd widget-sidebar

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

---

## 🚀 Inicio Rápido

### 1. Primera Ejecución

Al iniciar, el widget aparece en el **borde derecho** de tu pantalla:

```
┌────────┐
│   WS   │
├────────┤
│  Git   │  ← Click aquí
├────────┤
│  CMD   │
├────────┤
│ Docker │
└────────┘
```

### 2. Usar un Comando

1. **Click en categoría** (ej: Git)
2. **Panel se expande** →
   ```
   ┌─────────────────────────────┐
   │  Git                        │
   ├─────────────────────────────┤
   │  🔍 Buscar items...         │
   ├─────────────────────────────┤
   │  git status                 │ ← Click aquí
   │  git add .                  │
   │  git commit -m ""           │
   └─────────────────────────────┘
   ```
3. **Click en comando**
4. **Comando copiado** → Flash azul confirma
5. **Pega donde necesites** → `Ctrl+V`

### 3. Buscar un Comando

1. Abre categoría
2. Escribe en SearchBar: `"commit"`
3. Lista filtrada al instante
4. Click en resultado

### 4. Hotkey Global

- Presiona `Ctrl+Shift+V` desde **cualquier aplicación**
- Widget se muestra/oculta instantáneamente
- No necesitas alt-tab

### 5. Configuración

1. Click en botón **⚙** (parte inferior)
2. Ventana de configuración se abre
3. **4 tabs** disponibles:
   - Categorías → Gestiona categorías e items
   - Apariencia → Personaliza look & feel
   - Hotkeys → Configura atajos
   - General → Opciones y export/import
4. Haz cambios
5. Click **"Guardar"**

---

## 📚 Documentación

- **[Guía de Usuario Completa](USER_GUIDE.md)** → Tutorial paso a paso con screenshots
- **[Phase 5 Summary](PHASE5_SUMMARY.md)** → Documentación técnica de configuración
- **[Phase 4 Summary](PHASE4_SUMMARY.md)** → Hotkeys y system tray
- **[Phase 3 Summary](PHASE3_SUMMARY.md)** → Arquitectura de UI

### Contenido de la Guía de Usuario

- ✅ Instalación detallada
- ✅ Tutorial completo de uso
- ✅ Explicación de 8 categorías predefinidas
- ✅ Búsqueda avanzada
- ✅ Configuración paso a paso
- ✅ Personalización de categorías e items
- ✅ Export/Import de configuración
- ✅ Tips y trucos
- ✅ Troubleshooting

**[→ Leer Guía Completa](USER_GUIDE.md)**

---

## 📸 Screenshots

### Sidebar y Panel

```
┌────────┬─────────────────────────────┐
│   WS   │  Git                        │
├────────┼─────────────────────────────┤
│ >Git   │  🔍 Buscar...               │
├────────┼─────────────────────────────┤
│  CMD   │  ✓ git status               │ ← Item activo
├────────┤  git add .                  │
│ Docker │  git commit -m ""           │
├────────┤  git push                   │
│ Python │  git pull                   │
└────────┴─────────────────────────────┘
```

### Ventana de Configuración

```
┌────────────────────────────────────────┐
│  Configuración                    [×]  │
├────────────────────────────────────────┤
│ [Categorías] [Apariencia] [Hotkeys] [General]
│                                        │
│  Categorías         Items              │
│  ┌──────────┐      ┌────────────────┐ │
│  │ Git (14) │      │ git status     │ │
│  │ CMD (13) │      │ git add .      │ │
│  │ Docker…  │      │ git commit     │ │
│  └──────────┘      └────────────────┘ │
│  [+] [-]           [+] [✎] [-]        │
│                                        │
│           [Cancelar] [Aplicar] [Guardar]
└────────────────────────────────────────┘
```

---

## 🛠️ Tecnologías

### Core

- **Python 3.10+** → Lenguaje de programación
- **PyQt6** → Framework de interfaz gráfica
- **PyInstaller** → Compilador a ejecutable standalone

### Librerías

- **pyperclip** → Gestión de portapapeles
- **pynput** → Captura de hotkeys globales

### Arquitectura

- **MVC Pattern** → Model-View-Controller
- **Signal/Slot** → Comunicación entre componentes
- **JSON Config** → Persistencia de datos

---

## 💻 Desarrollo

### Requisitos

- Python 3.10+
- pip

### Setup

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py

# Ejecutar tests
python test_phase5.py
```

### Compilar Ejecutable

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar con build.bat
build.bat

# Resultado en dist/WidgetSidebar.exe
```

### Estructura del Proyecto

```
widget_sidebar/
├── main.py                      # Entry point
├── config.json                  # User configuration
├── default_categories.json      # Default categories & items
├── requirements.txt             # Python dependencies
├── widget_sidebar.spec          # PyInstaller config
├── build.bat                    # Build script
├── USER_GUIDE.md               # User documentation
├── README.md                    # This file
├── src/
│   ├── models/                 # Data models
│   │   ├── category.py
│   │   ├── item.py
│   │   └── config.py
│   ├── views/                  # UI components
│   │   ├── main_window.py
│   │   ├── sidebar.py
│   │   ├── content_panel.py
│   │   ├── settings_window.py
│   │   └── widgets/
│   ├── controllers/            # Business logic
│   │   ├── main_controller.py
│   │   └── clipboard_controller.py
│   └── core/                   # Core functionality
│       ├── config_manager.py
│       ├── clipboard_manager.py
│       ├── hotkey_manager.py
│       ├── tray_manager.py
│       └── search_engine.py
└── tests/
    ├── test_phase3.py
    ├── test_phase4.py
    └── test_phase5.py
```

### Roadmap

**Version 3.0.0** (Actual) ✅
- Settings window con editor completo
- Export/Import de configuración

**Version 3.1.0** (Próximamente)
- Hotkey capture dialog
- Tema Light mode
- Categorías numeradas (Ctrl+Shift+1-9)

**Version 3.2.0** (Futuro)
- Auto-start con Windows
- Historial de clipboard
- Drag & drop items
- Cloud sync

---

## 🤝 Contribuir

¡Contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guidelines

- Código Python PEP 8 compliant
- Commits descriptivos
- Tests para nuevas features
- Documentación actualizada

---

## 📝 Changelog

### Version 3.0.0 (2025-10-15)

**Phase 5 - Settings & Configuration**
- ✅ Settings window completa (4 tabs)
- ✅ Category/Item editor con CRUD
- ✅ Appearance settings (theme, opacity, dimensions)
- ✅ Hotkey settings (visualization)
- ✅ General settings (behavior, export/import)

### Version 2.0.0 (2025-10-14)

**Phase 4 - Hotkeys, Tray & Search**
- ✅ Global hotkey Ctrl+Shift+V
- ✅ System tray integration
- ✅ SearchBar con debouncing
- ✅ Search engine

### Version 1.0.0 (2025-10-13)

**Phase 3 - UI Complete**
- ✅ Sidebar con categorías
- ✅ Expandable content panel
- ✅ Dark theme
- ✅ Animaciones

---

## 📄 Licencia

MIT License

Copyright (c) 2025 Widget Sidebar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 💬 Soporte

¿Tienes preguntas o problemas?

- 📖 **[Guía de Usuario](USER_GUIDE.md)** → Instrucciones detalladas
- 🐛 **[GitHub Issues](https://github.com/tu-usuario/widget-sidebar/issues)** → Reporta bugs
- 💡 **[GitHub Discussions](https://github.com/tu-usuario/widget-sidebar/discussions)** → Ideas y sugerencias

---

## ⭐ ¿Te gusta el proyecto?

Si encuentras útil Widget Sidebar, considera:

- ⭐ Dar una estrella al repositorio
- 🐦 Compartir en redes sociales
- 🤝 Contribuir con código o documentación
- ☕ [Buy me a coffee](https://www.buymeacoffee.com/yourusername)

---

**Made with ❤️ by [Tu Nombre]**

*Widget Sidebar - Tu productividad en un click*
