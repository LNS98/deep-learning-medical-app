# Tackling Chron's Disease with Deep Learning

Group software engineering project, Spring 2020.

Team members:
- Toby Godwin
- Yoanna Peneva 
- Ahmed Djermani
- George Yiasemis
- Charles Metz
- Lorenzo Niccolini

Supervisor:
- Dr. Bernard Kainz

Gitlab Link: https://gitlab.doc.ic.ac.uk/cpm19/softwareengineering_group_project

## Introduction and Motivation
Crohn's disease is a lifelong inflammatory bowel disease. 
The prevalence in the UK is about 145 per 100,000 people [3]. The inflammation caused by Crohn's disease often spreads deep into the layers of affected bowel tissue. A segment of the small intestine, the ileum, is a particularly sensitive area which is most likely to develop Crohn's disease [1], and Computed Tomography (CT) and Magnetic Resonance Imaging (MRI) images are used to help diagnose the disease.  To date, radiologists and clinicians manually inspect the scans to diagnose the patient. This can be a slow process, which requires significant time from clinicians/radiologists. 

Previous work from Robert Holland et al. [2] has made significant progress in utilising deep learning and neural networks to automatically detect the presence of Crohn's disease from a Magnetic Resonance Enterography scan of the terminal ileum. The work presented in [2] achieves "comparable performance to the current clinical standard,...while requiring only a fraction of the preparation and inference time". The adoption of this approach would significantly save the time of radiologists, and would particularly assist relatively inexperienced clinicians. Furthermore, such an algorithm could be used to triage patients so that severe cases can be reviewed more immediately [2].  The advantages of this approach motivate the product presented in this report.

The general approach was to implement a web browser-based tool such that the clinician could upload and explore an image, mark the location of the terminal ileum, and obtain a diagnosis predicted by the pre-trained model described in [2]. To allow for easy deployment on a hospital intranet, docker containers were used to package the tool's dependencies and host the components of the product. The product has been designed so that the web page could be accessed anywhere on the hospital's network. This concept was demonstrated on Imperial College's network, where the web page was accessible anywhere on the network. 

### References
[1] Tung Chien-Chih Shih I-Lun Wang Horng-Yuan Wei Shu-Chen Chang Chen-Wang, Wong Jau-Min.Intestinal stricture in crohn’s disease.Intest Res, 13(1):19–26, 2015

[2]  Robert  Holland,  Uday  Patel,  Phillip  Lung,  Elisa  Chotzoglou,  and  Bernhard  Kainz.   Automaticdetection of bowel disease with residual networks, 2019.

[3]  Dr. Sarah Jarvis.  Crohn’s disease.https://patient.info/doctor/crohns-disease-pro, 2019
 
## Software Presented

The following software is presented in this repo:

- Web application
    - Front-end and back-end
- Pre-trained prediction model

## User Interface

![arch](https://gitlab.doc.ic.ac.uk/cpm19/softwareengineering_group_project/-/raw/master/front-end-scrn.png "User interface")


## Product Architecture 

![arch](https://gitlab.doc.ic.ac.uk/cpm19/softwareengineering_group_project/-/raw/master/architecture.png "Product architecture schematic")

Each component of the application is contained within its own docker container, and communicate through docker container networking. 

The model is served using a [Tensorflow Serving image](https://www.tensorflow.org/tfx/serving/docker) with the following [client](https://github.com/epigramai/tfserving-python-predict-client).

## Dependencies

The docker containers pre-package all of the dendencies required to host the application. Therefore, all that is required to initialise the application is:

- Docker 19.03.6
- Docker Compose 1.25.4

With GPU version, add:
- cudnntoolkit    10.0.130 
- cudnn 7.6.5_cuda10.0_0
          

## Initialising Application

Navigate to desired location to store code.

- `git clone https://gitlab.doc.ic.ac.uk/cpm19/softwareengineering_group_project.git`

- `cd softwareengineering_group_project`

- `docker-compose up` - Note this may take ~5 minutes

-  <strong> Procced ONLY ONCE the front-end and back-end containers are running </strong>

- Open new terminal window

- `cd softwareengineering_group_project/start-app`

- `sh start_tfserving_container_cpu.sh` or `sh 
start_tfserving_container_gpu.sh` depending on preference.

## Accessing Application

Access the application at `localhost:3000` in web-browser.

Or if the host machine has a defined address, access at: `host_address:3000` e.g. `dudley.doc.ic.ac.uk:3000`

## Note on Coordinates

NOTE: The coordinate system of Papaya viewer is different to those provided to us in the dataset of images, which we understand were from a London Hospital. There is a relationship between the coordinates on papaya, and the coordinates seen in the dataset.  To see how they are changed with respect to a given image see function change_coordinate_system in model_client.py file in back-end.



## Repo Guide

A brief explanation of the important files

- `/CrohnsDisease` - Contains model code. For an explanatation of the model, please refer to [Robbie Holland's Github](https://github.com/RobbieHolland/CrohnsDisease/), where we inherrited the code.

- `docker-commpose.yml` - Docker-compse file to spin up front-end and back-end containers. 

- `/back-end/api.py` - Server code written using Flask.

- `/back-end/model_client.py` - Called in `api.py` to serve model container and return results.

- `/examples` - Contains example .nii images

- `/front-end` - Contains JavaScript front-end code written using React. 

- `/start-app/start_tfserving_container_cpu.sh` - Shell script for spinning up CPU-compatible tensorflow serving image.

- `/start-app/start_tfserving_container_gpu.sh` - Shell script for spinning up GPU <strong> and </strong> CPU-compatible tensorflow serving image. 
    - NOTE: both shell scripts serve exactly the same model. The difference is in the initalisation of the container. `start_tfserving_container_gpu.sh` requires a GPU to initialise the container.




<!-- ## :point_right: :point_right: How to start containers :point_left: :point_left:

1. 'docker-compose up' in the softwareengineering_group_project folder
2. 'cd CrohnsDisease'
3. 'sh run_model.sh'
4. 'cd ..'
5. ONLY THEN CAN YOU RUN PREDICTIONS


## :point_right: :point_right: How to run the code :point_left: :point_left:

Steps for running the project locally on your laptop:

0. Download and install [Node.js](https://nodejs.org/en/) (LTS version).
1. Clone the whole project on your machine. You should have 2 folders `front-end` and `back-end`.
2. Go into `back-end` and type `npm install` in a terminal. `NPM` will install all the packages and dependencies required for the project.
3. In the same folder, type `node index.js`. The server will launch and keep running.
4. Go now to `front-end` and type `npm install`. `NPM` will install all the packages and dependencies required for the project.
5. In the same folder, type `npm start`. It will automatically open a new tab in Chrome at `localhost:3000`.
6. Try to modify the front-end code in `front-end/src' and save: the page will automatically refresh.
7. 

## :point_right: :point_right: Required tensorflow/cuda version :point_left: :point_left:

cudnntoolkit    10.0.130 

cudnn           7.6.5_cuda10.0_0


## :point_right: :point_right: How to bypass pre-commit and pre-push hooks :point_left: :point_left:
Note that as part of CI code won't be commited/pushed to the repository unless all tests pass. -->
<!-- To bypass that use: 
`git commit --no-verify` instead of `git commit`, and,
`git push --no-verify`  instead of `git push`  -->
