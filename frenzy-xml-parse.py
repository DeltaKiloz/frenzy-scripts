#!/bin/env/python

###############################################################################################################
## [Title]: frenzy-xml-parse.py -- a script to parse the xml report from Phishing Frenzy
## [Author]: @delta_kiloz
##-------------------------------------------------------------------------------------------------------------
## [Details]:
## This script is intended to be run against the .XML report that is generated from the Phishing Frenzy applcation
## at the conclusion of the Phishing Campaign. The original .PDF and .XLSX reports that are gneerated by Phishing
## Frenzy didn't provide enough information. The .XML report does pull the information I wanted to use, however
## not in a very good presentable format. This script will parse through the .XML report and present the data
## on the victims in a format easily ingestable by your target audience.
##-------------------------------------------------------------------------------------------------------------
## [Warning]:
## This script comes as-is with no promise of functionality or accuracy.  I strictly wrote it for personal use
## I have no plans to maintain updates, I did not write it to be efficient and in some cases you may find the
## functions may not produce the desired results so use at your own risk/discretion.
##-------------------------------------------------------------------------------------------------------------
## [Modification, Distribution, and Attribution]:
## You are free to modify and/or distribute this script as you wish.  I only ask that you maintain original
## author attribution and not attempt to sell it or incorporate it into any commercial offering. With the exeption
## that this may be included in the Phishing Frenzy application repo.
###############################################################################################################

from xml.etree import ElementTree
import fpdf
from optparse import OptionParser
import sys
import os

#sets up for creating a PDF
pdf = fpdf.FPDF(format='letter')
pdf.add_page()
print "\n[+] Make sure you are running this script from within the same directory"
print "[+] as the .XML file is located.\n\n"

#parses the user input to validate what's being entered into the console
parser=OptionParser(usage='%prog [OPTIONS] [INPUT_FILE]')
parser.add_option('-i','--input',help='The .XML document produced from Phishing Frenzy\'s report output',dest='source_file')
(options,args)=parser.parse_args()

#Checks input option, if none provided then print Usage
if options.source_file == None:
    parser.print_help()
    sys.exit(2)

#Checks to see if input file exists, if not print error
if options.source_file == True:
    if not os.path.exists(options.source_file):
        print "\n[+] Error, Source .XML file does not exist. Please check your input below:\n"
        print options.source_file
        sys.exit(2)

#reads in the XML file that your exported from Phishing Frenzy application
with open(options.source_file, 'rt') as f:
    tree = ElementTree.parse(f)

#will use these later to count how many emails were sent and how many Times
#the phishing links were clicked.
i=0
y=0
j=0

#prints the title of your report along with some details of the campaign
#at the top of the page. You can customize with your team's name
pdf.set_font("Arial", 'B', size=19)
pdf.cell(190,9,'Your Organization Name', 0,1,'C')
pdf.cell(190,9,'Phishing Campaign Results', 0,1,'C')
pdf.set_font("Arial", 'B', size=12)
pdf.cell(190,5,'',0,1,'L')

pdf.cell(190,5,'Campaign Overview',0,1,'L')
pdf.set_font("Arial", size=12)
for x in tree.iter("campaign"):
    name = x.find('.//name').text
    desc = x.find('.//description').text
    sender = x.find('.//baits/bait/from').text
    pdf.cell(190,5,"Name: {name}".format(name=name), 0,1,'L')
    pdf.cell(190,5,"Description: {desc}".format(desc=desc),0,1,'L')
    pdf.cell(190,5,"Sent from: {sender}".format(sender=sender),0,1,'L')

#the following several lines provide a quick summary of the overall campaign's
#success rate.
pdf.cell(190,5,'',0,1,'L')
pdf.set_font("Arial", 'B', size=12)
pdf.cell(190,5,'Campaign Summary',0,1,'L')
pdf.set_font("Arial", size=12)
#counts up how many phishing emails were sent out successfully in this campaign
for n in tree.findall(".//bait"):
    status = n.find('.//status').text
    if status:
        i += 1
pdf.cell(190,5,'Emails Sent: ' + str(i), 0, 1, 'L')

#counts up how many victims actually clicked on the link, based on weather or
#not their IP address was recorded. Not the best metric for this, but it works.
for z in tree.findall(".//victim"):
    ipz = z.find('.//ip-address')
    ipz = ipz.text if ipz is not None else 'Nope'
    if ipz is not 'Nope':
        y += 1
pdf.cell(190,5,'Emails Clicked: ' + str(y), 0, 1, 'L')
j = (float(y)/float(i))*100
u = str(j)
u = u[:-8]
pdf.cell(190,5,'Success: ' + str(u) + '%', 0 ,1, 'L')
pdf.cell(190,5,'',0,1,'L')


#This For loop goes through and finds all the victims (which are the folks that
#actually clicked on the link) and prints out each time the victim clicked on
#the phishing link, along with the victim's browser user-agent, and the IP
#address from where the victim originated.
pdf.set_font("Arial", 'B', size=14)
pdf.cell(190,5,'Victims That Activated (clicked) the link', 0, 1, 'L')
pdf.set_font("Arial", size=12)
for node in tree.findall(".//victim"):
    email = node.find('.//email-address').text
    last = node.find('.//lastname').text
    first = node.find('.//firstname').text
    for elem in node.findall(".//visit"):
        ip = elem.find('.//ip-address')
        ip = ip.text if ip is not None else 'Did not click link'
        browse = elem.find('.//browser')
        browse = browse.text if browse is not None else 'Did not click link'
        updated = elem.find('.//updated-at')
        updated = updated.text if updated is not None else 'Did not click link'
        if ip is not 'Did not click link':
            pdf.cell(190,5,"Name: {first} {last}".format(first=first, last=last),'T',1,'L')
            pdf.cell(190,5,"Email Address: {email}".format(email=email),0,1,'L')
            pdf.cell(190,5,"IP address: {ip}".format(ip=ip),0,1,'L')
            pdf.cell(190,5,"User-Agent: {browse}".format(browse=browse),0,1,'L')
            pdf.cell(190,5,"Clicked Date: {updated}".format(updated=updated),0,1,'L')
            pdf.cell(190,5,'',0,1,'L')

#outputs your results in a nice tidy PDF in the same directory you ran the script from
pdf.output(options.source_file + "_results.pdf")
print "\n[+] Script complete, file: " + options.source_file + "_results.pdf has been produced"
