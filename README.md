# Prisma SD-WAN Tunnel Reoptimization (Preview)
The purpose of this script to set an element extension to enable or disable tunnel reoptimization

#### License
MIT

#### Requirements
* Active CloudGenix Account - Please generate your API token and add it to cloudgenix_settings.py
* Python >=3.7

#### Installation:
 Scripts directory. 
 - **Github:** Download files to a local directory, manually run the scripts. 
 - pip install -r requirements.txt

### Examples of usage:
 Please generate your API token and add it to cloudgenix_settings.py

 1. ./tunnel-reoptimization.py -S Branch-Site-4
      - Will disable tunnel reoptimization on Branch-Site-4
 2. ./tunnel-reoptimization.py -R -S Branch-Site-4
      - Will enable tunnel reoptimization on Branch-Site-4
 3. ./tunnel-reoptimization.py -S All-Sites
      - Will disable tunnel reoptimization on all sites
 4. ./tunnel-reoptimization.py -R -S All-Sites
      - Will enable tunnel reoptimization on all sites
	  

### Caveats and known issues:
 - This is a PREVIEW release, hiccups to be expected. Please file issues on Github for any problems.

#### Version
| Version | Build | Changes |
| ------- | ----- | ------- |
| **1.0.0** | **b1** | Initial Release. |


#### For more info
 * Get help and additional Prisma SD-WAN Documentation at <https://docs.paloaltonetworks.com/prisma/cloudgenix-sd-wan.html>
PrismaAccess2023
