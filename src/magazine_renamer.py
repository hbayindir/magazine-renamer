#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Magazine Renamer - A RegEx based file_to_work_on renamer for IEEE Magazines and more.
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
import os.path
import re

# Utility imports are next.
import argparse
import logging

# Program wide defaults. Change the way you like.
LOGGING_LEVEL = logging.WARNING
LOGFILE_PATH = None

'''
@summary: A dead-simple, naive short month name to month number conversion function.
@warning: This function is no way optimized.
'''

month_number_dictionary = dict()
month_number_dictionary['jan'.casefold()] = '01'
month_number_dictionary['feb'.casefold()] = '02'
month_number_dictionary['mar'.casefold()] = '03'
month_number_dictionary['apr'.casefold()] = '04'
month_number_dictionary['may'.casefold()] = '05'
month_number_dictionary['jun'.casefold()] = '06'
month_number_dictionary['jul'.casefold()] = '07'
month_number_dictionary['aug'.casefold()] = '08'
month_number_dictionary['sep'.casefold()] = '09'
month_number_dictionary['oct'.casefold()] = '10'
month_number_dictionary['nov'.casefold()] = '11'
month_number_dictionary['dec'.casefold()] = '12'

edition_dictionary = dict()
edition_dictionary['INT'.casefold()] = 'International'
edition_dictionary['NA'.casefold()] = 'North America'

def month_string_to_number(month_string):
    '''
    @summary: Get a month name as a string, get its month number back.
    @warning: Case and language insensitive.
    '''
    return month_number_dictionary.get(month_string[0:3].casefold(), '00')

def convert_edition_string(edition_string):
    '''
    @summary: A simple, short edition to human readable edition string conversion function.
    @change: 20220427 - Can handle other editions as well.
    '''
    return edition_dictionary.get(edition_string, 'Other')

if __name__ == '__main__':

    # Let's parse some arguments.
    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument ('file', metavar='FILE', help='File(s) to be renamed.', type=str, nargs='+')
    
    argument_parser.add_argument ('-s', '--simulate', help='Do not actually rename the files, but show actions and quit.', action='store_true', default=False)
    
    # Verbosity settings are implemented as an mutually exclusive group.
    verbosity_group = argument_parser.add_mutually_exclusive_group()
    verbosity_group.add_argument ('-v', '--verbose', help='Print more detail about the process. Using more than one -v increases verbosity.', action='count', default=0)
    verbosity_group.add_argument ('-q', '--quiet', help='Do not print anything to console (overrides verbose).', action='store_true', default=False)

    # Version always comes last.
    argument_parser.add_argument ('-V', '--version', help='Print ' + argument_parser.prog + ' version and exit.', action='version', version=argument_parser.prog + ' version 0.0.4')    

    arguments = argument_parser.parse_args()

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
        local_logger = logging.getLogger('main')
        
        # Handle the quiet switch here, since it directly affects the logger.
        if arguments.quiet == True:
            logging.disable(logging.CRITICAL)  # Critical is the highest built-in level. This line disables CRITICAL and below.

        local_logger.debug('Logger setup completed.')
        local_logger.debug('%s is starting.', sys.argv[0])
    except IOError as exception:
        print ('Something about disk I/O went bad: ' + str(exception))
        sys.exit(1)
    
    # Let's print some information about what we're going to do.
    local_logger.debug('Files to rename are: %s', str(arguments.file))
    local_logger.debug('Total file_to_work_on count: %s', str(len(arguments.file)))
    local_logger.debug('Simulation state is %s', str(arguments.simulate))
    
    # We're going to match some regular expressions. We'll compile them here for conciseness.
    regex_ieee_spectrum_v_1 = re.compile('Spectrum_[\d]{5}_[A-Z][a-z]{2}_[\d]{4}\.PDF')
    regex_ieee_spectrum_v_2 = re.compile('[\d]{2}_Spectrum_[\d]{4}\.pdf')
    regex_ieee_spectrum_v2a = re.compile('[\d]{2}_Spectrum_[\d]{4}[_][A-Z]{2,3}\.pdf')
    regex_ieee_spectrum_v2b = re.compile('[\d]{2}_Spectrum_[\d]{4}[\.][A-Z]{2,3}\.pdf')
    regex_ieee_spectrum_v2c = re.compile('[\d]{2}_Spectrum_[\d]{2}\.pdf')
    regex_ieee_the_institute_v1 = re.compile('ieee_institute_[a-z]*[\d]{4}\.pdf')
    regex_ieee_the_institute_v1a = re.compile('ieee_institute_[a-z]*_[\d]{4}\.pdf')
    regex_ieee_the_institute_v2 = re.compile('TheInstitute_[A-Z][a-z]{2}_[\d]{4}\.pdf')
    regex_ieee_computational_intelligence_v1 = re.compile('CIG_[\d]{8}_[A-Z][a-z]{2}_[\d]{4}\.PDF')
    regex_ieee_computational_intelligence_v2 = re.compile('ieee_computationalintelligence_[0-9]{6}\.pdf')
    regex_ieee_potentials_v1 = re.compile('POT_[\d]{8}_[A-Z][a-z]{2}_[\d]{4}\.PDF')
    
    # Just allocate a variable for a new file_to_work_on name.
    new_file_name = None
    
    # Let's start on working files. Get them one by one, and test against RegEx rules.
    for file_to_work_on in arguments.file:
        local_logger.debug('Working on file_to_work_on  ' + str(file_to_work_on) + '.')
        
        # Need to divide the path and file_to_work_on itself before diving deeper, and need to preserve that path for merging later.
        if os.path.isfile(file_to_work_on) == False:
            local_logger.debug('Path ' + file_to_work_on + ' is not a file_to_work_on, skipping.')
            continue
        
        (file_path, file_to_rename) = os.path.split(file_to_work_on)
        (file_name, file_extension) = os.path.splitext(file_to_rename)
        local_logger.debug('File \'%s\' is located at \'%s\'.', str(file_to_rename), str(file_path))
        local_logger.debug('File name is \'%s\', with extension \'%s\'', file_name, file_extension)
        
        #IEEE Spectrum, V1.
        if regex_ieee_spectrum_v_1.match(file_to_rename):
            local_logger.info('%s is an IEEE Spectrum Magazine file_to_work_on, with V1 format.', file_to_rename)
            
            # First divide file_to_work_on name into its parts via split.
            file_name_parts = file_name.split('_')
            
            local_logger.debug('Month to convert is %s.', file_name_parts[2])
            local_logger.debug('Year is %s.', file_name_parts[3])
            
            # Let's convert month name to number.
            month_number = month_string_to_number(file_name_parts[2])
            local_logger.debug('New month identifier is \'%s\'.', month_number) 
            
            # We have everything we need, so assemble the new filename here.
            new_file_name = 'IEEE Spectrum ' + file_name_parts[3] + '-' + month_number + file_extension.lower()
            local_logger.info('File will be renamed to \'%s\'.', new_file_name)
                    
        elif regex_ieee_spectrum_v_2.match(file_to_rename):
            local_logger.info('%s is an IEEE Spectrum Magazine file_to_work_on, with V2 format.', file_to_rename)
            
            # This one is actually easy, since we're just going to rearrange some fields together.
            file_name_parts = file_name.split('_')
            
            local_logger.debug('Month is %s.', file_name_parts[0])
            local_logger.debug('Year is %s.', file_name_parts[2])
            
            # We have everything we need, so assemble the new filename here.
            new_file_name = 'IEEE Spectrum ' + file_name_parts[2] + '-' + file_name_parts[0] + file_extension.lower()
            local_logger.info('File will be renamed to \'%s\'.', new_file_name)      
            
        elif regex_ieee_spectrum_v2a.match(file_to_rename):
            local_logger.info('%s is an IEEE Spectrum Magazine file_to_work_on, with V2A format.', file_to_rename)
            
            # This is a variation on V2, but contains region information (NA for North America, INT for International).
            file_name_parts = file_name.split('_')
            
            local_logger.debug('Month is %s.', file_name_parts[0])
            local_logger.debug('Year is %s.', file_name_parts[2])
            local_logger.debug('Edition to convert is %s.', file_name_parts[3])
            
            longEditionString = convert_edition_string(file_name_parts[3])
            local_logger.debug('New edition string is \'%s\'.', longEditionString)
            
            # At this point we have everything we need, let's assemble the new filename.
            new_file_name = 'IEEE Spectrum ' + file_name_parts[2] + '-' + file_name_parts[0] + ' ' + longEditionString + file_extension.lower()
            local_logger.info('File will be renamed to \'%s\'.', new_file_name)
            
        elif regex_ieee_spectrum_v2b.match(file_to_rename):
            local_logger.info('%s is an IEEE Spectrum Magazine file_to_work_on, with V2B format.', file_to_rename)
            
            # This is a further variation on V2A, but contains region information after a dot (NA for North America, INT for International).
            file_name_parts = file_name.split('_')
            magazine_year = file_name_parts[2].split('.')[0]
            magazine_edition = file_name_parts[2].split('.')[1]
            
            local_logger.debug('Month is %s.', file_name_parts[0])
            local_logger.debug('Year is %s.', magazine_year)
            local_logger.debug('Edition to convert is %s.', magazine_edition)
            
            longEditionString = convert_edition_string(magazine_edition)
            local_logger.debug('New edition string is \'%s\'.', longEditionString)
            
            # At this point we have everything we need, let's assemble the new filename.
            new_file_name = 'IEEE Spectrum ' + magazine_year + '-' + file_name_parts[0] + ' ' + longEditionString + file_extension.lower()
            local_logger.info('File will be renamed to \'%s\'.', new_file_name)
        
        elif regex_ieee_spectrum_v2c.match(file_to_rename):
            local_logger.info('%s is an IEEE Spectrum Magazine file_to_work_on, with V2C format.', file_to_rename)
            
            # This is a direct variation of V2, but with two digit years.
            file_name_parts = file_name.split('_')
            
            local_logger.debug('Month is %s.', file_name_parts[0])
            local_logger.debug('Year is %s.', file_name_parts[2])
            
            # We have everything we need, so assemble the new filename here.
            new_file_name = 'IEEE Spectrum ' + '20' + file_name_parts[2] + '-' + file_name_parts[0] + file_extension.lower()
            local_logger.info('File will be renamed to \'%s\'.', new_file_name)
        
        elif regex_ieee_the_institute_v1.match(file_to_rename):
            local_logger.info('%s is an IEEE The Institute Magazine file_to_work_on, with V1 format.', file_to_rename)
            
            # This format has month and year concatenated, so we need to make some harder-coded extractions.
            # Get the year and month only, we know the rest.
            file_name_parts = file_name.split('_')[2]
            file_year = file_name_parts[-4:] # Get last 4 characters.
            file_month = file_name_parts[:-4] # Get from beginning to last 4 characters.
            
            local_logger.debug('Month to convert is %s.', file_month)
            month_number = month_string_to_number(file_month)
            local_logger.debug('New month identifier is %s.', month_number)
            
            new_file_name = 'IEEE The Institute ' + file_year + '-' + month_number + file_extension.lower()
            local_logger.info('File will be renamed to \'%s\'.', new_file_name)
            
        elif regex_ieee_the_institute_v1a.match(file_to_rename):
            local_logger.info('%s is an IEEE The Institute Magazine file_to_work_on, with V1A format.', file_to_rename)
            
            # This is a better variation on V1, with better separation between month and year.
            # Get the year and month only, we know the rest.
            
            local_logger.debug('Month to convert is %s.', file_name.split('_')[2])
            month_number = month_string_to_number(file_name.split('_')[2])
            local_logger.debug('New month identifier is %s.', month_number)
            
            new_file_name = 'IEEE The Institute ' + file_name.split('_')[3] + '-' + month_number + file_extension.lower()
            local_logger.info('File will be renamed to \'%s\'.', new_file_name)
        
        elif regex_ieee_the_institute_v2.match(file_to_rename):
            local_logger.info('%s is an IEEE The Institute Magazine file_to_work_on, with V2 format.', file_to_rename)
            
            # This is a variation on V1A, with some changing in name casing and date format, but it can be parsed the same way.
            # Get the year and month only, we know the rest.
            
            local_logger.debug('Month to convert is %s.', file_name.split('_')[1])
            month_number = month_string_to_number(file_name.split('_')[1])
            local_logger.debug('New month identifier is %s.', month_number)
            
            new_file_name = 'IEEE The Institute ' + file_name.split('_')[2] + '-' + month_number + file_extension.lower()
            local_logger.info('File will be renamed to \'%s\'.', new_file_name)
        
        elif regex_ieee_computational_intelligence_v1.match(file_to_rename):
            local_logger.info('%s is an IEEE Computational Intelligence Magazine file_to_work_on, with V1 format.', file_to_rename)
            
            # This is again some very concatenated format, but it can be easily disassembled into its parts with harder-coded ways.
            month_and_year = file_name.split('_')[1]
            file_month = month_and_year[-4:-2]
            file_year = month_and_year[:-4]
            
            new_file_name = 'IEEE Computational Intelligence Magazine ' + file_year + '-' + file_month + file_extension.lower()
            local_logger.info('File will be renamed to \'%s\'.', new_file_name)
            
        
        elif regex_ieee_computational_intelligence_v2.match(file_to_rename):
            local_logger.info('%s is an IEEE Computational Intelligence Magazine file_to_work_on, with V2 format.', file_to_rename)
            
            # This is again some very concatenated format, but it can be easily disassembled into its parts with harder-coded ways.
            month_and_year = file_name.split('_')[2]
            file_month = month_and_year[-2:]
            file_year = month_and_year[:-2]
            
            new_file_name = 'IEEE Computational Intelligence Magazine ' + file_year + '-' + file_month + file_extension.lower()
            local_logger.info('File will be renamed to \'%s\'.', new_file_name)
            
        elif regex_ieee_potentials_v1.match(file_to_rename):
            local_logger.info('%s is an IEEE Potentials Magazine file_to_work_on, with V1 format.', file_to_rename)
        
            # This is again some very concatenated format, but it can be easily disassembled into its parts with harder-coded ways.
            month_and_year = file_name.split('_')[1]
            file_month = month_and_year[-4:-2]
            file_year = month_and_year[:-4]
            
            new_file_name = 'IEEE Potentials ' + file_year + '-' + file_month + file_extension.lower()
            local_logger.info('File will be renamed to \'%s\'.', new_file_name)
        else:
            local_logger.info('%s in an unknown file_to_work_on, skipping.', file_to_rename)
            continue
        
        if arguments.simulate == False:
            # Let it rip!
            os.rename(file_to_work_on, os.path.join(file_path, new_file_name))
        
    sys.exit(0)
    pass