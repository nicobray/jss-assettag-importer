# jss-assettag-importer
JSS Asset Tag Importer - Get those asset tags into your Casper JSS. For Mobile Devices and Computers!
## JSS Asset Tag importer - v.3
## Authored by Brad Schmidt @bradschm on 12/29/2015
## Updated formating and issue with detection of smart group on 07/01/2016
## Updated by Nico Bray @nicobray on 07th Jan 2021
## Note: two versions, jss-assettag-importer-py3.9 finds and updates devices without any Asset tags already in JAMF JSS
## Second version: jss-assettag-importer-py3.9-overwrite will update any assets found in CSV. Non CSV devices will be left.

### DISCLAIMER
I am not providing any kind of warranty. This has been thoroughly tested in my environments but I cannot guarantee that this script is not without bugs.
Thank you

### TODOS
- Add more logging (Actual logging instead of print)
- Add gui? Prompt for values and file location
- Once bug in the API for large advanced searches is fixes, switch to advanced searches from smart groups.

### HOW TO USE
For more detailed instructions, check out the [Quickstart] (https://github.com/bradschm/jss-assettag-importer/wiki/Quickstart)   

1. Make an JSS User Account and give it these API rights:
  * Create/Read Computer Smart Groups
  * Create/Read Mobile Device Smart Groups
  * Update Computer records
  * Update Mobile Device records
  * Update User records
2. Save a csv file of your serial numbers and asset tags. Format is assettag,serialnumber. In other words, the first column is the asset tag and the second is the serialnumber.
3. Run the jss-importer.py script - be patient, this could take a while. Creating the groups can take a long time in large environments. Touching each record isn't blazing fast either but I did put in a progress counter ;)

> Example command to execute: Open Terminal and run: `python path/to/jss-assettag-importer.py`


