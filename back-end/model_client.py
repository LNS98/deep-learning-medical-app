"""
Client that performs inferences on the tensorflow serving model using the REST API.
"""

# for pre/post-proccesing
import SimpleITK as sitk
from preprocessing.metadata import Patient
from preprocessing.preprocess import Preprocessor
from augmentation.augment_data import process
import numpy as np
from scipy.ndimage import zoom

# for getting requests
from predict_client.prod_client import ProdClient

# constants needed for pre-proccesding
record_shape = [37,99,99]
feature_shape = [31,87,87]


def get_prediction(coords, path_to_img, host):

    # account for papaya recieved image
    coords = change_coordinate_system(coords, path_to_img)
    # pre-process image so that it matches input of model
    processed_image = pre_process_image(coords, path_to_img)
    # specify where the client should look to make requests
    client = ProdClient(host+':9200', 'crohns', 1)

    # query tensorflow seriving model for predictions and attention layer
    prob_values, max_prob_indx, attentions = query_client(processed_image, client)

    # proccess the feature map to get the average and resize it
    feature_maps_arr = process_feature_maps(attentions, processed_image[0].shape)
    # make the attention layer into a nifit file
    make_feature_image(coords, path_to_img, feature_maps_arr)

    # produce an output string to display on front-end
    classes = {0: 'healthy', 1: 'abnormal (Crohn\'s)'}
    predictions = classes[max_prob_indx]
    output_str = f'{predictions} with probability {round(prob_values[0][max_prob_indx], 3)}'

    return output_str


def change_coordinate_system(coords, path_image):
    print(coords)

    # load original image and convert to numpy arr
    loaded_image = sitk.ReadImage(path_image)
    arr_fig_shape = sitk.GetArrayFromImage(loaded_image).shape

    # account for papaya's weird system of changing coordinates
    new_x = arr_fig_shape[1] - coords[0]
    new_y = coords[1]
    new_z = arr_fig_shape[0] - coords[2]

    print(new_x, new_y, new_z)

    return [new_y, new_x, new_z]


def process_feature_maps(attention_layer, processed_image_shape):
    # Get the mean of the feature maps
    attention_layer = attention_layer.mean(4)
    # Upsample the attention layer to 87, 87 size
    ratio = tuple(map(lambda x, y: x/y, processed_image_shape, attention_layer.shape))
    upsampled_attention_layer = zoom(attention_layer, ratio)

    return upsampled_attention_layer


def make_feature_image(coords, path, feature_maps_arr):
    # load original image and convert to numpy arr
    loaded_image = sitk.ReadImage(path)
    arr_fig = sitk.GetArrayFromImage(loaded_image).astype("float32")
    # add the maps
    new_arr = add_feature_arra_zero_arr(arr_fig, feature_maps_arr, coords, feature_shape)
    # make it into a nifit file with the same meta-data as original image
    make_arr_into_nifit_image(loaded_image, new_arr)


def add_feature_arra_zero_arr(arr_image, arr_feature_map, pixel_center, physical_crop_size):
    # compute box size
    box_size = np.array([physical_crop_size[1], physical_crop_size[2], physical_crop_size[0]]) # np.array([pcsz / vsz for vsz,pcsz in zip(image.GetSpacing(), physical_crop_size)])
    lb = np.array(pixel_center - box_size/2).astype(int)  # lower corner of cropped box
    ub = (lb + box_size).astype(int)  # upper corner of cropped box
    # fully convert lower bound to Python (=!numpy) format, s.t. it can be used by SITK
    lb = list(lb)
    lb = [int(lower_b) for lower_b in lb]

    # noramlise feature array and fill original image zeros
    arr_feature_map = (arr_feature_map - arr_feature_map.min()) / (arr_feature_map.max() - arr_feature_map.min())
    arr_image = np.zeros(arr_image.shape)

    # get data of cropped box region
    arr_image[lb[2]:ub[2], lb[0]:ub[0], lb[1]:ub[1]] = arr_feature_map # place the feature map at the given location

    return arr_image.astype(np.float32)

def make_arr_into_nifit_image(base_image, new_image_arr):
    # make the new image array a sitk Image
    feature_map_image = sitk.GetImageFromArray(new_image_arr)
    feature_map_image.CopyInformation(base_image)
    # write to file
    sitk.WriteImage(feature_map_image, './feature_map_image.nii')


def pre_process_image(coords, path_to_img):

    # pre-proccess image as per Robbie Holland's code
    patient = Patient('A', 36)
    patient.set_paths(path_to_img)
    patient.set_ileum_coordinates(coords)
    patient.load_image_data()

    preprocessor = Preprocessor(constant_volume_size=[record_shape[1], record_shape[2], record_shape[0]])
    [patient] = preprocessor.process([patient], ileum_crop=True, region_grow_crop=False, statistical_region_crop=False)

    image = process(sitk.GetArrayFromImage(patient.axial_image), out_dims=feature_shape)
    # add this extra dimension so that it is ready for the input of the tf serving model
    image = image.reshape([-1, 1] + feature_shape)

    return image


def query_client(image, client):
    # specify the type of data that the client should send
    req_data = [{'in_tensor_name':'Input',
                 'in_tensor_dtype': 'DT_FLOAT',
                 'data': image}]

    # query the model with the given data
    out_model = client.predict(req_data)
    prob_values = out_model['Output']
    max_prob_indx = np.argmax(np.squeeze(prob_values))
    # get the attention layers
    attention_layer = out_model['attention_layer']

    return prob_values, max_prob_indx, attention_layer


if __name__=="__main__":
    coords = [281, 258, 44]
    get_prediction(coords, "../examples/A1 Axial T2.nii", "localhost")
