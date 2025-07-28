import sys
import csv
from datetime import datetime, date, timedelta
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QDateEdit, QGroupBox,
                             QGridLayout, QMessageBox, QFileDialog, QScrollArea,
                             QFrame, QSizePolicy, QApplication, QProgressBar)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPainter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from data_base.database import Database
import numpy as np

class ReportGeneratorThread(QThread):
    """Thread for generating reports to avoid blocking UI"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, report_data, file_path, format_type):
        super().__init__()
        self.report_data = report_data
        self.file_path = file_path
        self.format_type = format_type
    
    def run(self):
        try:
            if self.format_type == 'csv':
                self._export_csv()
            elif self.format_type == 'pdf':
                self._export_pdf()
            self.finished.emit(True, f"Report exported successfully to {self.file_path}")
        except Exception as e:
            self.finished.emit(False, f"Failed to export report: {str(e)}")
    
    def _export_csv(self):
        """Export sales report data to CSV"""
        with open(self.file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write summary data
            writer.writerow(['Sales Report Summary'])
            writer.writerow(['Date Range', f"{self.report_data['start_date']} to {self.report_data['end_date']}"])
            writer.writerow(['Total Revenue', f"₹{self.report_data['total_revenue']:.2f}"])
            writer.writerow(['Total Bills', self.report_data['total_bills']])
            writer.writerow(['Total Items Sold', self.report_data['total_items']])
            writer.writerow(['Average Bill Value', f"₹{self.report_data['avg_bill_value']:.2f}"])
            writer.writerow([])
            
            # Write top selling items
            writer.writerow(['Top Selling Items'])
            writer.writerow(['Item Name', 'Quantity Sold', 'Revenue'])
            for item in self.report_data['top_items']:
                writer.writerow([item['name'], item['quantity'], f"₹{item['revenue']:.2f}"])
            writer.writerow([])
            
            # Write category-wise sales
            writer.writerow(['Category-wise Sales'])
            writer.writerow(['Category', 'Revenue', 'Percentage'])
            for category in self.report_data['category_sales']:
                writer.writerow([category['name'], f"₹{category['revenue']:.2f}", f"{category['percentage']:.1f}%"])
    
    def _export_pdf(self):
        """Export sales report data to PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(self.file_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph("Sales Report", title_style))
            story.append(Spacer(1, 20))
            
            # Summary section
            summary_data = [
                ['Date Range', f"{self.report_data['start_date']} to {self.report_data['end_date']}"],
                ['Total Revenue', f"₹{self.report_data['total_revenue']:.2f}"],
                ['Total Bills', str(self.report_data['total_bills'])],
                ['Total Items Sold', str(self.report_data['total_items'])],
                ['Average Bill Value', f"₹{self.report_data['avg_bill_value']:.2f}"]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(Paragraph("Summary", styles['Heading2']))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Top selling items
            if self.report_data['top_items']:
                story.append(Paragraph("Top Selling Items", styles['Heading2']))
                items_data = [['Item Name', 'Quantity Sold', 'Revenue']]
                for item in self.report_data['top_items'][:10]:
                    items_data.append([item['name'], str(item['quantity']), f"₹{item['revenue']:.2f}"])
                
                items_table = Table(items_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                items_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(items_table)
            
            doc.build(story)
            
        except ImportError:
            # Fallback to simple text-based PDF if reportlab is not available
            with open(self.file_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write("SALES REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Date Range: {self.report_data['start_date']} to {self.report_data['end_date']}\n")
                f.write(f"Total Revenue: ₹{self.report_data['total_revenue']:.2f}\n")
                f.write(f"Total Bills: {self.report_data['total_bills']}\n")
                f.write(f"Total Items Sold: {self.report_data['total_items']}\n")
                f.write(f"Average Bill Value: ₹{self.report_data['avg_bill_value']:.2f}\n\n")
                
                f.write("TOP SELLING ITEMS:\n")
                f.write("-" * 30 + "\n")
                for item in self.report_data['top_items'][:10]:
                    f.write(f"{item['name']}: {item['quantity']} units, ₹{item['revenue']:.2f}\n")

class ChartWidget(QWidget):
    """Custom widget for displaying matplotlib charts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Set background color to match application theme
        self.figure.patch.set_facecolor('#f8f9fa')
    
    def clear_chart(self):
        """Clear the current chart"""
        self.figure.clear()
        self.canvas.draw()
    
    def create_pie_chart(self, data, title, colors=None):
        """Create a pie chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            self.canvas.draw()
            return
        
        labels = [item['name'] for item in data]
        sizes = [item['value'] for item in data]
        
        if colors is None:
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        self.canvas.draw()
    
    def create_bar_chart(self, data, title, xlabel, ylabel):
        """Create a bar chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            self.canvas.draw()
            return
        
        labels = [item['name'][:15] + '...' if len(item['name']) > 15 else item['name'] 
                 for item in data]
        values = [item['value'] for item in data]
        
        bars = ax.bar(labels, values, color='#3498db', alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def create_line_chart(self, data, title, xlabel, ylabel):
        """Create a line chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            self.canvas.draw()
            return
        
        dates = [datetime.strptime(item['date'], '%Y-%m-%d').date() for item in data]
        values = [item['value'] for item in data]
        
        ax.plot(dates, values, marker='o', linewidth=2, markersize=6, color='#e74c3c')
        ax.fill_between(dates, values, alpha=0.3, color='#e74c3c')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.figure.tight_layout()
        self.canvas.draw()

class SalesReportWindow(QMainWindow):
    """Sales Report Window with comprehensive analytics"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sales Report")
        self.setMinimumSize(1200, 800)
        self.db = Database()
        
        # Initialize date range
        self.start_date = date.today() - timedelta(days=30)  # Default: Last 30 days
        self.end_date = date.today()
        
        self.init_ui()
        self.load_report_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create scroll area for the entire content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.addWidget(scroll_area)
        
        content_layout = QVBoxLayout()
        scroll_content.setLayout(content_layout)
        
        # Header
        header_label = QLabel("Sales Report & Analytics")
        header_label.setFont(QFont("Poppins", 24, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 20px;
                background-color: #ecf0f1;
                border-radius: 10px;
                margin-bottom: 20px;
            }
        """)
        content_layout.addWidget(header_label)
        
        # Date Range Controls
        self.create_date_controls(content_layout)
        
        # Summary Cards
        self.create_summary_cards(content_layout)
        
        # Charts Section
        self.create_charts_section(content_layout)
        
        # Export Controls
        self.create_export_controls(content_layout)
        
        # Set main window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def create_date_controls(self, layout):
        """Create date range selection controls"""
        date_group = QGroupBox("Date Range Selection")
        date_group.setFont(QFont("Poppins", 14, QFont.Bold))
        date_layout = QHBoxLayout()
        
        # Quick date range buttons
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(lambda: self.set_date_range('today'))
        today_btn.setStyleSheet(self.get_button_style('#3498db'))
        
        week_btn = QPushButton("This Week")
        week_btn.clicked.connect(lambda: self.set_date_range('week'))
        week_btn.setStyleSheet(self.get_button_style('#2ecc71'))
        
        month_btn = QPushButton("This Month")
        month_btn.clicked.connect(lambda: self.set_date_range('month'))
        month_btn.setStyleSheet(self.get_button_style('#9b59b6'))
        
        # Custom date range
        date_layout.addWidget(QLabel("Quick Select:"))
        date_layout.addWidget(today_btn)
        date_layout.addWidget(week_btn)
        date_layout.addWidget(month_btn)
        date_layout.addStretch()
        
        # Custom date inputs
        date_layout.addWidget(QLabel("From:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.fromString(self.start_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        self.start_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.start_date_edit)
        
        date_layout.addWidget(QLabel("To:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.fromString(self.end_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        self.end_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.end_date_edit)
        
        # Update button
        update_btn = QPushButton("Update Report")
        update_btn.clicked.connect(self.update_date_range)
        update_btn.setStyleSheet(self.get_button_style('#e74c3c'))
        date_layout.addWidget(update_btn)
        
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
    
    def create_summary_cards(self, layout):
        """Create summary statistics cards"""
        summary_group = QGroupBox("Sales Summary")
        summary_group.setFont(QFont("Poppins", 14, QFont.Bold))
        summary_layout = QGridLayout()
        
        # Create summary labels
        self.total_revenue_label = QLabel("₹0.00")
        self.total_bills_label = QLabel("0")
        self.total_items_label = QLabel("0")
        self.avg_bill_label = QLabel("₹0.00")
        
        # Style summary labels
        summary_style = """
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }
        """
        
        self.total_revenue_label.setStyleSheet(summary_style)
        self.total_bills_label.setStyleSheet(summary_style)
        self.total_items_label.setStyleSheet(summary_style)
        self.avg_bill_label.setStyleSheet(summary_style)
        
        # Add labels with titles
        summary_layout.addWidget(QLabel("Total Revenue"), 0, 0)
        summary_layout.addWidget(self.total_revenue_label, 1, 0)
        
        summary_layout.addWidget(QLabel("Total Bills"), 0, 1)
        summary_layout.addWidget(self.total_bills_label, 1, 1)
        
        summary_layout.addWidget(QLabel("Items Sold"), 0, 2)
        summary_layout.addWidget(self.total_items_label, 1, 2)
        
        summary_layout.addWidget(QLabel("Avg Bill Value"), 0, 3)
        summary_layout.addWidget(self.avg_bill_label, 1, 3)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
    
    def create_charts_section(self, layout):
        """Create charts section"""
        charts_group = QGroupBox("Analytics Charts")
        charts_group.setFont(QFont("Poppins", 14, QFont.Bold))
        charts_layout = QGridLayout()
        
        # Create chart widgets
        self.item_type_chart = ChartWidget()
        self.gst_chart = ChartWidget()
        self.top_items_chart = ChartWidget()
        self.category_chart = ChartWidget()
        self.daily_trend_chart = ChartWidget()
        
        # Set minimum sizes for charts
        chart_min_size = (400, 300)
        self.item_type_chart.setMinimumSize(*chart_min_size)
        self.gst_chart.setMinimumSize(*chart_min_size)
        self.top_items_chart.setMinimumSize(*chart_min_size)
        self.category_chart.setMinimumSize(*chart_min_size)
        self.daily_trend_chart.setMinimumSize(800, 300)
        
        # Add charts to layout
        charts_layout.addWidget(self.item_type_chart, 0, 0)
        charts_layout.addWidget(self.gst_chart, 0, 1)
        charts_layout.addWidget(self.top_items_chart, 1, 0)
        charts_layout.addWidget(self.category_chart, 1, 1)
        charts_layout.addWidget(self.daily_trend_chart, 2, 0, 1, 2)
        
        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)
    
    def create_export_controls(self, layout):
        """Create export controls"""
        export_group = QGroupBox("Export Options")
        export_group.setFont(QFont("Poppins", 14, QFont.Bold))
        export_layout = QHBoxLayout()
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 6px;
            }
        """)
        
        export_csv_btn = QPushButton("Export as CSV")
        export_csv_btn.clicked.connect(lambda: self.export_report('csv'))
        export_csv_btn.setStyleSheet(self.get_button_style('#27ae60'))
        
        export_pdf_btn = QPushButton("Export as PDF")
        export_pdf_btn.clicked.connect(lambda: self.export_report('pdf'))
        export_pdf_btn.setStyleSheet(self.get_button_style('#f39c12'))
        
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.load_report_data)
        refresh_btn.setStyleSheet(self.get_button_style('#17a2b8'))
        
        export_layout.addWidget(export_csv_btn)
        export_layout.addWidget(export_pdf_btn)
        export_layout.addStretch()
        export_layout.addWidget(self.progress_bar)
        export_layout.addStretch()
        export_layout.addWidget(refresh_btn)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
    
    def get_button_style(self, color):
        """Get consistent button styling"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """
    
    def set_date_range(self, range_type):
        """Set predefined date ranges"""
        today = date.today()
        
        if range_type == 'today':
            self.start_date = today
            self.end_date = today
        elif range_type == 'week':
            self.start_date = today - timedelta(days=today.weekday())
            self.end_date = today
        elif range_type == 'month':
            self.start_date = today.replace(day=1)
            self.end_date = today
        
        # Update date edit widgets
        self.start_date_edit.setDate(QDate.fromString(self.start_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        self.end_date_edit.setDate(QDate.fromString(self.end_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        
        # Reload data
        self.load_report_data()
    
    def update_date_range(self):
        """Update date range from custom inputs"""
        self.start_date = self.start_date_edit.date().toPyDate()
        self.end_date = self.end_date_edit.date().toPyDate()
        
        if self.start_date > self.end_date:
            QMessageBox.warning(self, "Invalid Date Range", "Start date cannot be after end date!")
            return
        
        self.load_report_data()
    
    def load_report_data(self):
        """Load and display sales report data"""
        try:
            # Get bills data for the selected date range
            start_date_str = self.start_date.strftime('%Y-%m-%d')
            end_date_str = self.end_date.strftime('%Y-%m-%d')
            
            bills = self.db.get_bills_by_date_range(start_date_str, end_date_str)
            
            if not bills:
                self.show_no_data_message()
                return
            
            # Calculate summary statistics
            total_revenue = sum(bill['total_amount'] for bill in bills)
            total_bills = len(bills)
            total_items = sum(bill['total_items'] for bill in bills)
            avg_bill_value = total_revenue / total_bills if total_bills > 0 else 0
            
            # Update summary labels
            self.total_revenue_label.setText(f"₹{total_revenue:.2f}")
            self.total_bills_label.setText(str(total_bills))
            self.total_items_label.setText(str(total_items))
            self.avg_bill_label.setText(f"₹{avg_bill_value:.2f}")
            
            # Generate charts data
            self.generate_item_type_chart(bills)
            self.generate_gst_chart(bills)
            self.generate_top_items_chart()
            self.generate_category_chart()
            self.generate_daily_trend_chart(bills)
            
            # Store data for export
            self.current_report_data = {
                'start_date': start_date_str,
                'end_date': end_date_str,
                'total_revenue': total_revenue,
                'total_bills': total_bills,
                'total_items': total_items,
                'avg_bill_value': avg_bill_value,
                'top_items': self.get_top_items_data(),
                'category_sales': self.get_category_sales_data()
            }
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load report data: {str(e)}")
    
    def show_no_data_message(self):
        """Show message when no data is available"""
        # Clear all charts and show no data message
        self.total_revenue_label.setText("₹0.00")
        self.total_bills_label.setText("0")
        self.total_items_label.setText("0")
        self.avg_bill_label.setText("₹0.00")
        
        # Clear all charts
        self.item_type_chart.clear_chart()
        self.gst_chart.clear_chart()
        self.top_items_chart.clear_chart()
        self.category_chart.clear_chart()
        self.daily_trend_chart.clear_chart()
        
        QMessageBox.information(self, "No Data", "No sales data available for the selected date range.")
    
    def generate_item_type_chart(self, bills):
        """Generate pie chart for barcode vs loose items sales"""
        barcode_revenue = 0
        loose_revenue = 0
        
        for bill in bills:
            detailed_bill = self.db.get_bill_by_id(bill['id'])
            if detailed_bill:
                for item in detailed_bill['items']:
                    if item['item_type'] == 'barcode':
                        barcode_revenue += item['final_price']
                    else:
                        loose_revenue += item['final_price']
        
        data = []
        if barcode_revenue > 0:
            data.append({'name': 'Barcode Items', 'value': barcode_revenue})
        if loose_revenue > 0:
            data.append({'name': 'Loose Items', 'value': loose_revenue})
        
        self.item_type_chart.create_pie_chart(data, "Sales by Item Type")
    
    def generate_gst_chart(self, bills):
        """Generate pie chart for GST collected by category"""
        total_sgst = sum(bill.get('total_sgst', 0) for bill in bills)
        total_cgst = sum(bill.get('total_cgst', 0) for bill in bills)
        
        data = []
        if total_sgst > 0:
            data.append({'name': 'SGST', 'value': total_sgst})
        if total_cgst > 0:
            data.append({'name': 'CGST', 'value': total_cgst})
        
        self.gst_chart.create_pie_chart(data, "GST Collection Breakdown")
    
    def generate_top_items_chart(self):
        """Generate bar chart for top selling items"""
        # Get item sales data from bill_items
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bi.item_name, SUM(bi.quantity) as total_quantity, SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) BETWEEN ? AND ?
            GROUP BY bi.item_name
            ORDER BY total_quantity DESC
            LIMIT 10
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        results = cursor.fetchall()
        conn.close()
        
        data = [{'name': row[0], 'value': row[1]} for row in results]
        self.top_items_chart.create_bar_chart(data, "Top 10 Selling Items", "Items", "Quantity Sold")
    
    def generate_category_chart(self):
        """Generate bar chart for category-wise sales"""
        # Get category sales data
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get loose items category sales
        cursor.execute('''
            SELECT lc.name, SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            JOIN loose_items li ON bi.item_name = li.name
            JOIN loose_categories lc ON li.category_id = lc.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'loose'
            GROUP BY lc.name
            ORDER BY total_revenue DESC
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        loose_results = cursor.fetchall()
        
        # Get barcode items sales (as one category)
        cursor.execute('''
            SELECT SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'barcode'
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        barcode_result = cursor.fetchone()
        conn.close()
        
        data = [{'name': row[0], 'value': row[1]} for row in loose_results]
        if barcode_result and barcode_result[0]:
            data.append({'name': 'Barcode Items', 'value': barcode_result[0]})
        
        self.category_chart.create_bar_chart(data, "Category-wise Sales", "Categories", "Revenue (₹)")
    
    def generate_daily_trend_chart(self, bills):
        """Generate line chart for daily sales trend"""
        # Group bills by date
        daily_sales = {}
        for bill in bills:
            bill_date = bill['created_at'][:10]  # Extract date part
            if bill_date in daily_sales:
                daily_sales[bill_date] += bill['total_amount']
            else:
                daily_sales[bill_date] = bill['total_amount']
        
        # Fill missing dates with 0
        current_date = self.start_date
        while current_date <= self.end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str not in daily_sales:
                daily_sales[date_str] = 0
            current_date += timedelta(days=1)
        
        # Sort by date
        sorted_sales = sorted(daily_sales.items())
        data = [{'date': date_str, 'value': amount} for date_str, amount in sorted_sales]
        
        self.daily_trend_chart.create_line_chart(data, "Daily Sales Trend", "Date", "Revenue (₹)")
    
    def get_top_items_data(self):
        """Get top items data for export"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bi.item_name, SUM(bi.quantity) as total_quantity, SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) BETWEEN ? AND ?
            GROUP BY bi.item_name
            ORDER BY total_quantity DESC
            LIMIT 20
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{'name': row[0], 'quantity': row[1], 'revenue': row[2]} for row in results]
    
    def get_category_sales_data(self):
        """Get category sales data for export"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get total revenue for percentage calculation
        total_revenue = float(self.total_revenue_label.text().replace('₹', '').replace(',', ''))
        
        # Get loose items category sales
        cursor.execute('''
            SELECT lc.name, SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            JOIN loose_items li ON bi.item_name = li.name
            JOIN loose_categories lc ON li.category_id = lc.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'loose'
            GROUP BY lc.name
            ORDER BY total_revenue DESC
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        loose_results = cursor.fetchall()
        
        # Get barcode items sales
        cursor.execute('''
            SELECT SUM(bi.final_price) as total_revenue
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.id
            WHERE DATE(b.created_at) BETWEEN ? AND ? AND bi.item_type = 'barcode'
        ''', (self.start_date.strftime('%Y-%m-%d'), self.end_date.strftime('%Y-%m-%d')))
        
        barcode_result = cursor.fetchone()
        conn.close()
        
        data = []
        for row in loose_results:
            percentage = (row[1] / total_revenue * 100) if total_revenue > 0 else 0
            data.append({'name': row[0], 'revenue': row[1], 'percentage': percentage})
        
        if barcode_result and barcode_result[0]:
            percentage = (barcode_result[0] / total_revenue * 100) if total_revenue > 0 else 0
            data.append({'name': 'Barcode Items', 'revenue': barcode_result[0], 'percentage': percentage})
        
        return data
    
    def export_report(self, format_type):
        """Export sales report"""
        if not hasattr(self, 'current_report_data'):
            QMessageBox.warning(self, "No Data", "No report data to export. Please generate a report first.")
            return
        
        # Get file path
        if format_type == 'csv':
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Sales Report as CSV",
                f"sales_report_{self.start_date}_{self.end_date}.csv",
                "CSV Files (*.csv)"
            )
        else:  # PDF
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Sales Report as PDF",
                f"sales_report_{self.start_date}_{self.end_date}.pdf",
                "PDF Files (*.pdf)"
            )
        
        if not file_path:
            return
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start export thread
        self.export_thread = ReportGeneratorThread(self.current_report_data, file_path, format_type)
        self.export_thread.finished.connect(self.on_export_finished)
        self.export_thread.start()
    
    def on_export_finished(self, success, message):
        """Handle export completion"""
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Export Complete", message)
        else:
            QMessageBox.critical(self, "Export Failed", message)
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Adjust chart sizes based on window size
        if hasattr(self, 'item_type_chart'):
            width = self.width()
            if width < 1400:
                chart_size = (350, 250)
            else:
                chart_size = (400, 300)
            
            self.item_type_chart.setMinimumSize(*chart_size)
            self.gst_chart.setMinimumSize(*chart_size)
            self.top_items_chart.setMinimumSize(*chart_size)
            self.category_chart.setMinimumSize(*chart_size)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SalesReportWindow()
    window.showMaximized()
    sys.exit(app.exec_())