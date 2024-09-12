import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QImage
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import subprocess

class LatexPreviewApp(QWidget):
    def __init__(self):
        super().__init__()
        self.latex_preamble = r"""
        \documentclass{article}
        \usepackage{amsmath}
        \usepackage{amsfonts}
        \usepackage{amssymb}
        \pagestyle{empty}
        \begin{document}
        """
        self.latex_postamble = r"\end{document}"
        self.init_ui()

    def init_ui(self):
        # Set up the layout and widgets
        self.layout = QVBoxLayout()

        # Input field for LaTeX
        self.latex_input = QLineEdit(self)
        self.latex_input.setPlaceholderText("Enter LaTeX equation...")
        self.latex_input.textChanged.connect(self.update_preview)
        self.layout.addWidget(self.latex_input)

        # Label for live preview
        self.preview_label = QLabel(self)
        self.layout.addWidget(self.preview_label)

        # Error message label
        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: red;")  # Set the text color to red
        self.layout.addWidget(self.error_label)

        # Button to save the PNG
        self.save_button = QPushButton("Save as PNG", self)
        self.save_button.clicked.connect(self.save_png)
        self.layout.addWidget(self.save_button)

        # Button to process all LaTeX strings
        self.process_button = QPushButton("Process All LaTeX", self)
        self.process_button.clicked.connect(self.process_all_latex)
        self.layout.addWidget(self.process_button)

        # Set the layout
        self.setLayout(self.layout)
        self.setWindowTitle('LaTeX to PNG Converter')
        self.setGeometry(100, 100, 600, 400)
        self.show()

    def update_preview(self):
        """Update the live preview based on the LaTeX input."""
        latex_code = self.latex_input.text()
        if latex_code:
            try:
                pixmap = self.latex_to_pixmap(latex_code)
                self.preview_label.setPixmap(pixmap)
                self.error_label.setText("")  # Clear any previous error messages
            except Exception as e:
                # Show only the first 3 lines of the error message
                error_message = str(e).splitlines()[:3]
                self.error_label.setText("\n".join(error_message))

    def latex_to_pixmap(self, latex_code, dpi=0):
        """Convert LaTeX to a QPixmap for display in the GUI without preamble."""
        try:
            plt.figure(figsize=(6, 2), dpi=dpi)  # Increased figure size for better display
            plt.text(0.5, 0.5, f"$${latex_code}$$", fontsize=20, ha='center', va='center')
            plt.axis('off')

            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
            buffer.seek(0)  # Rewind the buffer to the beginning

            # Convert buffer to QPixmap
            image = Image.open(buffer)
            qimg = QImage(image.tobytes(), image.width, image.height, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimg)

            buffer.close()
            plt.close()
            return pixmap

        except Exception as e:
            raise ValueError(f"Failed to render LaTeX: {str(e)}")

    def save_png(self):
        """Save the current LaTeX equation as a PNG file and log it to a text file."""
        latex_code = self.latex_input.text()
        if latex_code:
            try:
                self.latex_to_png(latex_code)
                self.latex_to_svg(latex_code)
                self.log_latex(latex_code)  # Log LaTeX to file
                self.error_label.setText("PNG saved successfully.")  # Show success message
            except Exception as e:
                # Show only the first 3 lines of the error message
                error_message = str(e).splitlines()[:3]
                self.error_label.setText("\n".join(error_message))

    def latex_to_svg(self, latex_code, output_path='output.svg', image_size=(100, 25), dpi=1200):
      """Convert LaTeX to SVG and save to a file with high DPI."""
      try:
          # Create a temporary figure to measure text size
          fig_temp, ax_temp = plt.subplots()
          fig_temp.patch.set_visible(False)
          ax_temp.axis('off')
          text = ax_temp.text(0.5, 0.5, f"${latex_code}$", fontsize=20, ha='center', va='center', usetex=True)
          fig_temp.tight_layout(pad=0)
          
          # Measure text size
          bbox_temp = text.get_window_extent(renderer=fig_temp.canvas.get_renderer())
          bbox_temp = bbox_temp.transformed(fig_temp.dpi_scale_trans.inverted())
          width, height = bbox_temp.width, bbox_temp.height
          
          # Calculate figure size in inches based on desired DPI
          fig_width_inch = image_size[0] / dpi
          fig_height_inch = image_size[1] / dpi
          
          # Close the temporary figure
          plt.close(fig_temp)
          
          # Create the final figure with high DPI
          fig, ax = plt.subplots(figsize=(fig_width_inch, fig_height_inch), dpi=dpi)
          ax.text(0.5, 0.5, f"${latex_code}$", fontsize=20, ha='center', va='center', usetex=True)
          ax.axis('off')
          plt.tight_layout(pad=0)
          
          # Save to buffer
          buffer = BytesIO()
          plt.savefig(buffer, format='svg', bbox_inches='tight', pad_inches=0, transparent=True)
          buffer.seek(0)
          
          # Save the SVG image
          with open(output_path, 'wb') as f:
              f.write(buffer.getvalue())
          
          plt.close()
          
      except Exception as e:
          raise ValueError(f"Failed to save SVG: {str(e)}")
      
    def latex_to_png(self, latex_code, output_path='output.png', dpi=1200):
        """Convert LaTeX to PNG and save to a file with preamble and postamble."""
        try:
            # Create a temporary figure to measure text size
            fig_temp, ax_temp = plt.subplots()
            fig_temp.patch.set_visible(False)
            ax_temp.axis('off')
            text = ax_temp.text(0.5, 0.5, f"${latex_code}$", fontsize=10, ha='center', va='center', usetex=True)
            fig_temp.tight_layout(pad=0)
            
            # Measure text size
            bbox_temp = text.get_window_extent(renderer=fig_temp.canvas.get_renderer())
            bbox_temp = bbox_temp.transformed(fig_temp.dpi_scale_trans.inverted())
            width, height = bbox_temp.width, bbox_temp.height
            
            # Close the temporary figure
            scale_factor = 50
            plt.close(fig_temp)
            # Create the final figure with the exact size needed
            fig, ax = plt.subplots(figsize=(width/scale_factor, height/scale_factor), dpi=dpi)
            ax.text(0.5, 0.5, f"${latex_code}$", fontsize=10, ha='center', va='center', usetex=True)
            ax.axis('off')
            plt.tight_layout(pad=0)
            
            # Save to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0.5, transparent=True, dpi=1200)
            buffer.seek(0)
            
            # Open the image and crop to fit the equation
            image = Image.open(buffer)
            image = image.convert("RGBA")  # Ensure image is in RGBA format
            
            # Find bounding box of non-white areas
            bbox = image.getbbox()
            if bbox:
                image = image.crop(bbox)
            
            # new_size = (int(image.width /scale_factor), int(image.height /scale_factor))
            # image = image.resize(new_size, Image.LANCZOS, dpi=(1200, 1200))
            
            # Save the cropped image
            image.save(output_path, format='png', dpi=(1200, 1200))
            plt.close()
            
        except Exception as e:
            raise ValueError(f"Failed to save PNG: {str(e)}")

    def log_latex(self, latex_code, log_file='latex_log.txt'):
        """Append the LaTeX string to a log file."""
        try:
            with open(log_file, 'a') as file:
                file.write(latex_code + '\n')
        except Exception as e:
            self.error_label.setText(f"Error logging LaTeX: {str(e)}")


    def svg_to_png_with_inkscape(svg_path, png_path, height, dpi=1200):
        """
        Convert SVG to PNG using Inkscape with specified height, preserving aspect ratio.

        Parameters:
        - svg_path: Path to the input SVG file.
        - png_path: Path to the output PNG file.
        - height: Desired height of the output PNG in pixels.
        - dpi: DPI for the output PNG.
        """
        try:
            # First, get the dimensions of the SVG file
            with Image.open(svg_path) as img:
                # Calculate aspect ratio
                aspect_ratio = img.width / img.height
                width = int(height * aspect_ratio)
            
            # Construct the Inkscape command
            command = [
                'inkscape',  # Command to invoke Inkscape
                svg_path,    # Input SVG file
                '--export-type=png',  # Export format
                f'--export-filename={png_path}',  # Output PNG file
                f'--export-width={width}',  # Set width based on height and aspect ratio
                f'--export-height={height}',  # Set height
                f'--export-dpi={dpi}',  # Set DPI
                '--export-background-opacity=0'  # Transparent background
            ]
            
            # Run the command
            subprocess.run(command, check=True)
            
            print(f"Successfully converted {svg_path} to {png_path} with height {height} pixels and {dpi} DPI.")
        
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while converting SVG to PNG: {e}")
        except Exception as e:
            print(f"Error occurred: {e}")


    def process_all_latex(self):
        """Generate images for all LaTeX strings in the log file and save them in the 'auto/' folder."""
        log_file = 'latex_log.txt'
        output_dir = 'auto/'
        
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        try:
            with open(log_file, 'r') as file:
                latex_strings = file.readlines()
            
            for index, latex_code in enumerate(latex_strings):
                latex_code = latex_code.strip()
                if latex_code:  # Skip empty lines
                    output_path_png = os.path.join(output_dir, f'equation_{index + 1}.png')
                    self.latex_to_png(latex_code, output_path_png)
                    # output_path = os.path.join(output_dir, f'equation_{index + 1}.svg')
                    # self.latex_to_svg(latex_code, output_path)
                    # self.svg_to_png_with_inkscape(output_path, output_path_png, 150)
            self.error_label.setText("All LaTeX strings processed successfully.")
        
        except Exception as e:
            # Show only the first 3 lines of the error message
            error_message = str(e).splitlines()[:3]
            self.error_label.setText("\n".join(error_message))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LatexPreviewApp()
    sys.exit(app.exec_())
