import tkinter as tk
import cv2
from PIL import Image, ImageTk

class CameraPreviewApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera Previews")

        # Create labels for camera previews
        self.camera_labels = []
        for i in range(4):
            label = tk.Label(self.root, borderwidth=2, relief="solid")
            label.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            self.camera_labels.append(label)

        # Start capturing frames from cameras
        self.capture_frames()

        self.root.mainloop()

    def capture_frames(self):
        # Open the first four cameras available
        self.captures = [cv2.VideoCapture(i) for i in range(4)]

        # Continuously update camera previews
        self.update_previews()

    def update_previews(self):
        # Read a frame from each camera and display it
        for i, capture in enumerate(self.captures):
            ret, frame = capture.read()
            if ret:
                # Convert frame from BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Resize frame to fit label size
                frame_resized = cv2.resize(frame_rgb, (300, 200))
                # Convert frame to ImageTk format
                img = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))
                # Update label with new image
                self.camera_labels[i].config(image=img)
                self.camera_labels[i].image = img

        # Schedule next update after 10 milliseconds
        self.root.after(10, self.update_previews)

# Create an instance of the application
app = CameraPreviewApp()
