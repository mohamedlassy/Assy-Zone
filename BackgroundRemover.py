import requests
from tkinter import Tk, Label, Button, filedialog, messagebox, PhotoImage, Toplevel, Canvas
from PIL import Image, ImageTk
import os
from datetime import datetime
import io
from tqdm import tqdm

# تكوين مفتاح API
API_KEY = 'vzPnZevrRuMwi26CwDs4hqa8'

# إعداد نافذة واجهة المستخدم
window = Tk()
window.title("Background Remover")
window.geometry("650x750")
window.configure(bg="#f0f2f5")

# العنوان الرئيسي
title_label = Label(window, text="Background Remover", font=("Arial", 28, "bold"), fg="#4CAF50", bg="#f0f2f5")
title_label.pack(pady=30)

# اختيار الصورة من الجهاز
image_path = None
original_image = None  # To store the original image for preview


def select_image():
    global image_path, original_image
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
    if image_path:
        # Show image preview
        image_label.config(text=f"Selected Image: {os.path.basename(image_path)}", fg="#007acc")
        preview_image(image_path)


def preview_image(image_path):
    global original_image
    try:
        original_image = Image.open(image_path)
        preview = original_image.resize((250, 250))  # Resize for preview
        preview_image_tk = ImageTk.PhotoImage(preview)

        # Display preview
        if 'preview_label' in globals():
            preview_label.config(image=preview_image_tk)
            preview_label.image = preview_image_tk  # Keep a reference to the image
        else:
            preview_label = Label(window, image=preview_image_tk, bg="#f0f2f5")
            preview_label.pack(pady=20)
            preview_label.image = preview_image_tk  # Keep a reference to the image
    except Exception as e:
        messagebox.showerror("Error", f"Error displaying image preview: {e}")


# زر اختيار الصورة
select_button = Button(window, text="Choose Image", command=select_image, font=("Arial", 14), bg="#4CAF50", fg="white",
                       relief="flat", width=20, height=2)
select_button.pack(pady=20)

image_label = Label(window, text="No image selected", font=("Arial", 12), bg="#f0f2f5", fg="#333")
image_label.pack(pady=10)

# شريط التحميل
progress_bar = Canvas(window, width=500, height=30, bg="#e6e6e6", bd=0, highlightthickness=0)
progress_bar.pack(pady=20)


# زر إزالة الخلفية
def remove_background():
    if not image_path:
        messagebox.showerror("Error", "Please select an image.")
        return

    status_label.config(text="Removing background...", fg="blue")
    window.update_idletasks()

    # تحديد مكان حفظ الصورة
    output_path = filedialog.asksaveasfilename(defaultextension=".png",
                                               filetypes=[("PNG files", "*.png"), ("All files", "*.*")])

    if not output_path:
        return  # If the user cancels the save dialog

    try:
        # Request to remove the background using remove.bg API
        with open(image_path, 'rb') as image_file:
            response = requests.post(
                "https://api.remove.bg/v1.0/removebg",
                files={"image_file": image_file},
                data={"size": "auto"},
                headers={"X-Api-Key": API_KEY},
                stream=True
            )

        if response.status_code == requests.codes.ok:
            # Simulate a loading progress (for illustration)
            total_size = int(response.headers.get('Content-Length', 0))
            chunk_size = 1024
            with open(output_path, 'wb') as out_file:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading image") as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        out_file.write(chunk)
                        pbar.update(len(chunk))  # Update progress bar

            status_label.config(text="Background removed and saved!", fg="green")
            messagebox.showinfo("Success", f"Image saved at: {output_path}")
            # Optionally, show a new preview of the output image
            preview_image(output_path)
        else:
            messagebox.showerror("Error", f"Error removing background: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# زر إزالة الخلفية
remove_button = Button(window, text="Remove Background", command=remove_background, font=("Arial", 16), bg="#28a745",
                       fg="white", relief="flat", width=20, height=2)
remove_button.pack(pady=30)

# شريط الحالة أسفل الواجهة
status_label = Label(window, text="Status: Ready", font=("Arial", 14), bg="#f0f2f5", fg="#333")
status_label.pack(pady=10)


# زر إعادة تعيين
def reset_application():
    global image_path, original_image
    image_path = None
    original_image = None
    image_label.config(text="No image selected", fg="#333")
    status_label.config(text="Status: Ready", fg="#333")
    if 'preview_label' in globals():
        preview_label.config(image='')
        preview_label.image = None
    # Reset progress bar
    progress_bar.delete("all")
    progress_bar.create_rectangle(0, 0, 500, 30, fill="#e6e6e6")


reset_button = Button(window, text="Reset", command=reset_application, font=("Arial", 14), bg="#dc3545", fg="white",
                      relief="flat", width=20, height=2)
reset_button.pack(pady=10)

# تذييل التطبيق
footer_label = Label(window, text="By Mohamed Assy", font=("Arial", 12, "italic"), bg="#f0f2f5", fg="gray")
footer_label.pack(side="bottom", pady=20)

# تشغيل واجهة المستخدم
window.mainloop()
