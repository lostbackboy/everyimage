import numpy as np
import matplotlib.pyplot as plt
import threading
import argparse
import psutil
import os
import hashlib

def generate_image(width, height, color):
    image = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            image[i, j] = color
    return image

def generate_images_thread(start, end, width, height, limit_bytes, processed_images):
    for r in range(start, end):
        for g in range(256):
            for b in range(256):
                color = (r, g, b)
                image = generate_image(width, height, color)
                file_name = "image_" + str(r) + "_" + str(g) + "_" + str(b) + ".png"
                file_size = os.path.getsize(file_name)
                hash = hashlib.sha1(image).hexdigest()
                if hash in processed_images:
                    continue
                if psutil.virtual_memory().available < file_size:
                    print("Out of memory")
                    return
                if psutil.disk_usage(".").free < file_size + limit_bytes:
                    print("Reached disk space limit")
                    return
                plt.imsave(file_name, image)
                processed_images.add(hash)

def generate_images(width, height, num_threads, limit_gb):
    threads = []
    chunk_size = 256 // num_threads
    start = 0
    end = chunk_size
    limit_bytes = limit_gb * 1024**3
    processed_images = set()
    for i in range(num_threads):
        thread = threading.Thread(target=generate_images_thread, args=(start, end, width, height, limit_bytes, processed_images))
        thread.start()
        threads.append(thread)
        start = end
        end += chunk_size
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use")
    parser.add_argument("--limit", type=int, default=100, help="Disk space limit in GB")
    args = parser.parse_args()
    
    width = 1920
    height = 1080
    generate_images(width, height, args.threads, args.limit)
