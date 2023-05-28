import os
import time

directory_path = '/home/zheng/projects/ground-texture-slam/src/results/results_HD_ori'  # 修改为你的文件夹路径

for dirname in os.listdir(directory_path):
    dir_path = os.path.join(directory_path, dirname)
    if os.path.isdir(dir_path):
        base_name = os.path.basename(dirname)
        # new_directory_path = os.path.join(directory_path, base_name)
        old_file_path = os.path.join(dir_path, base_name)
        new_file_path = os.path.join(dir_path, base_name+'.txt')
        
        # 如果新的子文件夹还不存在，则创建
        # if not os.path.exists(new_directory_path):
        #     os.makedirs(new_directory_path)
        # 将文件重命名并移动到新的子文件夹
        # os.rename(file_path, old_file_path)
        os.rename(old_file_path, new_file_path)
