from os import listdir
from os.path import isfile, join

import cv2
import numpy as np

from keras.layers import Input, Dense, Flatten, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model


def extract_non_zero_image(in_image, out_image, max_size, border=0):
    vert = np.where(np.sum(out_image, axis=1) > 0)[0]
    hor = np.where(np.sum(out_image, axis=0) > 0)[0]
    min_y = max(0, np.min(vert) - border)
    min_x = max(0, np.min(hor) - border)
    in_empty_image = np.zeros(max_size, np.uint8)
    out_empty_image = np.zeros(max_size, np.uint8)
    max_y = min(min_y + max_size[0], len(in_image))
    max_x = min(min_x + max_size[1], len(in_image[0]))
    in_empty_image[:max_y - min_y, :max_x - min_x] = in_image[min_y:max_y, min_x:max_x]
    out_empty_image[:max_y - min_y, :max_x - min_x] = out_image[min_y:max_y, min_x:max_x]
    return in_empty_image, out_empty_image


in_train_path = '../rosatom_dataset/train/in/'
out_train_path = '../rosatom_dataset/train/out/'
files = [f for f in listdir(in_train_path) if isfile(join(in_train_path, f))]

in_images = []
out_images = []
test = 15000
train = 5000
in_images = np.array(in_images)
out_images = np.array(out_images)
in_images = np.reshape(in_images, (len(in_images), 50, 50, 1))
out_images = np.reshape(out_images,  (len(out_images),  50, 50, 1))
in_images = np.array(in_images)
out_images = np.array(out_images)
in_images = np.reshape(in_images, (len(in_images), 50, 50, 1))
out_images = np.reshape(out_images,  (len(out_images),  50, 50, 1))

def create_dense_ae():
    # Размерность кодированного представления
    encoding_dim = 49
    in_0 = 50
    in_1 = 50

    # Энкодер
    # Входной плейсхолдер
    input_img = Input(
        shape=(in_0, in_1, 1))  # 28, 28, 1 - размерности строк, столбцов, фильтров одной картинки, без батч-размерности
    # Вспомогательный слой решейпинга
    x = Conv2D(128, (7, 7), activation='relu', padding='same')(input_img)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(64, (7, 7), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(32, (2, 2), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(1, (7, 7), activation='relu', padding='same')(x)
    flat_img = Flatten()(x)
    # Кодированное полносвязным слоем представление
    encoded = Dense(encoding_dim, activation='relu')(flat_img)

    # На этом моменте представление  (7, 7, 1) т.е. 49-размерное

    input_encoded = Input(shape=(encoding_dim,))
    flat_decoded = Dense(in_0 * in_1, activation='sigmoid')(input_encoded)
    x = Conv2D(32, (7, 7), activation='relu', padding='same')(flat_decoded)
    x = UpSampling2D((2, 2))(x)
    x = Conv2D(64, (7, 7), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(128, (2, 2), activation='relu', padding='same')(x)
    x = UpSampling2D((2, 2))(x)
    decoded = Conv2D(1, (7, 7), activation='sigmoid', padding='same')(x)

    # Модели, в конструктор первым аргументом передаются входные слои, а вторым выходные слои
    # Другие модели можно так же использовать как и слои
    encoder = Model(input_img, encoded, name="encoder")
    decoder = Model(input_encoded, decoded, name="decoder")
    autoencoder = Model(input_img, decoder(encoder(input_img)), name="autoencoder")
    return encoder, decoder, autoencoder

encoder, decoder, autoencoder = create_dense_ae()
autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

autoencoder.summary()

autoencoder.fit(in_images[:train], out_images[:train],
                epochs=150,
                batch_size=256,
                shuffle=True,
                validation_data=(in_images[train:], out_images[train:]))

import seaborn as sns
import matplotlib.pyplot as plt


def plot_digits(*args):
    args = [x.squeeze() for x in args]
    n = min([x.shape[0] for x in args])

    plt.figure(figsize=(2 * n, 2 * len(args)))
    for j in range(n):
        for i in range(len(args)):
            ax = plt.subplot(len(args), n, i * n + j + 1)
            plt.imshow(args[i][j])
            plt.gray()
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)

    plt.show()


n = 10

imgs = in_images[train:]
encoded_imgs = encoder.predict(imgs, batch_size=n)

decoded_imgs = decoder.predict(encoded_imgs, batch_size=n)

plot_digits(imgs, decoded_imgs)