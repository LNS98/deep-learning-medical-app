import SimpleITK as sitk
import matplotlib.pyplot as plt

def show(img_arr):
    img = plt.imshow(img_arr, cmap='gray');
    plt.axis('off')
    plt.colorbar(img)
    plt.show()
