import os
import subprocess

result_directory_path = 'src/results/results_HD_copy'  # 你的结果文件所在的文件夹路径
ground_truth_root_path = '/media/zheng/My_Passport/home/zheng/datasets/ground-texture/HD_ground'  # 真值文件的根目录路径

# 遍历结果文件夹下的所有子文件夹
for subdir in os.listdir(result_directory_path):
    subdir_path = os.path.join(result_directory_path, subdir)
    if os.path.isdir(subdir_path):
        if 'result.txt' in os.listdir(subdir_path):
            continue
        # 找到子文件夹下的txt文件
        for filename in os.listdir(subdir_path):
            if filename.endswith('.txt') and '_seq' in filename:
                result_file_path = os.path.join(subdir_path, filename)
                # 根据结果文件的名字生成真值文件的路径
                base_name = os.path.splitext(filename)[0]
                parts = base_name.split('_database_')
                ground_truth_subdir_path = os.path.join(ground_truth_root_path, parts[0], 'database', parts[-1])
                ground_truth_file_path = os.path.join(ground_truth_subdir_path, 'groundtruth.txt')
                # 检查真值文件是否存在
                if os.path.isfile(ground_truth_file_path):
                    # 执行evo命令并将结果重定向到result.txt文件
                    with open(os.path.join(subdir_path, 'result.txt'), 'w') as f:
                        subprocess.run(['evo_ape', 'tum', ground_truth_file_path, result_file_path, '-as'], stdout=f)
                    with open(os.path.join(subdir_path, 'length.txt'), 'w') as f:
                        subprocess.run(['evo_traj', 'tum', '--ref', ground_truth_file_path, result_file_path, '-as'], stdout=f)                        
                else:
                    print(f'Ground truth file does not exist: {ground_truth_file_path}')
