import os
import shutil
import gzip
import logging
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

# 设置日志
logging.basicConfig(level=logging.INFO)

class BackUp:
    def __init__(self, source_dir=None, target_dir=None):
        if source_dir is None:
            raise ValueError("Source directory must be specified.")
        if target_dir is None:
            raise ValueError("Target directory must be specified.")
        self.source_dir = source_dir
        self.target_dir = target_dir

    def _get_size_of_folder(self, folder_path):
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
        except OSError as e:
            logging.error(f"Error while getting the size of {folder_path}: {e}")
            return None

        return total_size

    def _copy_file(self, src, dst):
        try:
            shutil.copy2(src, dst)
        except Exception as e:
            logging.error(f"Copy failed for {src}: {e}")
            return False
        return True

    def _compress_files(self, destination_folder):
        try:
            for root, dirs, files in os.walk(destination_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    compressed_file_path = f"{file_path}.gz"
                    with open(file_path, "rb") as f_in:
                        with gzip.open(compressed_file_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            logging.error(f"Compression failed: {e}")
            return False
        return True

    def _remove_unzipped_folder(self, destination_folder):
        try:
            shutil.rmtree(destination_folder)
        except Exception as e:
            logging.error(f"Removal failed: {e}")
            return False
        return True
    def backup(self, is_remove_unzipped_folder=False, is_zip=False, is_compare_size=False):
        if is_compare_size:
            source_size = self._get_size_of_folder(self.source_dir)
            target_size = self._get_size_of_folder(self.target_dir)

            if source_size is None or target_size is None:
                logging.error("Error: cannot get size of folder")
                return False

            if source_size > target_size:
                logging.warning("Source folder is larger than target folder")
                return False

        try:
            shutil.copytree(self.source_dir, self.target_dir)
        except FileExistsError as e:
            logging.error(f"Target directory already exists: {e}")
            return False
        except Exception as e:
            logging.error(f"Backup failed: {e}")
            return False

        logging.info("Backup completed.")

        # get file count and total size
        file_count = 0
        total_size = 0
        for root, dirs, files in os.walk(self.target_dir):
            file_count += len(files)
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)

        # choose whether to use multithreading based on file count and size
        use_multithreading = file_count > 100 or total_size >= 100 * 1024 * 1024  # 100MB

        if use_multithreading:
            # 使用多线程
            with ThreadPoolExecutor(max_workers=5) as executor:
                # 复制文件从源文件夹到目标文件夹
                futures = []
                for root, dirs, files in os.walk(self.source_dir):
                    for file in files:
                        src = os.path.join(root, file)
                        dst = os.path.join(self.target_dir, os.path.relpath(src, self.source_dir))
                        future = executor.submit(self._copy_file, src, dst)
                        futures.append(future)

                # 等待所有任务完成
                wait(futures, return_when=ALL_COMPLETED)

            logging.info("File copy completed (using multithreading).")
        else:
            # 单线程处理
            logging.info("File copy completed (using single-threading).")

        if is_zip:
            if not self._compress_files(self.target_dir):
                return False

            logging.info("Compression complete.")
            if is_remove_unzipped_folder:
                if not self._remove_unzipped_folder(self.target_dir):
                    return False

                logging.info("Unzipped folder removed.")

        else:
            logging.info("Backup completed without compression.")
            return True

        return True
