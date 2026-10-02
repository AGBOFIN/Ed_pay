"""
Thème visuel moderne pour l'application EduPaie.
Fournit une feuille de style QSS élégante, professionnelle et adaptée
à une utilisation quotidienne dans un établissement scolaire.
"""

MODERN_STYLE = """
/* ========================================================================= */
/* Global Application Styles                                                 */
/* ========================================================================= */
QWidget {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
    color: #1E293B;
    background-color: #F8FAFC;
}

QMainWindow {
    background-color: #F1F5F9;
}

/* ========================================================================= */
/* Menu Bar                                                                  */
/* ========================================================================= */
QMenuBar {
    background-color: #FFFFFF;
    color: #334155;
    border-bottom: 1px solid #E2E8F0;
    padding: 2px 6px;
    font-weight: 500;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
    margin: 2px;
}

QMenuBar::item:selected {
    background-color: #EFF6FF;
    color: #1D4ED8;
}

QMenu {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
    color: #1E293B;
}

QMenu::item:selected {
    background-color: #2563EB;
    color: #FFFFFF;
}

QMenu::separator {
    height: 1px;
    background: #E2E8F0;
    margin: 4px 6px;
}

/* ========================================================================= */
/* ToolBar / Top Navigation                                                  */
/* ========================================================================= */
QToolBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 6px 12px;
    spacing: 8px;
}

QToolButton {
    background-color: #F8FAFC;
    color: #334155;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
    font-size: 13px;
}

QToolButton:hover {
    background-color: #EFF6FF;
    color: #1D4ED8;
    border-color: #BFDBFE;
}

QToolButton:checked {
    background-color: #2563EB;
    color: #FFFFFF;
    border-color: #1D4ED8;
}

/* ========================================================================= */
/* Status Bar                                                                */
/* ========================================================================= */
QStatusBar {
    background-color: #FFFFFF;
    color: #64748B;
    border-top: 1px solid #E2E8F0;
    font-size: 12px;
    padding: 4px 8px;
}

/* ========================================================================= */
/* Form Controls (Inputs, Combos, SpinBoxes)                                 */
/* ========================================================================= */
QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 13px;
    color: #0F172A;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
    border: 2px solid #2563EB;
    background-color: #FFFFFF;
}

QLineEdit:hover, QSpinBox:hover, QDateEdit:hover, QComboBox:hover {
    border-color: #94A3B8;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #E2E8F0;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    background-color: #F8FAFC;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    selection-background-color: #EFF6FF;
    selection-color: #1D4ED8;
    padding: 4px;
}

/* ========================================================================= */
/* Push Buttons                                                              */
/* ========================================================================= */
QPushButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #1D4ED8;
}

QPushButton:pressed {
    background-color: #1E40AF;
}

QPushButton:disabled {
    background-color: #E2E8F0;
    color: #94A3B8;
}

/* Special Button Variants via objectName or property */
QPushButton[variant="secondary"] {
    background-color: #FFFFFF;
    color: #334155;
    border: 1px solid #CBD5E1;
}

QPushButton[variant="secondary"]:hover {
    background-color: #F1F5F9;
    color: #0F172A;
    border-color: #94A3B8;
}

QPushButton[variant="success"] {
    background-color: #059669;
    color: #FFFFFF;
}

QPushButton[variant="success"]:hover {
    background-color: #047857;
}

QPushButton[variant="danger"] {
    background-color: #DC2626;
    color: #FFFFFF;
}

QPushButton[variant="danger"]:hover {
    background-color: #B91C1C;
}

/* ========================================================================= */
/* Tables and Views                                                          */
/* ========================================================================= */
QTableWidget, QTableView {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #F1F5F9;
    selection-background-color: #DBEAFE;
    selection-color: #1E3A8A;
    outline: none;
}

QTableWidget::item, QTableView::item {
    padding: 8px 10px;
    border-bottom: 1px solid #F1F5F9;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #DBEAFE;
    color: #1E3A8A;
    font-weight: 500;
}

QHeaderView::section {
    background-color: #F8FAFC;
    color: #475569;
    font-weight: 700;
    font-size: 12px;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
    border-right: 1px solid #F1F5F9;
    text-transform: uppercase;
}

QHeaderView::section:hover {
    background-color: #F1F5F9;
    color: #1E293B;
}

/* ========================================================================= */
/* ScrollBars                                                                */
/* ========================================================================= */
QScrollBar:vertical {
    border: none;
    background: #F1F5F9;
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #F1F5F9;
    height: 8px;
    border-radius: 4px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #CBD5E1;
    min-width: 25px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background: #94A3B8;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ========================================================================= */
/* Dialogs and Popups                                                        */
/* ========================================================================= */
QDialog {
    background-color: #FFFFFF;
}

QDialogButtonBox QPushButton {
    min-width: 80px;
}

/* ========================================================================= */
/* GroupBoxes and Frames                                                     */
/* ========================================================================= */
QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    margin-top: 24px;
    padding: 16px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #2563EB;
}
"""


def apply_theme(app):
    """Applique le thème moderne à l'application Qt."""
    app.setStyleSheet(MODERN_STYLE)
