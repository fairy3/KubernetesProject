from pathlib import Path
from matplotlib.image import imread, imsave
import numpy as np
import random
import copy


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


class Img:

    def __init__(self, path):
        self.path = Path(path)
        self.data = imread(path)

    def save_img(self):
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        imsave(new_path, self.data, cmap='gray')
        return new_path

    def blur(self, blur_level=32):
        self.data = rgb2gray(self.data).tolist()
        height = len(self.data)
        width = len(self.data[0])
        filter_sum = blur_level ** 2

        result = []
        for i in range(height - blur_level + 1):
            row_result = []
            for j in range(width - blur_level + 1):
                sub_matrix = [row[j:j + blur_level] for row in self.data[i:i + blur_level]]
                average = sum(sum(sub_row) for sub_row in sub_matrix) // filter_sum
                row_result.append(average)
            result.append(row_result)

        self.data = result

    def contour(self):
        self.data = rgb2gray(self.data).tolist()
        for i, row in enumerate(self.data):
            res = []
            for j in range(1, len(row)):
                res.append(abs(row[j - 1] - row[j]))

            self.data[i] = res

    def rotate(self):
        rotated_matrix = np.rot90(self.data, k=2)  # for 90 degrees: np.rot90(self.data, k=-1)
        self.data = rotated_matrix

    def salt_n_pepper(self):
        self.data = copy.deepcopy(self.data)
        height = len(self.data)
        width = len(self.data[0])

        for y in range(height):
            for x in range(width):
                rand_num = random.random()
                if rand_num < 0.2:
                    self.data[y][x] = 255
                elif rand_num > 0.8:
                    self.data[y][x] = 0

    def concat(self, other_img, direction='horizontal'):
        direction = direction.lower()
        if direction == 'horizontal':
            self_height = len(self.data)
            other_height = len(other_img.data)
            if self_height != other_height:
                raise ValueError("Horizontal concatenation is impossible when images have different heights")
            else:
                concatenated_h = np.concatenate((self.data, other_img.data), axis=1)
                self.data = concatenated_h

        elif direction == 'vertical':
            self_width = len(self.data[0])
            other_width = len(other_img.data[0])
            if self_width != other_width:
                raise ValueError("Vertical concatenation is impossible when images have different width")
            else:
                concatenated_v = np.vstack((self.data, other_img.data))
                self.data = concatenated_v
        else:
            raise ValueError("Invalid direction. Supported directions are 'horizontal' and 'vertical'.")

    def segment(self):
        self.data = copy.deepcopy(self.data)

        image_array = np.array(self.data)

        height = len(self.data)
        width = len(self.data[0])

        for y in range(height):
            for x in range(width):
                intensity = sum(image_array[y, x]) / 3
                if intensity > 100:
                    self.data[y][x] = 255
                else:
                    self.data[y][x] = 0
