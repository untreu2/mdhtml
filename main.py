import sys
import json
import markdown
import tempfile
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTextEdit, QWidget, QVBoxLayout,
    QHBoxLayout, QFormLayout, QPushButton, QComboBox, QColorDialog, QLabel, QFileDialog, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView

# HTML template
HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>mdhtml</title>
  <link href="https://fonts.googleapis.com/css2?family={font_family}:wght@300;400;700&display=swap" rel="stylesheet">
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      font-family: '{font_family}', monospace;
      background-color: {bg_color};
      color: {text_color};
      line-height: 1.6;
    }}
    body {{ padding: 40px; }}
    h1, h2, h3, h4, h5, h6 {{
      color: {text_color};
      margin-top: 20px;
      margin-bottom: 10px;
      text-align: center;
    }}
    p {{ margin: 15px 0; font-size: 1.1em; }}
    a {{
      color: #83a598;
      text-decoration: none;
    }}
    a:hover {{ text-decoration: underline; }}
    img {{
      max-width: 100%;
      height: auto;
      display: block;
      margin: 20px auto;
    }}
    blockquote {{
      border-left: 4px solid #83a598;
      margin: 20px 0;
      padding: 10px 20px;
      background-color: #3c3836;
      color: #d5c4a1;
      font-style: italic;
    }}
    code {{
      background-color: #3c3836;
      padding: 3px 6px;
      border-radius: 4px;
      font-family: '{font_family}', monospace;
    }}
    pre {{
      background-color: #3c3836;
      padding: 15px;
      border-radius: 8px;
      overflow-x: auto;
    }}
    {center_css}
    @media (max-width: 600px) {{
      body {{ padding: 20px; }}
    }}
  </style>
</head>
<body>
  {content}
</body>
</html>"""

class SettingsPanel(QWidget):
    """
    SettingsPanel class creates the side panel for various configuration options,
    including background color, text color, font selection, centering option, and
    file save/load operations.
    """
    # Define signals to notify when settings are changed or actions are triggered.
    settingsChanged = pyqtSignal()
    saveMarkdown = pyqtSignal()
    saveHtml = pyqtSignal()
    saveConfig = pyqtSignal()
    loadConfig = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Default settings
        self.default_bg_color = "#282828"
        self.default_text_color = "#ebdbb2"
        self.default_font = "roboto+mono"

        # Initialize current settings with default values.
        self.bg_color = self.default_bg_color
        self.text_color = self.default_text_color
        self.font_family = self.default_font
        self.center = True

        self.init_ui()

    def init_ui(self):
        """Initializes the user interface of the settings panel."""
        layout = QFormLayout()

        # Button to select background color
        self.bg_color_button = QPushButton(self.bg_color)
        self.bg_color_button.clicked.connect(self.select_bg_color)
        layout.addRow("Background Color:", self.bg_color_button)

        # Button to select text color
        self.text_color_button = QPushButton(self.text_color)
        self.text_color_button.clicked.connect(self.select_text_color)
        layout.addRow("Text Color:", self.text_color_button)

        # Font selection drop-down
        self.font_combo = QComboBox()
        fonts = [
            "roboto+mono", "arial", "times+new+roman", "courier+new", "verdana",
            "open+sans", "lato", "montserrat", "oswald", "source+code+pro",
            "fira+code", "pt+mono", "droid+sans+mono"
        ]
        self.font_combo.addItems(fonts)
        self.font_combo.setCurrentText(self.font_family)
        self.font_combo.currentIndexChanged.connect(self.on_font_changed)
        layout.addRow("Font:", self.font_combo)

        # Checkbox for centering the content on desktop.
        self.center_checkbox = QCheckBox("Center on Desktop")
        self.center_checkbox.setChecked(True)
        self.center_checkbox.stateChanged.connect(self.on_center_changed)
        layout.addRow(self.center_checkbox)

        # Button to save Markdown content to a file
        self.save_markdown_button = QPushButton("Save Markdown")
        self.save_markdown_button.clicked.connect(lambda: self.saveMarkdown.emit())
        layout.addRow(self.save_markdown_button)

        # Button to save HTML content to a file
        self.save_html_button = QPushButton("Save HTML")
        self.save_html_button.clicked.connect(lambda: self.saveHtml.emit())
        layout.addRow(self.save_html_button)

        # Button to save the current configuration settings
        self.save_config_button = QPushButton("Save Config")
        self.save_config_button.clicked.connect(lambda: self.saveConfig.emit())
        layout.addRow(self.save_config_button)

        # Button to load configuration settings from a file
        self.load_config_button = QPushButton("Load Config")
        self.load_config_button.clicked.connect(lambda: self.loadConfig.emit())
        layout.addRow(self.load_config_button)

        # Button to reset all settings to their default values
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self.reset_to_default)
        layout.addRow(self.reset_button)

        self.setLayout(layout)

    def select_bg_color(self):
        """Opens a color dialog to select a new background color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = color.name()
            self.bg_color_button.setText(self.bg_color)
            self.settingsChanged.emit()

    def select_text_color(self):
        """Opens a color dialog to select a new text color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color.name()
            self.text_color_button.setText(self.text_color)
            self.settingsChanged.emit()

    def on_font_changed(self):
        """Updates the font family when the user selects a different font."""
        self.font_family = self.font_combo.currentText()
        self.settingsChanged.emit()

    def on_center_changed(self, state):
        """Updates the centering option based on the checkbox state."""
        self.center = (state == Qt.Checked)
        self.settingsChanged.emit()

    def reset_to_default(self):
        """Resets settings to their default values."""
        self.bg_color = self.default_bg_color
        self.text_color = self.default_text_color
        self.font_family = self.default_font
        self.center = True  # Default: center enabled
        self.bg_color_button.setText(self.bg_color)
        self.text_color_button.setText(self.text_color)
        self.font_combo.setCurrentText(self.font_family)
        self.center_checkbox.setChecked(True)
        self.settingsChanged.emit()

    def get_settings(self):
        """Returns a dictionary of the current settings."""
        return {
            "bg_color": self.bg_color,
            "text_color": self.text_color,
            "font_family": self.font_family,
            "center": self.center
        }

    def apply_config(self, config):
        """
        Applies configuration settings from a given dictionary to the interface.

        Args:
            config (dict): A dictionary containing configuration keys.
        """
        if "bg_color" in config:
            self.bg_color = config["bg_color"]
            self.bg_color_button.setText(self.bg_color)
        if "text_color" in config:
            self.text_color = config["text_color"]
            self.text_color_button.setText(self.text_color)
        if "font_family" in config:
            self.font_family = config["font_family"]
            # Add the font to the combo box if not already present.
            if self.font_combo.findText(self.font_family) == -1:
                self.font_combo.addItem(self.font_family)
            self.font_combo.setCurrentText(self.font_family)
        if "center" in config:
            self.center = config["center"]
            self.center_checkbox.setChecked(self.center)
        self.settingsChanged.emit()

class MainWindow(QMainWindow):
    """
    MainWindow is the central window of the application, containing a three-pane layout:
    - Left: Settings panel
    - Center: Markdown editor with zoom controls
    - Right: HTML preview pane with an option to open in the browser
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mdhtml")
        self.resize(1200, 700)

        # Global style sheet for the application
        self.setStyleSheet("""
            QWidget {
                background-color: #3c3836;
                color: #ebdbb2;
                font-family: 'Segoe UI', sans-serif;
            }
            QMainWindow {
                background-color: #3c3836;
            }
            QPushButton {
                background-color: #504945;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                color: #ebdbb2;
            }
            QPushButton:hover {
                background-color: #665c54;
            }
            QPushButton:pressed {
                background-color: #7c6f64;
            }
            /* Additional widget styles */
            QComboBox {
                background-color: #282828;
                border: 1px solid #504945;
                border-radius: 4px;
                padding: 2px 4px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QLabel {
                font-weight: bold;
            }
            QFormLayout {
                margin: 10px;
            }
        """)

        # Default font size for the Markdown editor
        self.markdown_font_size = 12

        # Create a splitter for a three-pane layout:
        # Left: Settings panel; Center: Markdown editor; Right: HTML preview
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Settings Panel
        self.settings_panel = SettingsPanel()
        self.settings_panel.settingsChanged.connect(self.update_html)
        self.settings_panel.saveMarkdown.connect(self.save_markdown)
        self.settings_panel.saveHtml.connect(self.save_html)
        self.settings_panel.saveConfig.connect(self.save_config)
        self.settings_panel.loadConfig.connect(self.load_config)

        # Center panel: Markdown editing area
        self.markdown_edit = QTextEdit()
        self.markdown_edit.setPlaceholderText("Write your Markdown content here...")
        self.markdown_edit.setFont(QFont("Courier", self.markdown_font_size))
        self.markdown_edit.textChanged.connect(self.update_html)
        self.markdown_edit.setStyleSheet("background-color: black; color: white;")

        zoom_in_button = QPushButton("Zoom In")
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_out_button = QPushButton("Zoom Out")
        zoom_out_button.clicked.connect(self.zoom_out)

        markdown_container = QWidget()
        markdown_layout = QVBoxLayout()
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(zoom_in_button)
        zoom_layout.addWidget(zoom_out_button)
        zoom_layout.addStretch()
        markdown_layout.addLayout(zoom_layout)
        markdown_layout.addWidget(self.markdown_edit)
        markdown_container.setLayout(markdown_layout)

        # HTML preview
        self.html_view = QWebEngineView()
        open_browser_button = QPushButton("Open in Browser")
        open_browser_button.clicked.connect(self.open_in_browser)

        html_container = QWidget()
        html_layout = QVBoxLayout()
        html_layout.addWidget(open_browser_button)
        html_layout.addWidget(self.html_view)
        html_container.setLayout(html_layout)

        # Add the three panels to the splitter.
        splitter.addWidget(self.settings_panel)
        splitter.addWidget(markdown_container)
        splitter.addWidget(html_container)

        # Set initial sizes for the three panels.
        splitter.setSizes([200, 300, 500])

        # Set the central widget of the main window.
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Generate the initial HTML preview.
        self.update_html()

    def update_html(self):
        """
        Converts the Markdown text to HTML, fills the HTML template with the current settings,
        and loads it into the HTML preview pane.
        """
        # Get the Markdown content from the editor.
        md_text = self.markdown_edit.toPlainText()
        # Convert Markdown to HTML using the markdown library with code extensions.
        html_content = markdown.markdown(md_text, extensions=['fenced_code', 'codehilite'])
        # Retrieve current settings from the settings panel.
        settings = self.settings_panel.get_settings()

        # If "Center on Desktop" is enabled, add extra CSS for centering the content.
        if settings.get("center"):
            center_css = """
            @media (min-width: 1024px) {
                body {
                    max-width: 800px;
                    margin: 0 auto;
                }
            }
            """
        else:
            center_css = ""

        # Fill the HTML template with the current settings and generated HTML content.
        full_html = HTML_TEMPLATE.format(
            content=html_content,
            bg_color=settings["bg_color"],
            text_color=settings["text_color"],
            font_family=settings["font_family"],
            center_css=center_css
        )
        # Load the HTML into the preview panel.
        self.html_view.setHtml(full_html)

    def zoom_in(self):
        """Increases the font size of the Markdown editor."""
        self.markdown_font_size += 1
        self.update_markdown_font()

    def zoom_out(self):
        """Decreases the font size of the Markdown editor."""
        if self.markdown_font_size > 1:
            self.markdown_font_size -= 1
            self.update_markdown_font()

    def update_markdown_font(self):
        """Applies the updated font size to the Markdown editor."""
        font = self.markdown_edit.font()
        font.setPointSize(self.markdown_font_size)
        self.markdown_edit.setFont(font)

    def save_markdown(self):
        """
        Saves the current Markdown content to a file.
        Opens a file dialog for the user to specify the save location.
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Save Markdown", "", "Markdown Files (*.md);;All Files (*)")
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.markdown_edit.toPlainText())

    def save_html(self):
        """
        Generates the HTML from the Markdown content and saves it to a file.
        Opens a file dialog for the user to specify the save location.
        """
        md_text = self.markdown_edit.toPlainText()
        html_content = markdown.markdown(md_text, extensions=['fenced_code', 'codehilite'])
        settings = self.settings_panel.get_settings()
        if settings.get("center"):
            center_css = """
            @media (min-width: 1024px) {
                body {
                    max-width: 800px;
                    margin: 0 auto;
                }
            }
            """
        else:
            center_css = ""
        full_html = HTML_TEMPLATE.format(
            content=html_content,
            bg_color=settings["bg_color"],
            text_color=settings["text_color"],
            font_family=settings["font_family"],
            center_css=center_css
        )
        filename, _ = QFileDialog.getSaveFileName(self, "Save HTML", "", "HTML Files (*.html);;All Files (*)")
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(full_html)

    def save_config(self):
        """
        Saves the current configuration settings to a JSON file.
        Opens a file dialog for the user to specify the save location.
        """
        config = self.settings_panel.get_settings()
        filename, _ = QFileDialog.getSaveFileName(self, "Save Config", "", "JSON Files (*.json);;All Files (*)")
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)

    def load_config(self):
        """
        Loads configuration settings from a JSON file.
        Opens a file dialog for the user to choose the configuration file.
        """
        filename, _ = QFileDialog.getOpenFileName(self, "Load Config", "", "JSON Files (*.json);;All Files (*)")
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.settings_panel.apply_config(config)
            except Exception as e:
                print("Error loading config:", e)

    def open_in_browser(self):
        """
        Writes the generated HTML content to a temporary file and opens it in the default web browser.
        """
        md_text = self.markdown_edit.toPlainText()
        html_content = markdown.markdown(md_text, extensions=['fenced_code', 'codehilite'])
        settings = self.settings_panel.get_settings()
        if settings.get("center"):
            center_css = """
            @media (min-width: 1024px) {
                body {
                    max-width: 800px;
                    margin: 0 auto;
                }
            }
            """
        else:
            center_css = ""
        full_html = HTML_TEMPLATE.format(
            content=html_content,
            bg_color=settings["bg_color"],
            text_color=settings["text_color"],
            font_family=settings["font_family"],
            center_css=center_css
        )
        # Create a temporary HTML file.
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as tmp_file:
            tmp_file.write(full_html)
            temp_path = tmp_file.name
        # Open the temporary file in the system's default web browser.
        webbrowser.open('file://' + temp_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
