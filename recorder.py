import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import cv2
import os
from PIL import Image, ImageTk

class VideoRecorderApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Video Recorder")
        self.geometry("800x600")

        self.active_shot = tk.StringVar()
        self.take_number = tk.IntVar(value=1)
        self.prefix = tk.StringVar()
        self.destination_folder = tk.StringVar()
        self.shot_names = []
        global right_frame
        right_frame = tk.Frame(self)
        self.create_widgets()
        
    def create_widgets(self):
        # Left side
        left_frame = tk.Frame(self, bg="black")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        shot_names_label = tk.Label(left_frame, text="Shot Names", bg="black", fg="white")
        shot_names_label.pack()

        self.shot_listbox = tk.Listbox(left_frame, selectmode=tk.SINGLE)
        self.shot_listbox.pack(fill=tk.BOTH, expand=True)

        prefix_label = tk.Label(left_frame, text="Prefix:", bg="black", fg="white")
        prefix_label.pack()

        prefix_entry = tk.Entry(left_frame, textvariable=self.prefix)
        prefix_entry.pack()

        choose_destination_button = tk.Button(left_frame, text="Choose Destination", command=self.choose_destination)
        choose_destination_button.pack()

        load_shots_button = tk.Button(left_frame, text="Load Shots", command=self.load_shots)
        load_shots_button.pack()

        complete_shot_button = tk.Button(left_frame, text="Complete Shot", command=self.complete_shot)
        complete_shot_button.pack()


        # Right side
        
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # Create rectangles for displaying camera feeds
        self.camera_labels = []
        self.video_captures = []
        self.active_sources = [0] * 4  # Default video sources for each panel
        for i in range(2):
            for j in range(2):
                camera_frame = tk.Label(right_frame, bg="white", relief=tk.SUNKEN, width=320, height=240)
                camera_frame.grid(row=i, column=j, padx=10, pady=10)
                while True:
                    # OpenCV code to capture frames from camera
                    cap = cv2.VideoCapture(0)  # Use appropriate camera index
                    ret, frame = cap.read()
                    if ret:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame = Image.fromarray(frame)
                        frame = ImageTk.PhotoImage(frame)
                        camera_frame.imgtk = frame
                        camera_frame.config(image=frame)
                        break

        self.video_sources = [tk.StringVar(value=f"Video Source {i+1}") for i in range(4)]
        # Start streaming video from cameras
        self.stream_videos(right_frame)


        active_shot_label = tk.Label(right_frame, text="Active Shot:", bg="black", fg="white")
        active_shot_label.grid(row=2, column=0, columnspan=2)

        active_shot_entry = tk.Entry(right_frame, state='readonly',textvariable=self.active_shot)
        active_shot_entry.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        record_button = tk.Button(right_frame, text="Record", command=self.record)
        record_button.grid(row=4, column=0, columnspan=2, pady=10)
        # In the create_widgets method:
        self.shot_listbox.bind("<<ListboxSelect>>", self.on_shot_select)
        # # Create rectangles for displaying camera feeds
        # Bind ButtonRelease-1 event to update active shot entry
        self.shot_listbox.bind("<ButtonRelease-1>", self.update_active_shot)
        self.after(10, self.update_video_feed, right_frame) 
    def update_active_shot(self, event):
        selected_shot_index = self.shot_listbox.curselection()
        if selected_shot_index:
            selected_shot = self.shot_listbox.get(selected_shot_index[0])
            self.active_shot.set(selected_shot)

    def choose_destination(self):
        self.destination_folder.set(filedialog.askdirectory())

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
        selected_index = self.shot_listbox.curselection()
        if selected_index:
            del self.shot_names[selected_index[0]]
            self.update_shot_listbox()

    
    async def record_from_source(self, source_index, shot_folder):
        video_capture = cv2.VideoCapture(source_index)
        out_path = os.path.join(shot_folder, f"{self.prefix.get()}_{self.active_shot.get()}_take{self.take_number.get()}_source{source_index+1}.mp4")
        out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            cv2.imshow(f"Video Source {source_index+1}", frame)
            out.write(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        out.release()
        cv2.destroyWindow(f"Video Source {source_index+1}")

    def stream_videos(self,right_frame):
        for cap, source_index in zip(self.video_captures, self.active_sources):
            cap.open(source_index)
            self.update_video_feed(right_frame)

    def update_video_feed(self, right_frame):
        print("updated feed")
        self.camera_labels = []
        self.video_captures = []
        self.active_sources = [0] * 4  # Default video sources for each panel
        for i in range(2):
            for j in range(2):
                camera_frame = tk.Label(right_frame, bg="white", relief=tk.SUNKEN, width=320, height=240)
                camera_frame.grid(row=i, column=j, padx=10, pady=10)
              
                 # OpenCV code to capture frames from camera
                cap = cv2.VideoCapture(0)  # Use appropriate camera index
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = Image.fromarray(frame)
                    frame = ImageTk.PhotoImage(frame)
                    camera_frame.imgtk = frame
                    camera_frame.config(image=frame)
        #self.after(10, self.update_video_feed, right_frame)                    
        

    def record(self):
        if not self.destination_folder.get():
            messagebox.showerror("Error", "Please choose a destination folder.")
            return

        if not self.active_shot.get():
            messagebox.showerror("Error", "Please select an active shot.")
            return

        async def record_async():
            shot_folder = os.path.join(self.destination_folder.get(), f"{self.prefix.get()}_{self.active_shot.get()}")
            os.makedirs(shot_folder, exist_ok=True)

           
if __name__ == "__main__":
    app = VideoRecorderApp()
    app.mainloop()
