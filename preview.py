import tkinter as tk
import cv2
from PIL import Image, ImageTk
from tkinter import ttk

class CameraPreviewApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera Previews")

        # Create labels and dropdowns for camera previews
        self.camera_labels = []
        self.camera_selections = []
        self.captures = [None] * 4  # Initialize with None values for 4 cameras

        for i in range(4):
            # Label for camera preview
            label = tk.Label(self.root, borderwidth=2, relief="solid")
            label.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            self.camera_labels.append(label)
            row = i // 2  # Calculate row index based on current iteration
            col = i % 2   # Calculate column index based on current iteration
            # Dropdown menu for camera selection
            dropdown = ttk.Combobox(self.root, values=[f"Camera {j}" for j in range(4)], state="readonly")
            dropdown.current(i)  # Set default selection to current camera index
            dropdown.grid(row=(row), column=(col), padx=10,pady=(0, 10), sticky="n")
            dropdown.bind("<<ComboboxSelected>>", lambda event, index=i: self.dropdown_callback(event, index))
            self.camera_selections.append(dropdown)

        self.root.mainloop()

    def dropdown_callback(self, event, index):
        selected_camera_index = self.camera_selections[index].current()

        # Check if the selected camera index is already in use
        if selected_camera_index < 0 or selected_camera_index >= 4:
            return
        
        # Release the current capture if it's not None
        if self.captures[index] is not None:
            self.captures[index].release()
        
        # Open the selected camera index
        self.captures[index] = cv2.VideoCapture(selected_camera_index)
        
        # Start updating the preview for the selected camera
        self.update_preview(index)

    def update_preview(self, index):
        capture = self.captures[index]
        label = self.camera_labels[index]

        ret, frame = capture.read()
        if ret:
            # Convert frame from BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Resize frame to fit label size
            frame_resized = cv2.resize(frame_rgb, (300, 200))
            # Convert frame to ImageTk format
            img = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))
            # Update label with new image
            label.config(image=img)
            label.image = img

        # Schedule next update after 10 milliseconds
        self.root.after(10, lambda: self.update_preview(index))

# Create an instance of the application
app = CameraPreviewApp()
