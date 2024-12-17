import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image App")

        self.create_widgets()

    def create_widgets(self):
        self.open_button = tk.Button(self.root, text="Открыть изображение", command=self.open_image)
        self.open_button.pack(pady=10)

        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack()

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", ".jpg .jpeg .png .bmp .webp")])
        if file_path:
            img = Image.open(file_path)

            img_tk = ImageTk.PhotoImage(img)
            label = tk.Label(self.image_frame, image=img_tk)
            label.image = img_tk
            label.grid(row=0, column=0, padx=5, pady=5)

            scaled_img = self.scale_nearest_neighbor(img, 2)
            scaled_img_tk = ImageTk.PhotoImage(scaled_img)
            label = tk.Label(self.image_frame, image=scaled_img_tk)
            label.image = scaled_img_tk
            label.grid(row=0, column=1, padx=5, pady=5)

            rotated_img = self.rotate_bilinear(img, -30)
            rotated_img_tk = ImageTk.PhotoImage(rotated_img)
            label = tk.Label(self.image_frame, image=rotated_img_tk)
            label.image = rotated_img_tk
            label.grid(row=1, column=0, padx=5, pady=5)

            skewed_img = self.bicubic_interpolation(img, 45)
            skewed_img_tk = ImageTk.PhotoImage(skewed_img)
            label = tk.Label(self.image_frame, image=skewed_img_tk)
            label.image = skewed_img_tk
            label.grid(row=1, column=1, padx=5, pady=5)

    def scale_nearest_neighbor(self, image, scale_factor):
        width, height = image.size
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        scaled_img = Image.new('RGB', (new_width, new_height))
        
        for x in range(new_width):
            for y in range(new_height):
                original_x = round(x / scale_factor)
                original_y = round(y / scale_factor)
                
                if 0 <= original_x < width and 0 <= original_y < height:
                    scaled_img.putpixel((x, y), image.getpixel((original_x, original_y)))

        left = (new_width - width) // 2
        top = (new_height - height) // 2
        right = (new_width + width) // 2
        bottom = (new_height + height) // 2

        cropped_img = scaled_img.crop((left, top, right, bottom))
        return cropped_img

    def rotate_bilinear(self, image, angle):
        angle = -angle  # Инвертируем угол для правильного вращения
        width, height = image.size
        angle_rad = np.radians(angle)
        cos_theta = np.cos(angle_rad)
        sin_theta = np.sin(angle_rad)

        # Новый размер холста
        new_width = int(abs(width * cos_theta) + abs(height * sin_theta))
        new_height = int(abs(width * sin_theta) + abs(height * cos_theta))

        rotated_img = Image.new('RGB', (new_width, new_height))

        cx = width // 2
        cy = height // 2
        ncx = new_width // 2
        ncy = new_height // 2

        # Выполняем поворот с билинейной интерполяцией
        for x in range(new_width):
            for y in range(new_height):
                original_x = (x - ncx) * cos_theta + (y - ncy) * sin_theta + cx
                original_y = -(x - ncx) * sin_theta + (y - ncy) * cos_theta + cy

                l = int(np.floor(original_x))
                k = int(np.floor(original_y))
                a = original_x - l
                b = original_y - k
                if 0 <= l < width and 0 <= k < height:
                    f_ll = image.getpixel((l, k))
                    f_l1 = image.getpixel((l + 1, k)) if l + 1 < width else f_ll
                    f_1k = image.getpixel((l, k + 1)) if k + 1 < height else f_ll
                    f_11 = image.getpixel((l + 1, k + 1)) if l + 1 < width and k + 1 < height else f_ll

                    pixel_value = (
                        (1 - a) * (1 - b) * f_ll[0] + a * (1 - b) * f_l1[0] + (1 - a) * b * f_1k[0] + a * b * f_11[0],
                        (1 - a) * (1 - b) * f_ll[1] + a * (1 - b) * f_l1[1] + (1 - a) * b * f_1k[1] + a * b * f_11[1],
                        (1 - a) * (1 - b) * f_ll[2] + a * (1 - b) * f_l1[2] + (1 - a) * b * f_1k[2] + a * b * f_11[2]
                    )

                    rotated_img.putpixel((x, y), tuple(map(int, pixel_value)))

        # Центрируем и обрезаем изображение до исходного размера
        left = (new_width - width) // 2
        top = (new_height - height) // 2
        right = (new_width + width) // 2
        bottom = (new_height + height) // 2

        cropped_img = rotated_img.crop((left, top, right, bottom))
        return cropped_img


    def bicubic_interpolation(self, image, angle):
        width, height = image.size
        angle_rad = np.radians(angle)
        skew_matrix = (1, np.tan(angle_rad), 0, 0, 1, 0)
        skewed_img = image.transform((width, height), Image.AFFINE, skew_matrix, resample=Image.BICUBIC)
        return skewed_img

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()
