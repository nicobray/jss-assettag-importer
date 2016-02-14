#####################################################
# JSS Asset Tag importer - v.2
# Import Asset tags from a csv into your Casper JSS
# Authored by Brad Schmidt @bradschm on 12/29/2015
#####################################################

#####################################################
# DISCLAIMER
# I am not providing any kind of warranty. This has been thoroughly tested in my environments but I cannot guarantee that this script is not without bugs.
# Thank you
#####################################################

#####################################################
# LICENSE
# The MIT License (MIT)
#
# Copyright (c) 2015 Brad Schmidt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#####################################################

#####################################################
# TODOS
# Add more logging (Actual logging instead of print)
# Add gui? Prompt for values and file location
# Once bug in the API for large advanced searches is fixes, switch to advanced searches from smart groups.
#####################################################

#####################################################
# HOW TO USE
# 1. Make an API user and give it the rights specified BELOW
# 2. Save a csv file of your serial numbers and asset tags. Format is assettag,serialnumber. In other words, the first column is the asset tag and the second is the serialnumber.
# 3. Run the python script - be patient, this could take a while. Creating the groups can take a long time in large environments. Touching each record isn't blazing fast either but I did put in a progress counter ;)
# 4. Profit?
#####################################################

#####################################################
# HARD CODED VALUES

# JSS URL
jss_host = "https://jss.com"
jss_port = "8443"
jss_path = "" #Example: "jss" for a JSS at https://www.company.com:8443/jss

# API User needs the following rights:
####### 1. Create/Read Computer Smart Groups
####### 2. Create/Read Mobile Device Smart Groups
####### 3. Update Computer records
####### 4. Update Mobile Device records

# JSS API Username and Password
jss_username = "api_user"
jss_password = "potato"

# Place the csv in the same directory as the script.
csv_file_name = 'filename.csv'

# Turn on or off device types False turns it off, True turns it on. 
computersMode = True
# computersMode = False
mobileDevicesMode = True
# mobileDevicesMode = False

#####################################################

#####################################################
#####################################################
#####################################################
#### You should not need to edit below this line ####
#####################################################
#####################################################
#####################################################

# Import required libraries
import requests
import csv
import os

# Start the Mobile Device import
def mobileDevices():
    if mobileDevicesMode == True:
        print "---Starting the Mobile Device pass---"
        mobileDevices,status_code = getMobileDevices()
        if len(mobileDevices) != 0:
            if status_code == 200:
                print "Got some mobile devices back!"

            else:
                createMobileDeviceGroup()

            mobileDevicesTotal = len(mobileDevices)
            counter = 0
            for md in mobileDevices:
                    serialNumber = md.get("serial_number")
                    assetTag = assetLookup(serialNumber)
                    updateMobileDeviceInventory(serialNumber,assetTag)
                    counter = counter + 1
                    print "Submitting %s of %s devices" % (counter,mobileDevicesTotal)
            print "---Finished importing asset tags for Mobile Devices---"
        else:
            print "No Mobile Devices Found"
    else:
        print "Mobile Device Mode: Off"

# Start the Computer import
def computers():
    if computersMode == True:
        print "---Starting the Computer pass---"
        computers,status_code = getComputers()
        if len(computers) != 0:
            if status_code == 200:
                print "Got some computers back!"

            else:
                createComputerGroup()

            computersTotal = len(computers)
            counter = 0
            for md in computers:
                    serialNumber = md.get("serial_number")
                    assetTag = assetLookup(serialNumber)
                    updateComputerInventory(serialNumber,assetTag)
                    counter = counter + 1
                    print "Submitting %s of %s devices" % (counter,computersTotal)
            print "---Finished importing asset tags for Computers---"
        else:
            print "No Computers Found"
    else:
        print "Computer Mode: off"

# Create the computer group if it doesn't exist
def createComputerGroup():
    print "Stand by, creating the Smart Group and this does take a while in larger environments..."
    body = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><computer_group><name>_API-Asset-Tag-Importer</name><is_smart>true</is_smart><criteria><size>1</size><criterion><name>Asset Tag</name><priority>0</priority><and_or>and</and_or><search_type>is</search_type><value></value></criterion></criteria><computers/></computer_group>"
    r = requests.post(jss_host + ':' + str(jss_port) + jss_path + '/JSSResource/computergroups/id/-1', auth=(jss_username,jss_password), data=body)
    if r.status_code == 201:
        print "Group created! Status code: %s " % r.status_code # This should be logging not printing
        computers()
    else:
        print "Something went wrong. Status code: %s " % r.status_code # This should be logging not printing
        print r.text

# Create the mobile device group if it doesn't exist
def createMobileDeviceGroup():
    print "Stand by, creating the Smart Group and this does take a while in larger environments..."
    body = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><mobile_device_group><name>_API-Asset-Tag-Importer</name><is_smart>true</is_smart><criteria><size>1</size><criterion><name>Asset Tag</name><priority>0</priority><and_or>and</and_or><search_type>is</search_type><value></value></criterion></criteria><mobile_devices/></mobile_device_group>"
    r = requests.post(jss_host + ':' + str(jss_port) + jss_path + '/JSSResource/mobiledevicegroups/id/-1', auth=(jss_username,jss_password), data=body)
    if r.status_code == 201:
        print "Group created!. Status code: %s " % r.status_code # This should be logging not printing
        # Jump back to the main program for mobile devices
        mobileDevices()
    else:
        print "Something went wrong. Status code: %s " % r.status_code # This should be logging not printing
        print r.text

# Get the mobile devices without asset tags
def getMobileDevices():

    r = requests.get(jss_host + ':' + str(jss_port) + jss_path + '/JSSResource/mobiledevicegroups/name/_API-Asset-Tag-Importer', headers={'Accept': 'application/json'}, auth=(jss_username,jss_password))
    try:
        report_data = r.json()["mobile_device_group"]
        return (report_data["mobile_devices"],r.status_code)
    except:
        report_data = None
        return (report_data,r.status_code)


# Get the computers without asset tags
def getComputers():

    r = requests.get(jss_host + ':' + str(jss_port) + jss_path + '/JSSResource/computergroups/name/_API-Asset-Tag-Importer', headers={'Accept': 'application/json'}, auth=(jss_username,jss_password))
    try:
        report_data = r.json()["computer_group"]
        return (report_data["computers"],r.status_code)
    except:
        report_data = None
        return (report_data,r.status_code)

# Read the csv
def assetLookup(serial):
    csvFile = os.path.join(os.path.dirname(__file__), csv_file_name)
    file = open(csvFile)
    filereader = csv.reader(file)
    for row in filereader:
        try:
            #print row[1]
            if row[1] == serial:
                asset = row[0]
                # strip dashs for my environment
                asset_tag = (asset.translate(None, "-"))
                return asset_tag
        except:
            continue

# Submit the asset tag to the JSS
def updateMobileDeviceInventory(serialNumber,assetTag):

    if assetTag != None:

        print "\tSubmitting command to update device " + serialNumber + "..."
        try:
            body = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><mobile_device><general><asset_tag>%s</asset_tag></general></mobile_device>" % assetTag
            r = requests.put(jss_host + ':' + jss_port + jss_path + '/JSSResource/mobiledevices/serialnumber/' + serialNumber, auth=(jss_username,jss_password), data=body)
            #print r.text
            print ""
        except:
            print "\tUnknown error submitting PUT XML."
    else:
        print "Skipping Serial Number: %s...Not found in csv" % serialNumber

def updateComputerInventory(serialNumber,assetTag):

    if assetTag != None:

        print "\tSubmitting command to update device " + serialNumber + "..."
        try:
            body = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><computer><general><asset_tag>%s</asset_tag></general></computer>" % assetTag
            r = requests.put(jss_host + ':' + jss_port + jss_path + '/JSSResource/computers/serialnumber/' + serialNumber, auth=(jss_username,jss_password), data=body)
            #print r.text
            print ""
        except:
            print "\tUnknown error submitting PUT XML."
    else:
        print "Skipping Serial Number: %s...Not found in csv" % serialNumber


if __name__ == '__main__':
    computers()
    mobileDevices()