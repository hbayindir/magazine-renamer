#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Magazine Renamer - A RegEx based file renamer for IEEE Magazines and more.
Copyright (C) 2022  Hakan Bayindir

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Created on 17 April 2022

@author: Hakan Bayindir
'''

# Core imports goes here.
import sys
import os
import os.path
import re

# Utility imports are next.
import argparse
import logging

# Program wide defaults. Change the way you like.
LOGGING_LEVEL = logging.INFO
LOGFILE_PATH = None

'''
@summary: A dead-simple, naive short month name to month number conversion function.
@warning: This function is no way optimized.  
'''
def monthStringToNumber(monthString):
    if monthString.casefold() == 'jan'.casefold() or monthString.casefold() == 'january'.casefold():
        return '01'

    elif monthString.casefold() == 'feb'.casefold() or monthString.casefold() == 'february'.casefold():
        return '02'
    
    elif monthString.casefold() == 'mar'.casefold() or monthString.casefold() == 'march'.casefold():
        return '03'    
    
    elif monthString.casefold() == 'apr'.casefold() or monthString.casefold() == 'april'.casefold():
        return '04'
        
    elif monthString.casefold() == 'may'.casefold():
        return '05'
        
    elif monthString.casefold() == 'jun'.casefold() or monthString.casefold() == 'june'.casefold():
        return '06'
        
    elif monthString.casefold() == 'jul'.casefold() or monthString.casefold() == 'july'.casefold():
        return '07'
        
    elif monthString.casefold() == 'aug'.casefold() or monthString.casefold() == 'august'.casefold():
        return '08'
        
    elif monthString.casefold() == 'sep'.casefold() or monthString.casefold() == 'september'.casefold():
        return '09'
        
    elif monthString.casefold() == 'oct'.casefold() or monthString.casefold() == 'october'.casefold():
        return '10'
        
    elif monthString.casefold() == 'nov'.casefold() or monthString.casefold() == 'november'.casefold():
        return '11'
        
    elif monthString.casefold() == 'dec'.casefold() or monthString.casefold() == 'december'.casefold():
        return '12'
    
    else:
        return '00'

'''
@summary: A dead-simple, naive short edition to human readable edition string conversion function.
@warning: This function is no way optimized.  
'''
def convertEditionString(editionString):
    if editionString.casefold() == 'INT'.casefold():
        return 'International'
    
    elif editionString.casefold() == 'NA'.casefold():
        return 'North America'

if __name__ == '__main__':

    # Let's parse some arguments.
    argumentParser = argparse.ArgumentParser()

    argumentParser.add_argument ('file', metavar='FILE', help='File(s) to be renamed.', type=str, nargs='+')
    
    argumentParser.add_argument ('-s', '--simulate', help='Do not actually rename the files, but show actions and quit.', action='store_true', default=False)
    
    # Verbosity settings are implemented as an mutually exclusive group.
    verbosityGroup = argumentParser.add_mutually_exclusive_group()
    verbosityGroup.add_argument ('-v', '--verbose', help='Print more detail about the process. Using more than one -v increases verbosity.', action='count', default=0)
    verbosityGroup.add_argument ('-q', '--quiet', help='Do not print anything to console (overrides verbose).', action='store_true', default=False)

    # Version always comes last.
    argumentParser.add_argument ('-V', '--version', help='Print ' + argumentParser.prog + ' version and exit.', action='version', version=argumentParser.prog + ' version 0.0.2')    

    arguments = argumentParser.parse_args()

    # At this point we have the required arguments, let's start with logging duties.
    if arguments.verbose != None:
        if arguments.verbose == 1:
            LOGGING_LEVEL = logging.INFO
        elif arguments.verbose >= 2:
            LOGGING_LEVEL = logging.DEBUG

    # Let's set the logger up.
    try:
        logging.basicConfig(filename=LOGFILE_PATH, level=LOGGING_LEVEL, format='%(levelname)s: %(message)s')

        # Get the local logger and start.
        localLogger = logging.getLogger('main')
        
        # Handle the quiet switch here, since it directly affects the logger.
        if arguments.quiet == True:
            logging.disable(logging.CRITICAL)  # Critical is the highest built-in level. This line disables CRITICAL and below.

        localLogger.debug('Logger setup completed.')
        localLogger.debug('%s is starting.', sys.argv[0])
    except IOError as exception:
        print ('Something about disk I/O went bad: ' + str(exception), file=sys.stderr)
        sys.exit(1)
    
    # Let's print some information about what we're going to do.
    localLogger.debug('Files to rename are: %s', str(arguments.file))
    localLogger.debug('Total file count: %s', str(len(arguments.file)))
    localLogger.debug('Simulation state is %s', str(arguments.simulate))
    
    # We're going to match some regular expressions. We'll compile them here for conciseness.
    regexIEEESpectrumV1 = re.compile('Spectrum_[\d]{5}_[A-Z][a-z]{2}_[\d]{4}\.PDF')
    regexIEEESpectrumV2 = re.compile('[\d]{2}_Spectrum_[\d]{4}\.pdf')
    regexIEEESpectrumV2A = re.compile('[\d]{2}_Spectrum_[\d]{4}[_][A-Z]{2,3}\.pdf')
    regexIEEESpectrumV2B = re.compile('[\d]{2}_Spectrum_[\d]{4}[\.][A-Z]{2,3}\.pdf')
    regexIEEESpectrumV2C = re.compile('[\d]{2}_Spectrum_[\d]{2}\.pdf')
    regexIEEETheInstituteV1 = re.compile('ieee_institute_[a-z]*[\d]{4}\.pdf')
    regexIEEETheInstituteV1A = re.compile('ieee_institute_[a-z]*_[\d]{4}\.pdf')
    regexIEEETheInstituteV2 = re.compile('TheInstitute_[A-Z][a-z]{2}_[\d]{4}\.pdf')
    regexIEEEComputationalIntelligenceV1 = re.compile('CIG_[\d]{8}_[A-Z][a-z]{2}_[\d]{4}\.PDF')
    regexIEEEComputationalIntelligenceV2 = re.compile('ieee_computationalintelligence_[0-9]{6}\.pdf')
    regexIEEEPotentialsV1 = re.compile('POT_[\d]{8}_[A-Z][a-z]{2}_[\d]{4}\.PDF')
    
    # Just allocate a variable for a new file name.
    newFileName = None
    
    # Let's start on working files. Get them one by one, and test against RegEx rules.
    for file in arguments.file:
        localLogger.debug('Working on file  ' + str(file) + '.')
        
        # Need to divide the path and file itself before diving deeper, and need to preserve that path for merging later.
        if os.path.isfile(file) == False:
            localLogger.debug('Path ' + file + ' is not a file, skipping.')
            continue
        
        (filePath, fileToRename) = os.path.split(file)
        (fileName, fileExtension) = os.path.splitext(fileToRename)
        localLogger.debug('File \'%s\' is located at \'%s\'.', str(fileToRename), str(filePath))
        localLogger.debug('File name is \'%s\', with extension \'%s\'', fileName, fileExtension)
        
        #IEEE Spectrum, V1.
        if regexIEEESpectrumV1.match(fileToRename):
            localLogger.info('%s is an IEEE Spectrum Magazine file, with V1 format.', fileToRename)
            
            # First divide file name into its parts via split.
            fileNameParts = fileName.split('_')
            
            localLogger.debug('Month to convert is %s.', fileNameParts[2])
            localLogger.debug('Year is %s.', fileNameParts[3])
            
            # Let's convert month name to number.
            monthNumber = monthStringToNumber(fileNameParts[2])
            localLogger.debug('New month identifier is \'%s\'.', monthNumber) 
            
            # We have everything we need, so assemble the new filename here.
            newFileName = 'IEEE Spectrum ' + fileNameParts[3] + '-' + monthNumber + fileExtension.lower()
            localLogger.info('File will be renamed to \'%s\'.', newFileName)
                    
        elif regexIEEESpectrumV2.match(fileToRename):
            localLogger.info('%s is an IEEE Spectrum Magazine file, with V2 format.', fileToRename)
            
            # This one is actually easy, since we're just going to rearrange some fields together.
            fileNameParts = fileName.split('_')
            
            localLogger.debug('Month is %s.', fileNameParts[0])
            localLogger.debug('Year is %s.', fileNameParts[2])
            
            # We have everything we need, so assemble the new filename here.
            newFileName = 'IEEE Spectrum ' + fileNameParts[2] + '-' + fileNameParts[0] + fileExtension.lower()
            localLogger.info('File will be renamed to \'%s\'.', newFileName)      
            
        elif regexIEEESpectrumV2A.match(fileToRename):
            localLogger.info('%s is an IEEE Spectrum Magazine file, with V2A format.', fileToRename)
            
            # This is a variation on V2, but contains region information (NA for North America, INT for International).
            fileNameParts = fileName.split('_')
            
            localLogger.debug('Month is %s.', fileNameParts[0])
            localLogger.debug('Year is %s.', fileNameParts[2])
            localLogger.debug('Edition to convert is %s.', fileNameParts[3])
            
            longEditionString = convertEditionString(fileNameParts[3])
            localLogger.debug('New edition string is \'%s\'.', longEditionString)
            
            # At this point we have everything we need, let's assemble the new filename.
            newFileName = 'IEEE Spectrum ' + fileNameParts[2] + '-' + fileNameParts[0] + ' ' + longEditionString + fileExtension.lower()
            localLogger.info('File will be renamed to \'%s\'.', newFileName)
            
        elif regexIEEESpectrumV2B.match(fileToRename):
            localLogger.info('%s is an IEEE Spectrum Magazine file, with V2B format.', fileToRename)
            
            # This is a further variation on V2A, but contains region information after a dot (NA for North America, INT for International).
            fileNameParts = fileName.split('_')
            magazine_year = fileNameParts[2].split('.')[0]
            magazine_edition = fileNameParts[2].split('.')[1]
            
            localLogger.debug('Month is %s.', fileNameParts[0])
            localLogger.debug('Year is %s.', magazine_year)
            localLogger.debug('Edition to convert is %s.', magazine_edition)
            
            longEditionString = convertEditionString(magazine_edition)
            localLogger.debug('New edition string is \'%s\'.', longEditionString)
            
            # At this point we have everything we need, let's assemble the new filename.
            newFileName = 'IEEE Spectrum ' + magazine_year + '-' + fileNameParts[0] + ' ' + longEditionString + fileExtension.lower()
            localLogger.info('File will be renamed to \'%s\'.', newFileName)
        
        elif regexIEEESpectrumV2C.match(fileToRename):
            localLogger.info('%s is an IEEE Spectrum Magazine file, with V2C format.', fileToRename)
            
            # This is a direct variation of V2, but with two digit years.
            fileNameParts = fileName.split('_')
            
            localLogger.debug('Month is %s.', fileNameParts[0])
            localLogger.debug('Year is %s.', fileNameParts[2])
            
            # We have everything we need, so assemble the new filename here.
            newFileName = 'IEEE Spectrum ' + '20' + fileNameParts[2] + '-' + fileNameParts[0] + fileExtension.lower()
            localLogger.info('File will be renamed to \'%s\'.', newFileName)
        
        elif regexIEEETheInstituteV1.match(fileToRename):
            localLogger.info('%s is an IEEE The Institute Magazine file, with V1 format.', fileToRename)
            
            # This format has month and year concatenated, so we need to make some harder-coded extractions.
            # Get the year and month only, we know the rest.
            fileNameParts = fileName.split('_')[2]
            fileYear = fileNameParts[-4:] # Get last 4 characters.
            fileMonth = fileNameParts[:-4] # Get from beginning to last 4 characters.
            
            localLogger.debug('Month to convert is %s.', fileMonth)
            monthNumber = monthStringToNumber(fileMonth)
            localLogger.debug('New month identifier is %s.', monthNumber)
            
            newFileName = 'IEEE The Institute ' + fileYear + '-' + monthNumber + fileExtension.lower()
            localLogger.info('File will be renamed to \'%s\'.', newFileName)
            
        elif regexIEEETheInstituteV1A.match(fileToRename):
            localLogger.info('%s is an IEEE The Institute Magazine file, with V1A format.', fileToRename)
            
            # This is a better variation on V1, with better separation between month and year.
            # Get the year and month only, we know the rest.
            
            localLogger.debug('Month to convert is %s.', fileName.split('_')[2])
            monthNumber = monthStringToNumber(fileName.split('_')[2])
            localLogger.debug('New month identifier is %s.', monthNumber)
            
            newFileName = 'IEEE The Institute ' + fileName.split('_')[3] + '-' + monthNumber + fileExtension.lower()
            localLogger.info('File will be renamed to \'%s\'.', newFileName)
        
        elif regexIEEETheInstituteV2.match(fileToRename):
            localLogger.info('%s is an IEEE The Institute Magazine file, with V2 format.', fileToRename)
            
            # This is a variation on V1A, with some changing in name casing and date format, but it can be parsed the same way.
            # Get the year and month only, we know the rest.
            
            localLogger.debug('Month to convert is %s.', fileName.split('_')[1])
            monthNumber = monthStringToNumber(fileName.split('_')[1])
            localLogger.debug('New month identifier is %s.', monthNumber)
            
            newFileName = 'IEEE The Institute ' + fileName.split('_')[2] + '-' + monthNumber + fileExtension.lower()
            localLogger.info('File will be renamed to \'%s\'.', newFileName)
        
        elif regexIEEEComputationalIntelligenceV1.match(fileToRename):
            localLogger.info('%s is an IEEE Computational Intelligence Magazine file, with V1 format.', fileToRename)
            
            # This is again some very concatenated format, but it can be easily disassembled into its parts with harder-coded ways.
            monthAndYear = fileName.split('_')[1]
            fileMonth = monthAndYear[-4:-2]
            fileYear = monthAndYear[:-4]
            
            newFileName = 'IEEE Computational Intelligence Magazine ' + fileYear + '-' + fileMonth + fileExtension.lower()
            localLogger.info('File will be renamed to \'%s\'.', newFileName)
            
        
        elif regexIEEEComputationalIntelligenceV2.match(fileToRename):
            localLogger.info('%s is an IEEE Computational Intelligence Magazine file, with V2 format.', fileToRename)
            
            # This is again some very concatenated format, but it can be easily disassembled into its parts with harder-coded ways.
            monthAndYear = fileName.split('_')[2]
            fileMonth = monthAndYear[-2:]
            fileYear = monthAndYear[:-2]
            
            newFileName = 'IEEE Computational Intelligence Magazine ' + fileYear + '-' + fileMonth + fileExtension.lower()
            localLogger.info('File will be renamed to \'%s\'.', newFileName)
            
        elif regexIEEEPotentialsV1.match(fileToRename):
            localLogger.info('%s is an IEEE Potentials Magazine file, with V1 format.', fileToRename)
        
            # This is again some very concatenated format, but it can be easily disassembled into its parts with harder-coded ways.
            monthAndYear = fileName.split('_')[1]
            fileMonth = monthAndYear[-4:-2]
            fileYear = monthAndYear[:-4]
            
            newFileName = 'IEEE Potentials ' + fileYear + '-' + fileMonth + fileExtension.lower()
            localLogger.info('File will be renamed to \'%s\'.', newFileName)
        else:
            localLogger.info('%s in an unknown file, skipping.', fileToRename)
            continue
        
        if arguments.simulate == False:
            # Let it rip!
            os.rename(file, os.path.join(filePath, newFileName))
        
    sys.exit(0)
    pass