import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QApplication, QFrame, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from billing_tabs.create_bill import CreateBillWindow
from billing_tabs.bill_history import BillHistoryWindow
from billing_tabs.inventory import InventoryWindow
from billing_tabs.admin_settings import AdminSettingsWindow
from billing_tabs.sales_report import SalesReportWindow
from billing_tabs.thermal_printer import ThermalPrinter

class HomeDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickBill - Home")
        # Set window size based on screen resolution or sensible default
        screen = QApplication.primaryScreen()
        screen_size = screen.size() if screen else None
        default_width, default_height = 1280, 720
        if screen_size and (screen_size.width() < default_width or screen_size.height() < default_height):
            self.resize(screen_size.width() * 0.95, screen_size.height() * 0.95)
        else:
            self.resize(default_width, default_height)
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Initialize child windows
        self.create_bill_window = None
        self.bill_history_window = None
        self.inventory_window = None
        self.sales_report_window = None
        self.admin_settings_window = None
        
        # Initialize printer instance
        self.printer = ThermalPrinter()
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)

        # Header
        header_label = QLabel("QuickBill")
        header_label.setFont(QFont("Poppins", 32, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)

        # Subtitle
        subtitle_label = QLabel("Offline Billing Solution with GST Support")
        subtitle_label.setFont(QFont("Poppins", 18))
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)

        # Add some space
        main_layout.addSpacing(40)

        # Buttons layout
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(20)

        # Create Bill Button
        create_bill_btn = QPushButton("📄 Create Bill")
        create_bill_btn.setFont(QFont("Poppins", 20, QFont.Bold))
        create_bill_btn.setMinimumHeight(100)
        create_bill_btn.clicked.connect(self.open_create_bill)
        create_bill_btn.setStyleSheet("background-color: #3498db; color: white; border: none; border-radius: 8px; padding: 20px;")
        buttons_layout.addWidget(create_bill_btn)

        # Bill History Button
        bill_history_btn = QPushButton("📋 Bill History")
        bill_history_btn.setFont(QFont("Poppins", 20, QFont.Bold))
        bill_history_btn.setMinimumHeight(100)
        bill_history_btn.clicked.connect(self.open_bill_history)
        bill_history_btn.setStyleSheet("background-color: #2ecc71; color: white; border: none; border-radius: 8px; padding: 20px;")
        buttons_layout.addWidget(bill_history_btn)

        # Inventory Button
        inventory_btn = QPushButton("📦 Inventory")
        inventory_btn.setFont(QFont("Poppins", 20, QFont.Bold))
        inventory_btn.setMinimumHeight(100)
        inventory_btn.clicked.connect(self.open_inventory)
        inventory_btn.setStyleSheet("background-color: #9b59b6; color: white; border: none; border-radius: 8px; padding: 20px;")
        buttons_layout.addWidget(inventory_btn)

        # Sales Report Button
        sales_report_btn = QPushButton("📊 Sales Report")
        sales_report_btn.setFont(QFont("Poppins", 20, QFont.Bold))
        sales_report_btn.setMinimumHeight(100)
        sales_report_btn.clicked.connect(self.open_sales_report)
        sales_report_btn.setStyleSheet("background-color: #f39c12; color: white; border: none; border-radius: 8px; padding: 20px;")
        buttons_layout.addWidget(sales_report_btn)

        # Settings Button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setFont(QFont("Poppins", 20, QFont.Bold))
        settings_btn.setMinimumHeight(100)
        settings_btn.clicked.connect(self.open_settings)
        settings_btn.setStyleSheet("background-color: #e74c3c; color: white; border: none; border-radius: 8px; padding: 20px;")
        buttons_layout.addWidget(settings_btn)

        # Add buttons to main layout
        main_layout.addLayout(buttons_layout)

        # Add stretch to push everything to top
        main_layout.addStretch()

        # Footer
        footer_label = QLabel("✓ GST Support  ✓ Thermal Printing  ✓ Barcode Scanning  ✓ Offline Database  ✓ Whatsapp bill sharing")
        footer_label.setFont(QFont("Poppins", 16))
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #95a5a6; padding: 20px;")
        main_layout.addWidget(footer_label)

        # Set main window background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }
        """)
    
    def showEvent(self, event):
        """Center the window on the screen when shown"""
        super().showEvent(event)
        frame_geom = self.frameGeometry()
        screen = QApplication.primaryScreen()
        center_point = screen.geometry().center()
        frame_geom.moveCenter(center_point)
        self.move(frame_geom.topLeft())
    
    def open_create_bill(self):
        """Open Create Bill window"""
        if self.create_bill_window is None:
            self.create_bill_window = CreateBillWindow(self.printer)
        self.create_bill_window.showMaximized()
        self.create_bill_window.raise_()
        self.create_bill_window.activateWindow()
    
    def open_bill_history(self):
        """Open Bill History window"""
        if self.bill_history_window is None:
            self.bill_history_window = BillHistoryWindow(self.printer)
        self.bill_history_window.showMaximized()
        self.bill_history_window.raise_()
        self.bill_history_window.activateWindow()
    
    def open_inventory(self):
        """Open Inventory window"""
        if self.inventory_window is None:
            self.inventory_window = InventoryWindow()
        self.inventory_window.showMaximized()
        self.inventory_window.raise_()
        self.inventory_window.activateWindow()
    
    def open_sales_report(self):
        """Open Sales Report window"""
        if self.sales_report_window is None:
            self.sales_report_window = SalesReportWindow()
        self.sales_report_window.showMaximized()
        self.sales_report_window.raise_()
        self.sales_report_window.activateWindow()
    
    def open_settings(self):
        """Open admin settings window"""
        if self.admin_settings_window is None:
            self.admin_settings_window = AdminSettingsWindow()
            # Connect signal to refresh printer shop details
            self.admin_settings_window.shop_details_updated.connect(self.refresh_printer_details)
        # Always restore and bring to front
        self.admin_settings_window.showNormal()
        self.admin_settings_window.raise_()
        self.admin_settings_window.activateWindow()
    
    def refresh_printer_details(self):
        """Refresh printer shop details when admin settings are updated"""
        if self.printer:
            self.printer.refresh_shop_details()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Close all child windows
        if self.create_bill_window:
            self.create_bill_window.close()
        if self.bill_history_window:
            self.bill_history_window.close()
        if self.inventory_window:
            self.inventory_window.close()
        if self.sales_report_window:
            self.sales_report_window.close()
        if self.admin_settings_window:
            self.admin_settings_window.close()
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeDashboard()
    window.show()
    sys.exit(app.exec_())