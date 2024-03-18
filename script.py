import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QColorDialog, QDesktopWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image, ImageQt

def get_image_paths(folder_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in image_extensions]

def resize_image(image_path, target_width, target_height):
    image = Image.open(image_path)
    aspect_ratio = image.width / image.height
    new_height = min(target_height, int(target_width / aspect_ratio))
    new_width = int(new_height * aspect_ratio)
    if new_width > target_width:
        new_width = target_width
        new_height = int(new_width / aspect_ratio)
    return image.resize((new_width, new_height), Image.ANTIALIAS)

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super(ImageLabel, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):
        self.parent().swapImage(self)

class ImageSwapper(QWidget):
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.image_paths = get_image_paths(self.folder_path)
        self.current_images = random.sample(self.image_paths, 2)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Image Pairs')
        
        # Set window size to half the display height
        screen_geometry = QApplication.desktop().screenGeometry()
        window_height = screen_geometry.height() // 2
        self.setFixedSize(screen_geometry.width() // 2, window_height)
        
        self.mainLayout = QVBoxLayout()
        self.imageLayout = QHBoxLayout()
        
        self.imageLabel1 = ImageLabel(self)
        self.imageLabel2 = ImageLabel(self)
        self.imageLayout.addWidget(self.imageLabel1)
        self.imageLayout.addWidget(self.imageLabel2)
        
        self.controlLayout = QHBoxLayout()
        self.btnColor = QPushButton('Change Background Color', self)
        self.btnColor.clicked.connect(self.changeBackgroundColor)
        self.btnAdjust = QPushButton('Adjust Images', self)
        self.btnAdjust.clicked.connect(lambda: self.updateImages(force_update=True))
        self.controlLayout.addWidget(self.btnColor)
        self.controlLayout.addWidget(self.btnAdjust)
        
        self.mainLayout.addLayout(self.imageLayout)
        self.mainLayout.addLayout(self.controlLayout)
        
        self.setLayout(self.mainLayout)
        
        self.updateImages(force_update=True)
    
    def updateImages(self, force_update=False):
        padding = 10
        target_width = (self.size().width() - (3 * padding)) // 2
        target_height = self.size().height() - padding - self.controlLayout.sizeHint().height()
        
        for img_path, label in zip(self.current_images, [self.imageLabel1, self.imageLabel2]):
            image = resize_image(img_path, target_width, target_height)
            q_image = ImageQt.ImageQt(image)
            pixmap = QPixmap.fromImage(q_image)
            label.setPixmap(pixmap)
    
    def swapImage(self, label):
        new_img = random.choice(self.image_paths)
        if label == self.imageLabel1:
            self.current_images[0] = new_img
        else:
            self.current_images[1] = new_img
        self.updateImages(force_update=True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_J:
            self.current_images[0] = random.choice(self.image_paths)
            self.updateImages(force_update=True)
        elif event.key() == Qt.Key_K:
            self.current_images = random.sample(self.image_paths, 2)
            self.updateImages(force_update=True)
        elif event.key() == Qt.Key_L:
            self.current_images[1] = random.choice(self.image_paths)
            self.updateImages(force_update=True)
        elif event.key() == Qt.Key_S:
            self.saveCombination()

    def changeBackgroundColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.setStyleSheet(f"QWidget {{ background-color: {color.name()}; }}")

    def saveCombination(self):
        desktop_path = os.path.expanduser("~/Desktop")
        base_names = [os.path.splitext(os.path.basename(path))[0] for path in self.current_images]
        save_name = f"{'_'.join(base_names)}.jpg"
        save_path = os.path.join(desktop_path, save_name)
        images = [Image.open(path) for path in self.current_images]
        total_width = sum(image.width for image in images)
        max_height = max(image.height for image in images)
        combined = Image.new('RGB', (total_width, max_height))
        x_offset = 0
        for image in images:
            combined.paste(image, (x_offset,0))
            x_offset += image.width
        combined.save(save_path)
        print(f"Image saved to {save_path}")

def main():
    folder_path = 'images/'  # Update this path
    app = QApplication(sys.argv)
    ex = ImageSwapper(folder_path)
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
