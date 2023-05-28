"""
A simple example illustrating basic use of the Ground Texture SLAM system.
"""
import sys
sys.path.append('/app/build')
from typing import List
import numpy
import ground_texture_slam_new as ground_texture_slam
import cv2
import os
import time



dataset_root = '/dataset'
# 获取数据集目录下所有的文件夹
dataset_dirs = [os.path.join(dataset_root, d) for d in os.listdir(dataset_root) if os.path.isdir(os.path.join(dataset_root, d))]

# def create_images() -> List[numpy.ndarray]:
#     """
#     Create a series of fake images. This is just a rectangle translating across the image.
#     @return The list of images
#     @rtype List[numpy.ndarray]
#     """
#     image_list = []
#     for j in range(10):
#         image = numpy.zeros((600, 800), dtype=numpy.uint8)
#         image[200:260, j*10:100] = 255
#         image_list.append(image)
#     return image_list

def create_images(root, seq):
    """
    Create a series of fake images. This is just a rectangle translating across the image.
    @return The list of images
    @rtype List[numpy.ndarray]
    """
    dir = os.path.join(root, seq)
    files_ = os.listdir(dir)
    files_.sort()
    files = [f for f in files_ if '.png' in f]
    
    return files


def create_vocabulary() -> None:
    """
    Build a vocabulary tree out of random noise descriptors and save it locally for later use by the
    SLAM system.
    """
    print('Building the vocabulary from random descriptors...')
    all_descriptors = []
    for _ in range(100):
        all_descriptors.append(numpy.random.randint(
            low=0, high=256, size=(500, 32), dtype=numpy.uint8))
    vocab_options = ground_texture_slam.BagOfWords.VocabOptions()
    vocab_options.descriptors = all_descriptors
    bag_of_words = ground_texture_slam.BagOfWords(vocab_options)
    bag_of_words.save_vocabulary('example_vocab_python.bow')
    print('\tDone!')


if __name__ == '__main__':
    # Build a vocabulary to use later.
    create_vocabulary()
    for dataset_dir in dataset_dirs:

        # 提取数据集名称
        dataset_name = os.path.basename(dataset_dir)
        seqs = os.listdir(os.path.join(dataset_dir, 'database'))
        for seq in seqs:

            # Set all the parameters of this fake SLAM system. The important ones are the camera intrinsic
            # matrix and pose, and the vocabulary for bag of words.
            print('Loading system...')
            options = ground_texture_slam.GroundTextureSLAM.Options()
            options.bag_of_words_options.vocab_file = 'example_vocab_python.bow'
            options.keypoint_matcher_options.match_threshold = 0.6
            # Normally, you want a sliding window so that successive images don't get compared for loop
            # closure. However, I am specifically allowing that here since there are only a few images.
            options.sliding_window = 0
            camera_matrix = numpy.array([
                [2195.70853, 0.0, 820.7289683],
                [0.0, 2195.56073, 606.242723],
                [0.0, 0.0, 1.0]
            ])
            
            Dist_coef = cv2.UMat(numpy.array([-0.1581150018, 0.1909030804,0,0,0]))
            camera_matrix, _ = cv2.getOptimalNewCameraMatrix(camera_matrix, Dist_coef, (1200, 1600), 0, (1200, 1600))
            # print(camera_matrix)
            options.image_parser_options.camera_intrinsic_matrix = camera_matrix
            camera_pose = numpy.array([
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [-1.0, 0.0, 0.0, 0.09989],
                [0.0, 0.0, 0.0, 1.0]
            ])
            options.image_parser_options.camera_pose = camera_pose
            # Get the images "captured" by the robot.
            # Also, create some fake start pose info. This doesn't matter so set it to the origin. You could
            # also set it to a known start pose to align with any data you are comparing against.
            # Unlike C++, there is only one input type here - numpy arrays.
            img_names= create_images(os.path.join(dataset_dir, 'database'), seq)
            # print(type(images[0]))
            start_pose = numpy.zeros((3,1), dtype=numpy.float64)
            start_covariance = numpy.identity(3, dtype=numpy.float64)
            
            img = numpy.array(cv2.imread(os.path.join(os.path.join(dataset_dir, 'database'), seq, img_names[0]), cv2.IMREAD_GRAYSCALE), dtype=numpy.uint8)
            
            system = ground_texture_slam.GroundTextureSLAM(
                options, img, start_pose, start_covariance)
            
            print('Adding images...')
            # Now add each image. This would be done as images are received.
            for i in range(1, len(img_names)):
                start = time.time()
                img = numpy.array(cv2.imread(os.path.join(os.path.join(os.path.join(dataset_dir, 'database'), seq, img_names[i])), cv2.IMREAD_GRAYSCALE), dtype=numpy.uint8)
                system.insert_measurement(img)
                end = time.time()
                print("processing %s using %s seconds" % (img_names[i], str(end - start)))
            # Once done, get the optimized poses. This can be done incrementally after each image as well.
            # The results probably won't be any good, since this is a bunch of random images. But it
            # illustrates the point.
            pose_estimates = system.get_pose_estimates_matrix()
            print('Results:')
            save_file = os.path.join('results', 'results_HD', '%s_database_%s' % (dataset_name, seq))
            f = open(save_file,'a')
            for i in range(len(img_names)):
                x = pose_estimates[i, 0]
                y = pose_estimates[i, 1]
                t = pose_estimates[i, 2]
                print(F'({x:0.6f}, {y:0.6f}, {t:0.6f})')
                print('%s %s %s 0 0 0 0 1' % (img_names[i][:-4], x, y), file=f)
            f.close()