from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton
)
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QPixmap, QPainterPath, QPolygonF, QPen

import json
import os
import numpy as np
from SoilWise.ui.pages.advanced_reports_page import AdvancedReportsPage
from database.db_manager import get_database
from PySide6.QtWidgets import QTableWidgetItem



class SuitabilityMapWidget(QWidget):
    """Choropleth map visualization using GeoJSON polygons."""

    def __init__(self, results: dict, parent=None):
        super().__init__(parent)
        self.results = results
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Suitability Map: Piagapo, Lanao del Sur")
        title.setFont(QFont("Georgia", 18, QFont.Bold))
        title.setStyleSheet("color: #3d5a3f; padding: 8px 0px;")
        layout.addWidget(title)

        subtitle = QLabel(
            f" This predefined map is showing {self.results['crop_name']} "
            f"suitability distribution accross Piagapo."
        )
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #6a8a6c; padding-bottom: 8px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        map_container = QFrame()
        map_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e0ede0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        map_layout = QVBoxLayout(map_container)
        map_layout.setSpacing(12)

        map_label = QLabel()
        map_label.setAlignment(Qt.AlignCenter)

        base_map_path = self.find_file("piagapo-map.png")
        geojson_path = self.find_file("piagapo-zones.geojson")

        if base_map_path is None:
            map_label.setText(
                "⚠️ Map Image Not Found\n\n"
                "Place 'piagapo-map.png' in your project folder.\n\n"
                "The evaluation results are still available below."
            )
            map_label.setStyleSheet("""
                color: #c87b00;
                font-size: 14px;
                padding: 60px;
                background: #fff8dc;
                border-radius: 6px;
            """)
        else:
            pixmap = self.create_choropleth_map(base_map_path, geojson_path)
            if pixmap and not pixmap.isNull():
                map_label.setPixmap(pixmap)
            else:
                map_label.setText("⚠️ Map Generation Failed\n\nUsing base map only")

        map_layout.addWidget(map_label)
        legend = self.create_legend()
        map_layout.addWidget(legend)
        layout.addWidget(map_container)

    def find_file(self, filename: str):
        """Search for a file in common project locations."""
        base_dir = os.path.dirname(__file__)
        possible_paths = [
            filename,
            os.path.join("data", filename),
            os.path.join("assets", filename),
            os.path.join(base_dir, filename),
            os.path.join(base_dir, "..", "..", filename),
            os.path.join(base_dir, "..", "..", "data", filename),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Found {filename} at: {path}")
                return path
        print(f"❌ {filename} not found")
        return None

    def create_choropleth_map(self, base_map_path: str, geojson_path):
        """Create choropleth map with polygon-based coloring."""
        try:
            base_pixmap = QPixmap(base_map_path)
            base_pixmap = base_pixmap.scaled(750, 550, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            width, height = base_pixmap.width(), base_pixmap.height()

            result = QPixmap(base_pixmap.size())
            result.fill(Qt.white)

            painter = QPainter(result)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawPixmap(0, 0, base_pixmap)

            if geojson_path and os.path.exists(geojson_path):
                print("📍 Loading GeoJSON polygons...")
                self.draw_geojson_polygons(painter, geojson_path, width, height)
            else:
                print("⚠️ GeoJSON not found, using synthetic zones")
                self.draw_synthetic_zones(painter, width, height)

            painter.end()
            return result

        except Exception as e:
            print(f"❌ Choropleth map error: {e}")
            import traceback
            traceback.print_exc()
            return self.create_fallback_map(base_map_path)
        
    def create_barangay_highlight_map(self, geojson_path: str, selected_barangay: str):
        """Create a choropleth map highlighting the selected barangay with high contrast."""
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                geojson_data = json.load(f)
            
            features = geojson_data.get("features", [])
            bounds = self.get_geojson_bounds(features)
            
            # Create canvas
            width, height = 750, 550
            result = QPixmap(width, height)
            result.fill(Qt.white)
            
            painter = QPainter(result)
            painter.setRenderHint(QPainter.Antialiasing)
            
            print(f"🎯 Highlighting barangay: {selected_barangay}")
            
            for feature in features:
                brgy_name = feature.get("properties", {}).get("brgy_name", "")
                geometry = feature.get("geometry", {})
                
                # High contrast colors
                if brgy_name == selected_barangay:
                    color = QColor(45, 122, 45, 200)  # Dark green (highlighted)
                    border_color = QColor(29, 82, 29)  # Darker border
                    border_width = 1
                else:
                    color = QColor(232, 243, 232, 160)  # Very light green (background)
                    border_color = QColor(180, 200, 180, 100)  # Light gray border
                    border_width = 1
                
                polygons = self.geojson_to_qt_polygons(geometry, bounds, width, height)
                
                for polygon in polygons:
                    path = QPainterPath()
                    path.addPolygon(polygon)
                    
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(color)
                    painter.drawPath(path)
                    
                    painter.setPen(QPen(border_color, border_width))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawPath(path)
                
                # Add label to highlighted barangay
                if brgy_name == selected_barangay:
                    polygons_for_centroid = self.geojson_to_qt_polygons(geometry, bounds, width, height)
                    if polygons_for_centroid:
                        centroid = polygons_for_centroid[0].boundingRect().center()
                        
                        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
                        painter.setPen(Qt.white)
                        
                        # Draw text with shadow effect
                        painter.drawText(int(centroid.x()) + 2, int(centroid.y()) + 2, selected_barangay)
                        painter.setPen(QColor(45, 122, 45))
                        painter.drawText(int(centroid.x()), int(centroid.y()), selected_barangay)
            
            painter.end()
            print("✅ Barangay highlight map created!")
            return result
            
        except Exception as e:
            print(f"❌ Barangay highlight error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def draw_geojson_polygons(self, painter: QPainter, geojson_path: str, width: int, height: int):
        """Draw polygons from GeoJSON with suitability colors based on evaluation."""
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                geojson_data = json.load(f)

            features = geojson_data.get("features", [])
            print(f"📊 Rendering {len(features)} polygons...")

            # Get the evaluation results
            lsc = self.results['lsc']
            lsi = self.results['lsi']

            # Get selected barangay from results (if any)
            selected_barangay = self.results.get('site_name', '')

            # Clean up the selected barangay name
            if selected_barangay:
                if selected_barangay == "Select barangay...":
                    selected_barangay = ''
                else:
                    selected_barangay = selected_barangay.strip()

            print(f"   🔍 Selected barangay: '{selected_barangay}'")

            # Determine value range based on classification
            if lsc == 'S1':
                base_value = lsi
                variation = 10
                min_val, max_val = 70, 95
            elif lsc == 'S2':
                base_value = lsi
                variation = 12
                min_val, max_val = 45, 75
            elif lsc == 'S3':
                base_value = lsi
                variation = 10
                min_val, max_val = 25, 55
            else:  # N
                base_value = lsi
                variation = 8
                min_val, max_val = 5, 30

            print(f"   🎯 Base LSI: {lsi:.1f}, Range: {min_val}-{max_val}")

            # Generate values for each zone with realistic variation
            np.random.seed(42)
            zone_values = np.random.normal(base_value, variation, len(features))
            zone_values = np.clip(zone_values, min_val, max_val)
            print(f"   📊 Zone values: {zone_values.min():.1f} - {zone_values.max():.1f}")

            bounds = self.get_geojson_bounds(features)

            highlighted_count = 0

            for idx, feature in enumerate(features):
                brgy_name = feature.get("properties", {}).get("brgy_name", "")
                geometry = feature.get("geometry", {})
                zone_value = float(zone_values[idx])

                # Check if this is the selected barangay (exact match)
                is_selected = (selected_barangay and brgy_name == selected_barangay)

                if is_selected:
                    highlighted_count += 1
                    # MAXIMUM CONTRAST: Use the most extreme color in the gradient
                    if lsc == 'S1':
                        color = (25, 200, 34)  # Bright green
                        border_color = QColor(0, 100, 0)
                        border_width = 0
                        alpha = 255  # Fully opaque
                    elif lsc == 'S2':
                        color = (200, 220, 0)  # Bright yellow
                        border_color = QColor(200, 150, 0)
                        border_width = 0
                        alpha = 255
                    elif lsc == 'S3':
                        color = (200, 100, 0)  # Bright orange
                        border_color = QColor(200, 50, 0)
                        border_width = 0
                        alpha = 255
                    else:  # N
                        color = (160, 0, 0)  # Bright red
                        border_color = QColor(150, 0, 0)
                        border_width = 0
                        alpha = 255

                    print(f"   ⭐ HIGHLIGHTING: '{brgy_name}' with {lsc} color!")
                else:
                    # Normal gradient color with reduced opacity
                    color = self.value_to_color(zone_value)
                    border_color = QColor(60, 60, 60, 80)
                    border_width = 1
                    alpha = 130  # More transparent for background

                polygons = self.geojson_to_qt_polygons(geometry, bounds, width, height)

                for polygon in polygons:
                    path = QPainterPath()
                    path.addPolygon(polygon)

                    # Draw filled polygon
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor(color[0], color[1], color[2], alpha))
                    painter.drawPath(path)

                    # Draw border
                    painter.setPen(QPen(border_color, border_width))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawPath(path)

                # Add label to ALL barangays
                if polygons:
                    centroid = polygons[0].boundingRect().center()

                    if is_selected:
                        # Selected barangay: larger, bold, white text
                        painter.setFont(QFont("Segoe UI", 14, QFont.Bold))

                        # Shadow
                        painter.setPen(QColor(0, 0, 0, 200))
                        painter.drawText(int(centroid.x()) + 2, int(centroid.y()) + 2, brgy_name)

                        # Main text in white
                        painter.setPen(Qt.white)
                        painter.drawText(int(centroid.x()), int(centroid.y()), brgy_name)
                    else:
                        # Non-selected barangays: smaller, subtle text
                        painter.setFont(QFont("Segoe UI", 9))

                        # Dark text with slight transparency
                        painter.setPen(QColor(60, 80, 60, 180))
                        painter.drawText(int(centroid.x()), int(centroid.y()), brgy_name)

            if selected_barangay and highlighted_count == 0:
                print(f"   ⚠️ WARNING: '{selected_barangay}' not found in map!")
                print(f"   Available barangays: {[f.get('properties', {}).get('brgy_name', '') for f in features[:5]]}...")
            elif highlighted_count > 0:
                print(f"   ✅ Successfully highlighted {highlighted_count} polygon(s)")

            print("✅ Choropleth polygons rendered!")

        except Exception as e:
            print(f"❌ GeoJSON rendering failed: {e}")
            import traceback
            traceback.print_exc()
            self.draw_synthetic_zones(painter, width, height)


    def get_geojson_bounds(self, features: list):
        min_lon = min_lat = float("inf")
        max_lon = max_lat = float("-inf")

        for feature in features:
            coords = self.extract_coordinates(feature.get("geometry", {}))
            for lon, lat in coords:
                min_lon = min(min_lon, lon)
                max_lon = max(max_lon, lon)
                min_lat = min(min_lat, lat)
                max_lat = max(max_lat, lat)

        return {"min_lon": min_lon, "max_lon": max_lon, "min_lat": min_lat, "max_lat": max_lat}

    def extract_coordinates(self, geometry: dict):
        coords = []
        geom_type = geometry.get("type", "")
        coordinates = geometry.get("coordinates", [])

        if geom_type == "Polygon":
            for ring in coordinates:
                coords.extend(ring)
        elif geom_type == "MultiPolygon":
            for polygon in coordinates:
                for ring in polygon:
                    coords.extend(ring)
        return coords

    def geojson_to_qt_polygons(self, geometry: dict, bounds: dict, width: int, height: int):
        polygons = []
        geom_type = geometry.get("type", "")
        coordinates = geometry.get("coordinates", [])

        if geom_type == "Polygon":
            for ring in coordinates:
                poly = self.coords_to_polygon(ring, bounds, width, height)
                if poly:
                    polygons.append(poly)
        elif geom_type == "MultiPolygon":
            for polygon in coordinates:
                for ring in polygon:
                    poly = self.coords_to_polygon(ring, bounds, width, height)
                    if poly:
                        polygons.append(poly)
        return polygons

    def coords_to_polygon(self, coordinates: list, bounds: dict, width: int, height: int):
        lon_range = bounds["max_lon"] - bounds["min_lon"]
        lat_range = bounds["max_lat"] - bounds["min_lat"]
        if lon_range == 0 or lat_range == 0:
            return None

        padding = 0.05
        points = []

        for lon, lat in coordinates:
            x_norm = (lon - bounds["min_lon"]) / lon_range
            y_norm = (lat - bounds["min_lat"]) / lat_range
            x = (padding + x_norm * (1 - 2 * padding)) * width
            y = height - (padding + y_norm * (1 - 2 * padding)) * height
            points.append(QPointF(x, y))

        return QPolygonF(points) if points else None

    def draw_synthetic_zones(self, painter: QPainter, width: int, height: int):
        """Fallback grid zones based on evaluation results."""
        lsc = self.results['lsc']
        lsi = self.results['lsi']
        
        if lsc == 'S1':
            base_value, variation, min_val, max_val = lsi, 10, 70, 95
        elif lsc == 'S2':
            base_value, variation, min_val, max_val = lsi, 12, 45, 75
        elif lsc == 'S3':
            base_value, variation, min_val, max_val = lsi, 10, 25, 55
        else:
            base_value, variation, min_val, max_val = lsi, 8, 5, 30

        grid_rows, grid_cols = 4, 5
        cell_w, cell_h = width / grid_cols, height / grid_rows
        
        np.random.seed(42)
        cell_values = np.random.normal(base_value, variation, grid_rows * grid_cols)
        cell_values = np.clip(cell_values, min_val, max_val)

        idx = 0
        for row in range(grid_rows):
            for col in range(grid_cols):
                color = self.value_to_color(float(cell_values[idx]))
                idx += 1

                x, y = col * cell_w, row * cell_h
                polygon = QPolygonF([QPointF(x, y), QPointF(x + cell_w, y),
                                    QPointF(x + cell_w, y + cell_h), QPointF(x, y + cell_h)])

                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(color[0], color[1], color[2], 120))
                painter.drawPolygon(polygon)

                painter.setPen(QColor(80, 80, 80, 80))
                painter.setBrush(Qt.NoBrush)
                painter.drawPolygon(polygon)

    def value_to_color(self, value: float):
        """Map 0–100 suitability value to vibrant Red-Yellow-Green gradient."""
        normalized = max(0.0, min(1.0, value / 100.0))

        if normalized < 0.25:
            t = normalized / 0.25
            r = int(139 + (220 - 139) * t)
            g = int(0 + (20 - 0) * t)
            b = int(0 + (60 - 0) * t)
        elif normalized < 0.5:
            t = (normalized - 0.25) / 0.25
            r = int(220 + (255 - 220) * t)
            g = int(20 + (140 - 20) * t)
            b = int(60 + (0 - 60) * t)
        elif normalized < 0.75:
            t = (normalized - 0.5) / 0.25
            r = int(255 + (255 - 255) * t)
            g = int(140 + (215 - 140) * t)
            b = int(0 + (0 - 0) * t)
        else:
            t = (normalized - 0.75) / 0.25
            r = int(255 + (34 - 255) * t)
            g = int(215 + (139 - 215) * t)
            b = int(0 + (34 - 0) * t)
        
        return r, g, b

    def create_fallback_map(self, base_map_path: str):
        try:
            base_pixmap = QPixmap(base_map_path)
            base_pixmap = base_pixmap.scaled(750, 550, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            result = QPixmap(base_pixmap.size())
            result.fill(Qt.white)

            painter = QPainter(result)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawPixmap(0, 0, base_pixmap)
            painter.fillRect(result.rect(), QColor(100, 100, 100, 60))
            painter.end()
            return result
        except:
            return None

    def create_legend(self):
        legend_frame = QFrame()
        legend_frame.setStyleSheet("""
            QFrame {
                background: #f9fbf9;
                border-radius: 8px;
                padding: 16px;
                border: 1px solid #e0ede0;
            }
        """)
        layout = QVBoxLayout(legend_frame)
        layout.setSpacing(12)

        title_row = QHBoxLayout()
        legend_title = QLabel("Legend: Land Suitability Index (LSI)")
        legend_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        legend_title.setStyleSheet("color: #3d5a3f;")
        title_row.addWidget(legend_title)
        title_row.addStretch()

        current_label = QLabel(
            f"Current: {self.results['crop_name']} - "
            f"LSI {self.results['lsi']:.1f} ({self.results['lsc']})"
        )
        current_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        current_label.setStyleSheet(f"color: {self.get_solid_color(self.results['lsc'])};")
        title_row.addWidget(current_label)
        layout.addLayout(title_row)

        gradient_bar = self.create_gradient_bar()
        layout.addWidget(gradient_bar)

        classes_layout = QHBoxLayout()
        classes = [
            ("N (Not Suitable)", "0–25", "#8B0000"),
            ("S3 (Marginally)", "25–50", "#FF8C00"),
            ("S2 (Moderately)", "50–75", "#FFD700"),
            ("S1 (Highly)", "75–100", "#228B22"),
        ]
        for label_text, range_text, color in classes:
            item = QWidget()
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(4)

            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
            lbl.setStyleSheet(f"color: {color};")
            rng = QLabel(range_text)
            rng.setFont(QFont("Segoe UI", 9))
            rng.setStyleSheet("color: #6a8a6c;")

            item_layout.addWidget(lbl)
            item_layout.addWidget(rng)
            classes_layout.addWidget(item)
        layout.addLayout(classes_layout)

        note = QLabel("Note: This is not a real time and accurate report of the map. This is only an assumption.")
        note.setFont(QFont("Segoe UI", 10))
        note.setStyleSheet("color: #8a9a8c; font-style: italic;")
        note.setWordWrap(True)
        layout.addWidget(note)

        return legend_frame

    def create_gradient_bar(self):
        gradient_widget = QLabel()
        gradient_widget.setFixedHeight(30)
        gradient_widget.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgb(139, 0, 0),
                    stop:0.25 rgb(220, 20, 60),
                    stop:0.5 rgb(255, 140, 0),
                    stop:0.75 rgb(255, 215, 0),
                    stop:1 rgb(34, 139, 34));
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }
        """)
        return gradient_widget

    def get_solid_color(self, lsc: str):
        colors = {"S1": "#228B22", "S2": "#FFD700", "S3": "#FF8C00", "N": "#8B0000"}
        return colors.get(lsc, "#3d5a3f")


class ReportsPage(QWidget):
    """Main Reports & Analysis page."""

    new_evaluation_requested = Signal()

    def __init__(self, results: dict, parent=None):
        super().__init__(parent)
        self.results = results
        self.advanced_window = None
        self.init_ui()
        # Initialize database
        try:
            self.db = get_database()
            print("Database connected in Reports Page")
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.db = None

        # Load evaluations from database
        self.load_evaluations()


    def init_ui(self):
        """Initialize the Reports page UI"""
        # Add border: none to the main widget
        self.setStyleSheet("background-color: #fafcfa; border: none;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)  # Add this line
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")  # Add this line
        
        content = QWidget()
        content.setStyleSheet("background-color: transparent; border: none;")  # Add this line
        scroll.setWidget(content)
        
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)
        
        map_widget = SuitabilityMapWidget(self.results, self)
        content_layout.addWidget(map_widget)
        
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(12)
        
        btn_advanced = QPushButton("View Detailed Report")
        btn_advanced.setFixedHeight(40)
        btn_advanced.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #5b8a5b;
                border-radius: 6px;
                border: 1px solid #7d9d7f;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #f5f9f5;
            }
        """)
        btn_advanced.clicked.connect(self.open_advanced_report)
        buttons_row.addWidget(btn_advanced)
        
        btn_new = QPushButton("New Evaluation")
        btn_new.setFixedHeight(40)
        btn_new.setStyleSheet("""
            QPushButton {
                background-color: #5b8a5b;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4c7a4c;
            }
        """)
        btn_new.clicked.connect(self.new_evaluation_requested.emit)
        buttons_row.addWidget(btn_new)
        
        buttons_row.addStretch()
        content_layout.addLayout(buttons_row)
        content_layout.addStretch()
        
        main_layout.addWidget(scroll)


    def open_advanced_report(self):
        """Open the full AdvancedReportsPage in a separate window."""
        if self.advanced_window is None:
            self.advanced_window = AdvancedReportsPage()
        self.advanced_window.display_results(self.results)
        self.advanced_window.show()
        self.advanced_window.raise_()
        self.advanced_window.activateWindow()

    def load_evaluations(self):
        """Load evaluation results from database"""
        if not self.db:
            print("Database not available")
            return
        
        try:
            # Get recent evaluations from database
            evaluations = self.db.get_evaluation_history(limit=50)
            
            print(f"Loaded {len(evaluations)} evaluations from database")
            
            # Clear existing table
            if hasattr(self, 'results_table'):
                self.results_table.setRowCount(0)
            
            # Populate table with database results
            for eval_data in evaluations:
                self.add_evaluation_to_table(eval_data)
            
            return evaluations
            
        except Exception as e:
            print(f"Error loading evaluations: {e}")
            import traceback
            traceback.print_exc()
            return []

    def add_evaluation_to_table(self, eval_data):
        """Add a single evaluation to the table"""
        if not hasattr(self, 'results_table'):
            return
        
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Date
        date_str = eval_data.get('created_at', '')[:16] if eval_data.get('created_at') else 'N/A'
        self.results_table.setItem(row, 0, QTableWidgetItem(date_str))
        
        # Crop name
        crop_name = eval_data.get('crop_id', '').replace('_', ' ').title()
        self.results_table.setItem(row, 1, QTableWidgetItem(crop_name))
        
        # LSI
        lsi = eval_data.get('lsi', 0)
        self.results_table.setItem(row, 2, QTableWidgetItem(f"{lsi:.2f}"))
        
        # Classification
        classification = eval_data.get('full_classification', 'N/A')
        self.results_table.setItem(row, 3, QTableWidgetItem(classification))
        
        # Location (if available)
        location = eval_data.get('location', 'N/A')
        self.results_table.setItem(row, 4, QTableWidgetItem(location))
