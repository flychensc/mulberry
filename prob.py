# TensorFlow and tf.keras
import tensorflow as tf

# Helper libraries
import matplotlib.pyplot as plt
import numpy as np
import random
import pathlib


# 配置
AUTOTUNE = tf.data.experimental.AUTOTUNE
#  32: 0.514
#  64: 0.532 (1*OOM)
# 128: 0.5228 (2*OOM)
BATCH_SIZE = 32
# (96, 128, 160, 192, 224)
# 192: 0.513; 224: 0.531
IMAGE_SIZE = 224


# 加载和格式化图片
def preprocess_image(image):
  image = tf.image.decode_jpeg(image, channels=3)
  image = tf.image.resize(image, [IMAGE_SIZE, IMAGE_SIZE])
  image /= 255.0  # normalize to [0,1] range
  return image


def load_and_preprocess_image(path):
  image = tf.io.read_file(path)
  return preprocess_image(image)


def load_datasheet(path, disp_one=False):
  # 检索图片
  data_root = pathlib.Path(path)

  all_image_paths = list(data_root.glob('*'))
  all_image_paths = [str(path) for path in all_image_paths]
  random.shuffle(all_image_paths)

  image_count = len(all_image_paths)

  all_codes = [image_path.split('.')[0].split('_')[1] for image_path in all_image_paths]

  # 构建一个 tf.data.Dataset
  # 将字符串数组切片，得到一个字符串数据集
  path_ds = tf.data.Dataset.from_tensor_slices(all_image_paths)
  # 现在创建一个新的数据集，通过在路径数据集上映射 preprocess_image 来动态加载和格式化图片
  image_ds = path_ds.map(load_and_preprocess_image, num_parallel_calls=AUTOTUNE)
  # 使用同样的 from_tensor_slices 方法你可以创建一个标签数据集
  label_ds = tf.data.Dataset.from_tensor_slices(tf.cast(all_codes, tf.string))
  # 由于这些数据集顺序相同，可以将他们打包在一起得到一个(图片, 标签)对数据集：
  image_label_ds = tf.data.Dataset.zip((image_ds, label_ds))

  if disp_one:
    img_path = all_image_paths[0]

    plt.imshow(load_and_preprocess_image(img_path))
    plt.grid(False)
    plt.xlabel(pathlib.Path(img_path).relative_to(data_root))
    plt.show()

  return image_label_ds, image_count


#class_names = sorted(item.name for item in pathlib.Path('./test').glob('*/') if item.is_dir())
class_names = ['holding', 'loss', 'profit']
CLASS_NUM = len(class_names)
print(class_names)

def plot_image(i, predictions_array, true_label, img):
  predictions_array, true_label, img = predictions_array, true_label[i], img[i]
  plt.grid(False)
  plt.xticks([])
  plt.yticks([])

  plt.imshow(img, cmap=plt.cm.binary)

  predicted_label = np.argmax(predictions_array)
  color = 'red'

  plt.xlabel("{} {:2.0f}% ({})".format(class_names[predicted_label],
                                100*np.max(predictions_array),
                                true_label.decode("utf-8")),
                                color=color)

def plot_value_array(predictions_array):
  plt.grid(False)
  plt.xticks(range(CLASS_NUM))
  plt.yticks([])
  thisplot = plt.bar(range(CLASS_NUM), predictions_array, color="#777777")
  plt.ylim([0, 1])
  predicted_label = np.argmax(predictions_array)

  thisplot[predicted_label].set_color('red')


def prob():
  # 从保存的模型重新加载一个新的 Keras 模型
  model = tf.keras.models.load_model('saved_model/my_model')

  # 导入数据集
  test_ds, test_count = load_datasheet('./img')

  test_ds = test_ds.batch(BATCH_SIZE)
  # 当模型在训练的时候，`prefetch` 使数据集在后台取得 batch。
  test_ds = test_ds.prefetch(buffer_size=AUTOTUNE)

  # 进行预测
  probability_model = tf.keras.Sequential([model,
                                          tf.keras.layers.Softmax()])
  predictions = probability_model.predict(test_ds)
  print(predictions[0])
  # 哪个标签的置信度值最大
  print(np.argmax(predictions[0]))
  # 检查测试标签
  test_list = list(test_ds)
  test_images = np.array(test_list[0][0])
  test_labels = np.array(test_list[0][1])
  print(test_labels[0].decode("utf-8"))


  # Plot the first X test images, their predicted labels, and the true labels.
  # Color correct predictions in blue and incorrect predictions in red.
  num_rows = 5
  num_cols = 3
  num_images = num_rows*num_cols
  num_images = min(num_images, test_count)
  plt.figure(figsize=(2*2*num_cols, 2*num_rows))
  for i in range(num_images):
    plt.subplot(num_rows, 2*num_cols, 2*i+1)
    plot_image(i, predictions[i], test_labels, test_images)
    plt.subplot(num_rows, 2*num_cols, 2*i+2)
    plot_value_array(predictions[i])
  plt.tight_layout()
  plt.show()

  if test_count > 1:
    # 使用训练好的模型
    img = test_images[1]
    img = (np.expand_dims(img,0))
    predictions_single = probability_model.predict(img)

    print(predictions_single)
    print(np.argmax(predictions_single[0]))
    print(test_labels[1].decode("utf-8"))
    plot_value_array(predictions_single[0])
    _ = plt.xticks(range(CLASS_NUM), class_names, rotation=45)


if __name__ == "__main__":
  prob()
