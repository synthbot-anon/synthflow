# Introduction
This project is part of the Please Please Pleese-get-a-life Foundation (PPP). It's intended to help organize our development efforts and make it easier for anons to replicate our work.

If you're not familiar with Docker, please read the sections below in this order:
1. *What can containers do*
2. *How should I use a container*
3. *Setting up CUDA in Docker*
4. *What does SynthFlow do*
5. *How is SynthFlow organized*

This is the expected workflow for replicating someone's workspace:
1. Follow the installation steps below to set up Docker and CUDA.
2. Clone this repository (`git clone https://github.com/synthbot-anon/synthflow.git`).
3. Clone any target code into `run-data/src/` (e.g., `git clone https://github.com/CookiePPP/cookietts.git run-data/src/cookietts`)
4. Build the container with `./build WorkspaceNameGoesHere` (e.g., `./build cookietts`)
5. Run the container with `./run`

The entire `run-data` directory will be available in the workspace in `/data`. Once this workspace is running, you can run the scripts in `utils/` to get a new shell, get a root shell, start a Jupyter notebook server, and start an AirFlow server. See the *What does SynthFlow do* section below.

This is the expected workflow for creating a custom workspace:
1. Move your code to `run-data/src/RepoNameGoesHere`.
2. Copy the files from `run-data/src/synthflow/template` into your repository. This should add a `container` directory in your repo.
3. Modify the newly-created files to specify what packages you want and what scripts you want to run before installation.
4. Run `./build RepoNameGoesHere`.

# 1. What can containers do
Containers solve the problem of replicating working environments. Normally when other people try to run your code, you need to worry about what operating system they're using, what packages and libraries they've installed, what else might be running alongside your program that might interfere, files and folders on the filesystem, and so on. Containers simplify all of that by letting you specify all of this. Your code will get a virtual view of all of this so it can act as if it's running in a perfectly controlled environment.

The biggest benefit is that this makes it very easy for other people to run your code. The container encapsulates everything, so they just need to run the same container as you if they want to replicate your work. There are some corner-cases that break the abstraction, like with GPU drivers. Sometimes you want to deliberately break the abstraction so you can do things like share files between the container filesystem and your host filesystem. As far as replication goes, containers get us 95% of the way there. We'll need to use documentation and standard formats to get the rest of the 5%.

##### Setting up Docker in Ubuntu
You can find installation instructions here: https://docs.docker.com/engine/install/ubuntu/. This follows the general outline:
- Add Docker's GPG key so that apt will accept packages signed by Docker.
- Add the Docker repository to apt. This usually requires passing your distribution details. Some operating systems branched off from Ubuntu (like Linux Mint) may mess with the parameters these scripts use to identify the distribution. If you're not using Ubuntu, you may need to manually translate the name.
- Update the apt package list (using `apt-get update`) so it fetches the new information.
- Install docker (using `apt-get install docker-ce docker-ce-cli containerd.io`).

Once you've installed Docker, you might want to be able to run it without root. You can do this by following the instructions here: https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user. This follows the general outline:
- Create a `docker` group. Docker gives users in this group special permissions.
- Add your user to the `docker` group.
- Reboot, log out and back in, or run `newgrp docker` in a shell. All of these tell Linux to update the groups it associates with your process. If you use the `newgrp` approach, you'll need to run that command again for every new shell to create where you want to use docker.
- If needed, update the permissions for files in your `~/.docker` directory.

##### Setting up Docker in Windows
TODO

### Get a feel for containers
Once you've installed docker, you can run a simple container.
* `docker run --rm -it ubuntu:latest`

This will give you a root shell inside of an empty Ubuntu environment. You can create files, create users, and generally mess around with this environment however you like. When you exit the container (`Ctrl+D` or the `exit` command), all of your changes will be gone.

Try running these commands in the shell that's now inside the `ubuntu:latest` container:
* `cat /etc/issue` (check the current running OS)
* `adduser --disabled-password --gecos "" celestia` (create user `celestia`)
* `su celestia` (switch to user `celestia`)
* `exit` (switch back to the root shell)
* `rm -rf /usr` (delete the `/usr` folder inside the container, which contains pretty much everything)
* `ls` (command not found, since you just deleted it)
* `exit` (leave the main shell, thus closing the container)
* `docker run --rm -it ubuntu:latest` (start the container again)
* `ls /` (the command works again, and everything is back to its clean state)

You can persist files by sharing them with the containers you run. Here's an example:
* `mkdir shared` (optional: create the directory you want to share and give it any name)
* `echo world > shared/hello` (put a file in there for demonstration purposes)
* `docker run --rm -it --mount "type=bind,src=$(pwd)/shared,dst=/data" ubuntu:latest` (run the container with the `shared` host folder mounted onto the container `/data` folder.
* `cat /data/hello` (check the contents of `/data/hello` in the container, which should return `world`)
* `echo 'acute' > /data/sunset` (write something to `/data/sunset`)
* `exit` (close out the container)
* `cat shared/sunset` (verify that the new contents are still available on the host)

### Creating new container images
One of the nice things about containers is that you can modify the environment, then save the result as a new container image. We can play around in one container:
* `docker run --rm -it ubuntu:latest`
* `echo 'acute horse syndrome' > /sunset`

Now while this container is running, open a separate shell and run the following:
* `docker container ls` (this will list the running containers alongside the container id)
* `docker commit PasteContainerIdHere sunset:latest` (create a new container image called sunset:latest)

You can close out the first container now, then run:
* `docker run --rm -it sunset:latest` (run the new image you just created)
* `cat /sunset` (make sure your commited changes are still there)
* `exit`

That's one way to create a new container image. You can also create a new image using a Dockerfile. I won't explain Dockerfiles here, but you can see the `Dockerfile` in this repository for an example.

Once you have an image, you can host it on dockerhub, which like like the github of docker images. Other anons can run any images you host there with a single `docker run` command.

# 2. How should I use a container
Here's my typical setup:
- I run all my code inside of a docker environment. Whenever the code runs, it's running inside of a docker environment.
- I have one shared directory (`run-data`) between the host and the container. My code goes in that shared directory, as does any data I want to persist across container runs.
- Since my code is in the shared directory, I can edit it using my usual IDE and shell tools. The updates are automatically reflected inside the container.
- Whenever I need to install a new package, I figure out how to get it working inside the container, then I add the corresponding steps to my `Dockerfile`.
- I port-forward Jupyter and any other daemons to my host computer so I can access them from my browser. By default, nothing that happens inside of a container is accessible outside of it, so these ports need to be exposed explicitly. For security reasons, I only make these available on my host and not to the internet. This is done in the `run` script.
- I create scripts to wrap any `docker build` and `docker run` commands. These are in `build`, `run`, and `utils/`.

Killing and restarting a container takes seconds, so it's not a big deal. Building a new custom container usually takes a while (a few minutes), so I kick off a build as soon as I update my `Dockerfile`. You can kick off a build without closing the existing container.

All of my container build scripts follow this general pattern:
- Copy any necessary build files into the container.
- Install any necessary packages using apt and pip.
- Create a non-root user to perform most tasks.
- Do any final container setup.


# 3. Setting up CUDA in Docker
NOTE: This section is written for Linux users. I don't know how to get this working in Windows yet. If someone wants to write an explanation, please do. See https://developer.nvidia.com/blog/announcing-cuda-on-windows-subsystem-for-linux-2/ for details.

Your operating system runs as several components. The kernel is the "core" of the operating system. It defines how processes interact, how resources are shared between processes, and how hardware is exposed to processes. There's a bunch of other crud that's bundled into an "operating system" like your default packages, init scripts, daemons, configuration files, and so on. Containers try to replicate everything EXCEPT the kernel. When you run a container, it effectively shares a kernel with your host.

Containers virtualize most of an environment, but containers still share a kernel with the host. Notably, hardware drivers are typically loaded into the kernel, and so these are shared between the host and the container. If you want to make a hardware driver accessible inside a container, you normally need to first install it in your host, THEN make it available inside the container. This is exactly what we'll need to do for CUDA.

##### Optional step 1: Removing previous versions on Linux
If you run `nvidia-smi`, you can see what CUDA version you currently have installed at the top of the table that shows up. Only newer versions will interfere with a 10.2 installation, so if that version is older than or equal to than 10.2, you can skip this step. Otherwise you'll need to uninstall it. If the command doesn't exist, then you can also skip this step since that means you don't have CUDA Toolkit installed.

On Ubuntu, you can find your installed CUDA packages by running `apt list --installed cuda*`. You'll need to get rid of all of these if you have a newer version.

##### Step 2: Installing CUDA Toolkit 10.2 on Linux
If you alrady have CUDA Toolkit 10.2 installed, you can skip this step.

You can install CUDA Toolkit from here: https://developer.nvidia.com/cuda-10.2-download-archive. Make sure you're installing CUDA Toolkit 10.2 since that's that latest version currently supported by PyTorch.

On Linux if you have the option, use the installer that integrate nicely with your package manager. For example, use the deb package on Ubuntu.

##### Step 3: Installing nvidia-docker
Skip down to the Installation instructions on this page: https://developer.nvidia.com/blog/gpu-containers-runtime/ and follow those steps. This follows the general outline:
- Remove any existing nvidia-docker installation.
- Add Nvidia's GPG key so that apt will accept packages signed by Nvidia
- Add the nvidia-docker repository to apt. This requires distribution information collected from /etc/os-release. Some operating systems branched off from Ubuntu (like Linux Mint) may mess with the parameters these scripts use to identify the distribution. If you're not using Ubuntu, you may need to manually translate the name. If you're using such an operating system, see the table in https://nvidia.github.io/nvidia-docker/ for a list of acceptable distribution identifiers.
- Update the apt package list (using `apt-get update`) so it fetches the new information.
- Install nvidia-docker.
- Restart the dockerd daemon.
- You can skip the rest of the steps. You'll run into problems with them anyway because you've install CUDA Toolkit 10.2 instead of 11.0 as the guide expects.

You can test your installation with the following command:
- `docker run --rm --runtime=nvidia -it nvidia/cuda:10.2-base nvidia-smi` (this runs nvidia-smi inside of a cuda:10.2-base container)
- At the top-right corner of the table, you should see "CUDA Version 10.2".

# 4. What does SynthFlow do
- Push our preprocessing code towards a standardized flow to make them more replicable and reusable. I'll keep extending SynthFlow to support more of the preprocessing work we do. The "standardized flow" will probably be AirFlow's notion of DAGs. Chunks of preprocessing would be split off into tasks so they can be reused. A DAG would coordinate running sequences of tasks with dependencies.
- Make it easier for anons to replicate our workflows. AirFlow provides a web interface for running dags and viewing results. Although it's still a bit involved, anons can re-run our preprocessing code on their own data using the web interface. This would help them get familiar with what we're doing before they (hopefully) start mucking around with the code. As we find out more on how we (i.e., Cookie) is developing the ML scripts, I can find ways to make those more replicable, reusable, and scalable.
- Standardize container configuration so people can more easily replicate our workspaces. SynthFlow handles the boring work of setting up scripts and daemons, and it provides ways to customize the environment through hooks. The `container` folders let you hook various parts of container image creation so you can install your own packages and run pre-install/post-install scripts without messing with the Dockerfile. I can add scripts to trigger when people, e.g., add new files or interact with the filesystem and AirFlow UI in various ways. All of these would be exposed to hooks you plug in.
- Pre-install tools and keep them up-to-date. Right now, it comes with Nvidia Apex, PyTorch 1.6, Airflow 1.10.12, and PostgreSQL 10.14 running on Ubuntu 18.04. (At the time of writing, these are the latest versions supported based on PyTorch and AirFlow constraints.)

Replication is a big part of it. If we want anons extending our work, their starting point is to first replicate what we're doing. We've had a lot of issues with that on the preprocessing and AI side. This is a first attempt to broadly try fixing that problem.

# 5. How is SynthFlow organized
SynthFlow contains scripts for building and running containers. These containers can be customized through hooks. SynthFlow contains these files:
- `Dockerfile` - This tells Docker how to build new container images. If you need to modify this file, please tell me. Eventually, I'd like to get to the point where we never need to modify this.
- `build-data/` - This folder mirrors any files needed to build container images. This includes files from `container/` folders in whatever's being built. Files are copied into here when building a new container.
- `build` - This is a script to create new container images. You can create a new image by running `build name-goes-here`. The `name-goes-here` is used as a folder name in `run-data/src/`. That folder is expected to contain a `container/` folder that specifies packages to install and any pre/post installation scripts.
- `run-data/` - This is the shared folder between the host and the container. Inside the container, this folder is exposed as `/data`. It comes pre-populated with a few folders described below.
- `run-data/airflow` - This contains AirFlow configuration information.
- `run-data/downloaded` - Users are expected to drop their own datasets into this folder. Scripts should NOT modify anything in this directory.
- `run-data/uploadable` - Users should NOT modify anything in this directory unless they understand the internals of how relevant scripts work. Scripts should put data here if it's sensible for users to upload them for other anons. Any data here should NOT reference other local files since those references become meaningless on other people's machines. Data in this folder is expected to be self-contained.
- `run-data/generated` - Your scripts can use this as scratch space for any intermediate data.
- `run-data/src` - Any of your own code should go into this directory. You can expect users to `git clone` your repository into this folder.
- `utils/` - This contains utility scripts for working with a running container. There's a script for running a shell, for running a root shell, for starting the AirFlow webserver, and for starting a Jupyter notebook server.
- `run` - This is a script for running a container. For example, after running `./build cookietts`, the `./run` command will run a workspace with the `run-data/src/cookietts/container` customizations. This `run` script exposes any GPUs to your container, sets up the CUDA driver if neccessary, mounts the `run-data` directory, and exposes the ports necessary for AirFlow and Jupyter.

