from invoke import task
from subprocess import run
from time import time
import os
import re
import matplotlib.pyplot as plt

PLOTS_DIR = "../plots/"

def measure_nydus_startup(image: str, name: str) -> float:
    run_cmd = f"sudo nerdctl --snapshotter nydus run --name {name} {image}"
    start_ts = time()
    result = run(run_cmd, shell=True, check=True)
    end_ts = time()
    return end_ts - start_ts

def measure_docker_startup(image: str, name: str) -> float: 
    run_cmd = f"docker run --name {name} {image}"
    start_ts = time()
    run(run_cmd, shell=True, check=True)
    end_ts = time()
    return end_ts - start_ts


def cleanup(image_pairs: dict) -> None:
    docker_images = list(map(lambda p: p[0], image_pairs.values()))
    nydus_images = list(map(lambda p: p[1], image_pairs.values()))
    image_names = list(image_pairs.keys())

    remove_containers_cmd = "sudo nerdctl rm " + " ".join(image_names) + "&& docker rm " + " ".join(image_names) 
    remove_images_cmd = "sudo nerdctl rmi " + " ".join(nydus_images) + "&& docker rmi " + " ".join(docker_images)

    run(remove_containers_cmd, shell=True, check=True)
    run(remove_images_cmd, shell=True, check=True)


def create_plot(duration_pairs: dict):


    plot_filenames = os.listdir(PLOTS_DIR)
    if plot_filenames:
        experiment_number = sorted([int(re.findall(r'\d+', filename)[0]) for filename in plot_filenames])[-1] + 1 
    else:
        experiment_number = 0
    plot_filename = f"docker_vs_nydus_{experiment_number}.png"

    docker_durations = [pair[0] for pair in duration_pairs.values()]
    nydus_durations = [pair[1] for pair in duration_pairs.values()]
    names = list(duration_pairs.keys())


    ind = list(range(len(duration_pairs)))

    width = 0.35

    bars1 = plt.bar([i - width/2 for i in ind], docker_durations, width, label='Docker image statrup', color='orange')
    bars2 = plt.bar([i + width/2 for i in ind], nydus_durations, width, label='Nydus image statrup', color='blue')

    plt.ylabel('Time (s)')
    plt.title('Docker vs Nydus startup (cold start))')

    plt.xticks(ind, [f'{name.rsplit("-")[0]}' for name in names])
    
    plt.legend()
    
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            plt.annotate('{:.2f}'.format(height),
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3),
                         textcoords="offset points",
                         ha='center', va='bottom')

    add_labels(bars1)
    add_labels(bars2)

    plt.savefig(PLOTS_DIR + plot_filename) 
    

def run_experiment():
    image_pairs = {
                    "centos-tmp":["centos:latest", "localhost:5000/centos-nydus:latest"],
                    "openjdk-tmp": ["openjdk:latest", "localhost:5000/openjdk-nydus:latest" ],
                       "node-tmp": ["node:latest", "localhost:5000/node-nydus:latest"],
                    "tensorflow-tmp": ["tensorflow/tensorflow:latest", "localhost:5000/tensorflow-nydus:latest"]
                   }
    duration_pairs = {}
    for name, pair in image_pairs.items():
        docker_image = pair[0]
        docker_startup_duration = measure_docker_startup(docker_image, name)
        nydus_image = pair[1]
        nydus_startup_duration = measure_nydus_startup(nydus_image, name)
        duration_pairs[name] = [docker_startup_duration, nydus_startup_duration]

    create_plot(duration_pairs)
    cleanup(image_pairs)


if __name__ == "__main__":
    run_experiment()
