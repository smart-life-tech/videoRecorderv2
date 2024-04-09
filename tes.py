import tkinter as tk
import cv2
from PIL import Image, ImageTk
from tkinter import filedialog,ttk
import threading
from tkinter import messagebox
import os

def get_camera_index():
    # Try different camera indexes
    print("pinging all cameras wait a bit")
    detected_indexes = []
    for index in range(5):  # Adjust the range as needed
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            # Release the capture device
            cap.release()
            detected_indexes.append(index)
    return detected_indexes
    #return None  # No camera detected

class VideoRecorder:
    def __init__(self, camera_index, output_path,prefix):
        self.camera_index = camera_index
        self.prefix = prefix
        self.output_paths = output_path
        self.active_shot = None
        self.recording = False

    def start_recording(self):
        #output_path = self.output_paths[self.active_shot]
        self.recording = True
        self.capture = cv2.VideoCapture(self.camera_index,cv2.CAP_VFW)
        self.writer = cv2.VideoWriter(self.output_paths, cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))

        while self.recording:
            if self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    self.writer.write(frame)

    def stop_recording(self):
        self.recording = False
        self.capture.release()
        self.writer.release()

class VideoRecorderApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Video Recorder")
        self.geometry("800x600")

        self.active_shot = tk.StringVar()
        self.prefix = tk.StringVar()
        self.destination_folder = tk.StringVar()
        self.recording = False
        self.recording_threads = None
        self.recorders = None
        self.output_paths =None
        self.recordStart=False
        self.shot_completed=False
        self.writing=True
        # Initialize take number
        self.take_number = 1
        self.width = 1920 #adjust the number here
        self.height = 1080 #adjust the height too
        # Left side
        left_frame = tk.Frame(self, bg="black", width=400, height=600)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        self.camera_labels = []
        self.video_captures = [None] * 4
        # Create a list to store Combobox widgets
        self.camera_dropdowns = []
        camera_indexes=get_camera_index()
        self.selected_cameras = {index: 0 for index in [0, 1, 2, 3]}  # Dictionary to store selected cameras for each grid
        for i, camera_index in enumerate([0, 1, 2, 3]):
            print(camera_index)
            row = i // 2  # Calculate row index based on current iteration
            col = i % 2   # Calculate column index based on current iteration

            camera_frame = tk.Label(left_frame, bg="white", relief=tk.SUNKEN, width=50, height=20)
            camera_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
             # Dropdown menu for camera selection
            # Dropdown menu for camera selection
            self.options = [f"Camera {index}" for index in camera_indexes]
            self.options.append("None")  # Add "None" option
            self.dropdown = ttk.Combobox(left_frame, values=self.options)
            self.dropdown.current(len(self.options) - 1)  # Set default selection to "None"
            self.dropdown.grid(row=(row), column=(col), padx=10,pady=(0, 10), sticky="n")
            self.camera_labels.append(camera_frame)
            #print(self.camera_labels)
             # Bind a callback function to the dropdown menu
            self.dropdown.bind("<<ComboboxSelected>>", lambda event, index=camera_index: self.dropdown_callback(event, index))

            # Add the Combobox widget to the list
            self.camera_dropdowns.append(self.dropdown)
        print(self.camera_labels)

        # Right side
        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        active_shot_label = tk.Label(right_frame, text="Active Shot:", bg="black", fg="white")
        active_shot_label.pack()

        active_shot_entry = tk.Entry(right_frame, textvariable=self.active_shot)
        active_shot_entry.pack()

        prefix_label = tk.Label(right_frame, text="Prefix:", bg="black", fg="white")
        prefix_label.pack()

        prefix_entry = tk.Entry(right_frame, textvariable=self.prefix)
        prefix_entry.pack()

        choose_destination_button = tk.Button(right_frame, text="Choose Destination", command=self.choose_destination)
        choose_destination_button.pack()

        self.record_button = tk.Button(right_frame, text="Record", command=self.record)
        self.record_button.pack()

        complete_shot_button = tk.Button(right_frame, text="Complete Shot", command=self.complete_shot)
        complete_shot_button.pack()
        self.shot_listbox = tk.Listbox(right_frame, selectmode=tk.SINGLE)
        self.shot_listbox.pack(fill=tk.BOTH, expand=True)
        load_shots_button = tk.Button(right_frame, text="Load Shots", command=self.load_shots)
        load_shots_button.pack()

        # In the create_widgets method:
        self.shot_listbox.bind("<<ListboxSelect>>", self.on_shot_select)
        # Specify camera indexes for the connected USB cameras
        # Get the automatically detected camera index
        camera_index = camera_indexes
        if camera_index is not None:
            print("Automatically detected camera index:", camera_index)
        else:
            print("No camera device detected.")
        self.camera_indexes = camera_index  # Change these values according to your setup

        # Capture frames from USB cameras
        self.captures = self.capture_frames(self.camera_indexes)
        print("captures :" ,self.captures)

        # Update video feed
        self.update_video_feed()
    
    
    # Callback function for dropdown menu selection
    def dropdown_callback(self, event, camera_index):
        print(camera_index)
        selected_value = self.camera_dropdowns[camera_index].get()
        if selected_value == "None":
            self.selected_cameras[camera_index] = None
            print("Camera index", camera_index, "set to None")
        else:
            self.selected_cameras[camera_index] = selected_value
            if self.selected_cameras[camera_index] =='Camera 0':
                selected_value = 0
            if self.selected_cameras[camera_index] =='Camera 1':
                selected_value = 1
            if self.selected_cameras[camera_index] =='Camera 2':
                selected_value = 2
            if self.selected_cameras[camera_index] =='Camera 3':
                selected_value = 4
            print("Camera index", camera_index, "set to", selected_value)
        
            selected_camera_index = self.camera_dropdowns[camera_index].current()

            # Check if the selected camera index is already in use
            if selected_camera_index < 0 or selected_camera_index >= 4:
                return
            selected_value=int(selected_value)

    def update_preview(self, index):
        capture = self.video_captures[index]
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
        
    def record(self):
        if not self.recording:
            self.start_recording()
            
            
        else:
            self.stop_recording()
            self.recording=False
            self.shot_completed=True
            self.record_button.config(text="Record")
            # Change record button color back to its default color
            self.record_button.config(bg="white")
            
            

    def start_recording(self):
        # Check if destination folder is chosen
        if not self.destination_folder:
            messagebox.showerror("Error", "Please choose a destination folder.")
            return

        # Check if active shot is selected
        if not self.active_shot.get():
            messagebox.showerror("Error", "Please select an active shot.")
            return

        # Get the camera indexes for all connected cameras
        camera_indexes = self.camera_indexes

       # Construct the output paths for each camera using the prefix and active shot
        # Construct the output paths for each camera using the prefix, active shot, and take number
        self.output_paths = [os.path.join(self.destination_folder.get(), f"{self.prefix.get()}_Shot_{self.active_shot.get()}_Take_{self.take_number}_Camera_{i}.mp4") for i in range(4)]
        """
        # Create a VideoRecorder instance for each camera
        recorders = [VideoRecorder(camera_indexes[i], output_paths[i],self.prefix.get()) for i in range(len(camera_indexes))]

        # Start recording on each recorder in separate threads
        recording_threads = [threading.Thread(target=recorder.start_recording) for recorder in recorders]
        for thread in recording_threads:
            thread.start()

        # Store the recorder instances and recording threads for later use
        self.recorders = recorders
        self.recording_threads = recording_threads
        """
        ###print(self.output_paths)
        #self.recorder = MultiCamRecorder(camera_indexes, output_paths)
        #self.recorder.record()
        self.recordStart=True
        self.record_button.config(text="Stop Record")
        # Change record button color to red
        self.record_button.config(bg="red")
        self.recording=True
        print("recording started")
        self.take_number=self.take_number+1
        #messagebox.showinfo("Info", "recording started")


    def stop_recording(self):
        print("Recording stopped")
        #messagebox.showinfo("Info", "recording stopped")
        

              
    def update_active_shot(self, event):
        selected_shot_index = self.shot_listbox.curselection()
        if selected_shot_index:
            selected_shot = self.shot_listbox.get(selected_shot_index[0])
            self.active_shot.set(selected_shot)

    def choose_destination(self):
        self.destination_folder.set(filedialog.askdirectory())
        if self.destination_folder:
            self.output_paths = [f"{self.destination_folder}/{self.prefix}_0.avi",
                                 f"{self.destination_folder}/{self.prefix}_1.avi",
                                 f"{self.destination_folder}/{self.prefix}_2.avi",
                                 f"{self.destination_folder}/{self.prefix}_3.avi"]

    def on_shot_select(self, event):
        selected_index = self.shot_listbox.curselection()
        if selected_index:
            self.active_shot.set(self.shot_listbox.get([selected_index[0]]))

    def load_shots(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.xlsx")])
        if file_path:
            with open(file_path, 'r') as file:
                self.shot_names = [line.strip() for line in file.readlines()]
            self.update_shot_listbox()

    def update_shot_listbox(self):
        self.shot_listbox.delete(0, tk.END)
        for shot_name in self.shot_names:
            self.shot_listbox.insert(tk.END, shot_name)

    def complete_shot(self):
        print("complete shot button pressed")
        #self.stop_recording()
        self.shot_completed=True
        selected_index = self.shot_listbox.curselection()
        if selected_index:
            del self.shot_names[selected_index[0]]
            self.update_shot_listbox()

        
        messagebox.showinfo("Info", "recording in progress completed, shot deleted")

    def check_completion(self, event, wait_thread):
        print("checking completion")
        for recorder in self.recorders:
            print("checking completion stopped")
            recorder.stop_recording()  # Stop recording on each recorder instance
                
        if self.completion_event.is_set():
            print("event is set")
            # All recording threads have completed
            self.wait_thread.join()  # Join the wait thread
            for recorder in self.recorders:
                print("checking completion stopped")
                recorder.stop_recording()  # Stop recording on each recorder instance
        else:
            print("event is not set")
            # Wait for another 100ms before checking again
            #self.after(100, self.check_completion, event, wait_thread)

            

    def capture_frames(self, camera_indexes):
        captures = []
        for index in camera_indexes:
            print(index)
            capture = cv2.VideoCapture(index)
            if camera_indexes !=3:
                captures.append(capture)
            if camera_indexes==3:
                captures.append(4)
            capture.release()
        print(captures[0].get(cv2.CAP_PROP_FRAME_WIDTH))
        print(captures[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
         #width= int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                #height= int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return captures

    def update_video_feed(self):
            
        for i,(capture, label)  in enumerate (zip(self.captures, self.camera_labels)):
           
            ret, frame = cv2.VideoCapture(0).read()
            if ret:
                label = self.camera_labels[0]
                # Convert frame from BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Resize frame to fit label size
                frame_resized = cv2.resize(frame_rgb, (300, 200))
                # Convert frame to ImageTk format
                img = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))
                # Update label with new image
                label.config(image=img)
                label.image = img
                
                width= int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                height= int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                #width= self.width #uncomment for the custom height
                #height= self.height
                #print(width,height)
                if self.output_paths is not None and self.recordStart:
                    #print(self.output_paths[0])
                    global writer,writer2,writer3,writer4
                    if self.writing:
                        if self.selected_cameras[0] is not None:
                            print("writing",self.output_paths[0])
                            writer= cv2.VideoWriter(self.output_paths[0], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height))
                        if len(self.captures)>=2 and self.selected_cameras[1] is not None:
                            writer2= cv2.VideoWriter(self.output_paths[1], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height))
                        if len(self.captures)>=3 and self.selected_cameras[2] is not None:
                            writer3= cv2.VideoWriter(self.output_paths[2], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height))
                        if len(self.captures)>=4 and self.selected_cameras[3] is not None:
                            writer4= cv2.VideoWriter(self.output_paths[3], cv2.VideoWriter_fourcc(*'mp4v'), 20, (width,height))
                        self.writing=False
                    if i==0 and self.selected_cameras[0] is not None:
                        #print("recording on cam0")
                        writer.write(frame)
                    if i==1 and len(self.captures)>=2 and self.selected_cameras[1] is not None:
                        writer2.write(frame)
                    if i==2  and len(self.captures)>=3 and self.selected_cameras[2] is not None:
                        writer3.write(frame)
                    if i==3 and len(self.captures)>=4 and self.selected_cameras[3] is not None:
                        writer4.write(frame)
                if self.shot_completed:
                    #print(len(self.captures))
                    if len(self.captures)>=1 and  self.selected_cameras[0] is not None:
                        print("release writer")
                        writer.release()
                    if len(self.captures)>=2:
                        writer2.release()
                    if len(self.captures)>=3:    
                        writer3.release()
                    if len(self.captures)>=4:
                        writer4.release()
                    self.recordStart=False
                    self.shot_completed=False
                    self.writing=True
                            
        self.after(10, self.update_video_feed)
        
if __name__ == "__main__":
    app = VideoRecorderApp()
    app.mainloop()
