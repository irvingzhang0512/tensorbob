import os
import numpy as np
import scipy.io
from .dataset_utils import get_images_dataset_by_paths_config, get_classification_labels_dataset_config
from .base_dataset import BaseDataset


__all__ = ['get_imagenet_classification_dataset']

DATA_PATH = "/home/tensorflow05/data/ILSVRC2012"
IMAGE_DIRS = {"train": "ILSVRC2012_img_train",
              "val": "ILSVRC2012_img_val",
              "test": ""}
LABEL_DIRS = {"train": "ILSVRC2012_bbox_train",
              "val": "ILSVRC2012_bbox_val",
              "test": "ILSVRC2012_bbox_test_dogs"}
DEVKIT_DIR = "ILSVRC2012_devkit_t12/data"
META_FILE_NAME = "meta.mat"
VAL_LABEL_FILE_NAME = "ILSVRC2012_validation_ground_truth.txt"
BROKEN_IMAGES_TRAIN = ['n02667093_4388.JPEG',
                       'n09246464_51105.JPEG',
                       'n04501370_2480.JPEG',
                       'n04501370_19125.JPEG',
                       'n04501370_16347.JPE',
                       'n04501370_3775.JPEG',
                       'n02690373_15966.JPEG',
                       'n02494079_12155.JPEG',
                       'n04522168_538.JPEG',
                       'n02514041_1625.JPEG',
                       'n02514041_15019.JPEG',
                       'n07714571_1691.JPEG',
                       'n02640242_29608.JPEG',
                       'n04505470_7109.JPEG',
                       'n04505470_5018.JPEG',
                       'n09256479_9451.JPEG',
                       'n01770393_6999.JPEG',
                       'n09256479_1094.JPEG',
                       'n09256479_108.JPEG',
                       ]
BROKEN_IMAGE_VAL = []


def _load_mata_data(data_path):
    """
    从META File中读取分类id与分类细节
    :return: 分类id，分类细节
    """
    meta_file = os.path.join(data_path, DEVKIT_DIR, META_FILE_NAME)
    meta_data = scipy.io.loadmat(meta_file, struct_as_record=False)
    synsets = np.squeeze(meta_data['synsets'])
    wnids = np.squeeze(np.array([s.WNID for s in synsets]))
    words = np.squeeze(np.array([s.words for s in synsets]))
    return wnids, words


def _get_images_paths_and_labels(mode, data_path):
    wnids, words = _load_mata_data(data_path)
    paths = []
    labels = []
    if mode == 'train':
        for i, wnid in enumerate(wnids):
            if i >= 1000:
                break
            images = os.listdir(os.path.join(data_path, IMAGE_DIRS[mode], wnid))
            for image in images:
                if image in BROKEN_IMAGES_TRAIN:
                    continue
                paths.append(os.path.join(data_path, IMAGE_DIRS[mode], wnid, image))
                labels.append(i)
        ids = np.arange(0, len(labels))
        np.random.shuffle(ids)
        paths = np.array(paths)[ids]
        labels = np.array(labels)[ids]
    elif mode == 'val':
        with open(os.path.join(data_path, DEVKIT_DIR, VAL_LABEL_FILE_NAME)) as f:
            ground_truths = f.readlines()
        ground_truths = [int(label.strip()) for label in ground_truths]
        images = sorted(os.listdir(os.path.join(data_path, IMAGE_DIRS[mode])))
        for image, label in zip(images, ground_truths):
            if image in BROKEN_IMAGE_VAL:
                continue
            paths.append(os.path.join(data_path, IMAGE_DIRS[mode], image))
            labels.append(label)
    return paths, labels


def get_imagenet_classification_dataset(mode,
                                        batch_size,
                                        data_path=DATA_PATH,
                                        shuffle_buffer_size=10000,
                                        prefetch_buffer_size=10000,
                                        **kwargs):
    paths, labels = _get_images_paths_and_labels(mode, data_path)
    images_config = get_images_dataset_by_paths_config(paths, **kwargs)
    labels_config = get_classification_labels_dataset_config(labels)
    dataset_config = [images_config, labels_config]
    train_mode = True if mode == 'train' else False
    return BaseDataset(dataset_config,
                       batch_size=batch_size,
                       shuffle=train_mode, shuffle_buffer_size=shuffle_buffer_size,
                       repeat=train_mode,
                       prefetch_buffer_size=prefetch_buffer_size)
