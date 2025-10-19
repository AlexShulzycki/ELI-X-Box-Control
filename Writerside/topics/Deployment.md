# Deployment

## Server Deployment

The entry point for the server is **server/main.py**. In order to compile it into a single EXE file for deployment,
the file **entry.py** in the root folder passed to **autopytoexe** which turns it into an EXE.

Also in the root folder is **autopy_config.json**, which contains all the settings for **autopytoexe** needed to 
successfully create a functional EXE. 

>Remember to check that the paths in the *autopytoexe* config are correct for your machine,
>as they may be different from machine to machine

### Required files
Do note that the exe file generated assumes the following files and folders are present in its directory:

- settings
  - readonly
    - *PIStages.json*
    - *StandaAStages.json*
- data
  - *AbsorptionEnergy.csv*
  - *Crystals.csv*
  - *EmissionEnergy.csv*
- static **(optional)**
  - *index.html* - This will be served as a static web page
  - css, icons, etc. which *index.html* needs

> The server EXE will not run without these folders and files present.
{style="warning"}

## Web Interface Deployment
The web interface lives in the **webinterface** folder, and simply running the npm build command will create a static page 
(html and css files) you can serve.

[As described above](#required-files), any web files in the folder **server/static** are automatically served by the server. 
The idea here is you run npm build and then place the generated static page in the **server/static** folder.

> Note that because the server serves whatever is in the **server/static** folder, you do **not** need to rebuild the 
> exe evertime you update the web interface.