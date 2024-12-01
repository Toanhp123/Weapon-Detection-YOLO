import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

# Hàm phát hiện đối tượng bằng YOLOv8
def detect_objects(image_path):
    image_orig = cv2.imread(image_path)
    yolo_model = YOLO('./best2.pt')
    results = yolo_model(image_orig)
    detected = False  # Cờ phát hiện đối tượng
    detected_classes = set()  # Sử dụng set để chỉ lưu các lớp vũ khí duy nhất

    for result in results:
        classes = result.names
        cls = result.boxes.cls
        conf = result.boxes.conf
        detections = result.boxes.xyxy

        for pos, detection in enumerate(detections):
            if conf[pos] >= 0.5:
                detected = True
                class_name = classes[int(cls[pos])]
                detected_classes.add(class_name)  # Chỉ lưu loại vũ khí duy nhất

                xmin, ymin, xmax, ymax = detection
                color = (0, 255, 0)

                font_scale = max(0.5, image_orig.shape[0] / 750)
                thickness = max(1, image_orig.shape[0] // 500)

                # Vẽ bounding box nhưng không vẽ nhãn nữa
                cv2.rectangle(image_orig, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 2)

    result_path = "./detected_image.jpg"
    cv2.imwrite(result_path, image_orig)
    return result_path, detected, detected_classes

# Hàm chọn ảnh
def choose_image():
    global img, image_path
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if image_path:
        reset(False)
        img = Image.open(image_path)
        img = img.resize((600, 400))  # Resize ảnh để phù hợp giao diện
        img_tk = ImageTk.PhotoImage(img)
        canvas.itemconfig(image_item, image=img_tk)
        canvas.image = img_tk
        result_label.config(text="Ấn nút phát hiện để kiểm tra", fg="black")


# Hàm phát hiện đối tượng
def detect():
    if not image_path:
        result_label.config(text="Hãy chọn một ảnh trước!", fg="red")
        return
    result_path, detected, detected_classes = detect_objects(image_path)

    # Cập nhật label kết quả
    if detected:
        result_label.config(text="Phát hiện đối tượng: " + ", ".join(detected_classes), fg="red")
    else:
        result_label.config(text="Không phát hiện đối tượng nguy hiểm.", fg="green")

    img_result = Image.open(result_path)
    img_result = img_result.resize((600, 400))  # Resize ảnh kết quả
    img_tk_result = ImageTk.PhotoImage(img_result)
    canvas.itemconfig(image_item, image=img_tk_result)
    canvas.image = img_tk_result

# Hàm lưu ảnh
def save_image():
    if not os.path.exists("./detected_image.jpg"):
        result_label.config(text="Không có ảnh kết quả để lưu!", fg="red")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                             filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
    if save_path:
        os.rename("./detected_image.jpg", save_path)
        result_label.config(text="Ảnh đã được lưu!", fg="green")

# Hàm reset giao diện
def reset(delete = True):
    global img, image_path
    if delete == True:
        image_path = ""  # Reset đường dẫn ảnh
    canvas.itemconfig(image_item, image="")
    canvas.image = None

    # Xóa ảnh đã detect (nếu có)
    if os.path.exists("./detected_image.jpg"):
        os.remove("./detected_image.jpg")

    result_label.config(text="Chọn ảnh để kiểm tra", fg="black")

# Tạo giao diện
root = tk.Tk()
root.title("Phát hiện vũ khí - Ứng dụng YOLOv8")
root.geometry("1200x720")

# Căn giữa cửa sổ
window_width = 1200
window_height = 720
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

root.configure(bg="#f0f0f0")  # Màu nền

# Tiêu đề
title = tk.Label(root, font=("Helvetica", 24, "bold"), bg="#f0f0f0", fg="#333")
title.pack(pady=10)

# Khung hiển thị ảnh
canvas = tk.Canvas(root, width=600, height=400, bg="gray", highlightthickness=1, highlightbackground="#ccc")
canvas.pack(pady=20)
image_item = canvas.create_image(300, 200, image=None)

# Label để hiển thị kết quả
result_label = tk.Label(root, text="Chọn ảnh để kiểm tra", font=("Helvetica", 16), bg="#f0f0f0", fg="black")
result_label.pack(pady=20)

# Khung chứa các nút
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=10)

btn_choose = tk.Button(button_frame, text="Chọn ảnh", command=choose_image, font=("Helvetica", 14), bg="#007bff", fg="white", width=15)
btn_choose.grid(row=0, column=0, padx=10)

btn_detect = tk.Button(button_frame, text="Phát hiện", command=detect, font=("Helvetica", 14), bg="#28a745", fg="white", width=15)
btn_detect.grid(row=0, column=1, padx=10)

btn_save = tk.Button(button_frame, text="Lưu ảnh", command=save_image, font=("Helvetica", 14), bg="#ffc107", fg="black", width=15)
btn_save.grid(row=0, column=2, padx=10)

btn_reset = tk.Button(button_frame, text="Reset", command=reset, font=("Helvetica", 14), bg="#dc3545", fg="white", width=15)
btn_reset.grid(row=1, column=0, columnspan=3, pady=10)

# Khởi chạy ứng dụng
image_path = ""

# Xóa cache
reset()

root.mainloop()