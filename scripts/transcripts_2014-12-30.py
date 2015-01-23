from __future__ import division, print_function
import os
import re
import string
import sys

    
def count_words(s):
	s = s.split()
	non_words = ['-','--']
	return sum([x not in non_words for x in s])

def was_cut_off(w):
	if w in ['-','--']:
		return True
	return False

def find_docket_number(text):
    ''' Takes the oral argument text as input and returns the docket number for the case. '''
    match = re.search(r'No\.\s(\d+\-\d+)', text)
    if not match:
        print('no docket found')
        sys.exit(1)
    return match.group(1)

def get_docket_winners(infile):
    ''' Takes as input the Supreme Court Database file and returns 
        a dictionary whose key is the docket number and value is 
        the case winner ('Petitioner'/'Respondent')
    '''
    ## Create a dictionary to store info
    d = {}
    ## open the file and read the header
    f = open(infile, 'r')
    header = f.next().split('\t')
    ## Find index of "majority" column. Note the quotes are in the name.
    dcol = header.index('docket')
    #print('dcol = ', dcol)
    wcol = header.index('partyWinning')
    for line in f:
        split_line = line.split('\t')
        docket = split_line[dcol]
        winner = 'Res'
        if split_line[wcol] == '1':
            winner = 'Pet'
        if docket not in d:
            d[docket] = winner            
    f.close()
    return d


def get_petitioners_and_respondents_speakers(text):
    ''' This function takes as input a bit of the transcript that lists the people speaking,
        extracts their names and which side they argue for, and returns two lists:
        petitioners and respondents, or rather the lawyers on their behalf. 
    '''
    ## Define an empty dictionary
    d = {}
    
    ## get the portion of the transcript between APPEARANCES and CONTENTS or more typically C O N T E N T S   
    start = text.find('APPEARANCES:') + len('APPEARANCES:') 
    end = text.find('C O N T E N T S')
    names_text = text[start:end].strip()
    #print(names_text)
    
    ## find all appearances of 'Petitioner/appellant' and 'Respondent/appellee' to identify the solicitors associated with each.
    split_names_text = names_text.split('.\n')
    for entry in split_names_text:
        ## Quick check to make sure the phrase 'on behalf of' appears in the line. If not, skip it.
        if not any(x in entry for x in ['ehalf', 'upport']):
            continue
        ## Extract the lawyer's last name
        name = entry.split(',')[0]
        name = name.split()[-1]
        ## Find out if they are on behalf of petitioner or respondent
        if any(x in entry for x in ['etition' , 'ppellant']):
            d[name] = 'Pet'
        elif any(x in entry for x in ['espond' , 'ppellee']):
            d[name] = 'Res'
        else:
            d[name] = 'Other'
    return d
    ## return a dictionary keyed by name with value 'petitioner'/'respondent'/'other'? I need to know if each speaker is a winner or loser.
    ## ********************* Here ^^^^^



def main():
    if 0:
        scdb_file = '/Users/nasrallah/Desktop/scotus_project/SCOTUS_2/data/SCDB_2014_01_justiceCentered_Citation_tab.txt'
        winner_dict = get_docket_winners(scdb_file)
    if 0:    
        years = ['2012','2013']
        ## list all files in the directory
        main_path = '/Users/nasrallah/Desktop/scotus_project/scotus_transcript/'
        for year in years:
            this_path = main_path + year + '/'
            files = [ os.path.join(this_path,x) for x in os.listdir(this_path) if '.txt' in x ]
            ## for each file:
            for file in files:
                #print(file)   
                ## Read in the whole file as string to search a few things
                f = open(file, 'rU')
                text = f.read()
                f.close()
                ## Find the docket number from the text file to look up the votes in the SCDB using the 'docket' column
                docket = find_docket_number(text)
                print('\ndocket:',docket)
                oral_roles = get_petitioners_and_respondents_speakers(text)
                #for x in oral_roles: print(x, oral_roles[x])
                ## Convert Petitioner/respondent into winner/loser for this case.
                if docket in winner_dict:
                    for x in oral_roles:
                        if oral_roles is not 'Other':
                            if winner_dict[docket] == oral_roles[x]:
                                oral_roles[x] = 'W'
                            else:
                                oral_roles[x] = 'L'
                for x in oral_roles: print(x, oral_roles[x])

    ## Store all the dockets. The dockets here are the id numbers assigned to the case by the supreme court. These were redundant prior to 1971 or so. The SCDB stores these as 'docket' and has their own identification as 'docket_id'
    
    ## Use the dockets to query the SCDB to find the petitioner, respondent, winner and loser or each case. maybe even which justices voted how. Create an object to store these info.
    ## This can be done for all dockets in the SCDB in advance, not just for the ones being queried here.
        
    #sys.exit(1)
    
    transcript_file = "/Users/nasrallah/Desktop/scotus_project/scotus_python/greece_mod.txt"
    #transcript_file = "/Users/nasrallah/Desktop/scotus_project/scotus_transcript/2013/12-536_7l48.txt"
    f = open(transcript_file, 'rU')
    text = f.read()
    f.close()

#     match = re.findall(r'ORAL\sARGUMENT\sOF.*ON\sBEHALF\sOF', text)
#     if not match:
#         print('text not found')
#         sys.exit(1)
#     print(match)   
    #s = text.split('ORAL ARGUMENT OF')
    #print(len(s))
    ## Can classify the lawyers speaking as on behalf of the petitioner or respondent. The SCDB has a 'partyWinning' column that is 0/1/2 for the petitioner losing/winning/unclear
    ## Should probably also note from the SCDB if the outcome was a reversal or not. The Court tends to reverse lower Courts, so just being on the petitioner side that lost in lower Courts might help your chances of success.

   
   
   ## When you encounter a new speaker, see if they represent the respondent or petitioner (winner or loser)
   
   
    ## find the docket number
    
    
    #sys.exit()
    
    ## Read whole file and extract the justice and lawyer names using regular expressions
    prefaces = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Chief Justice', 'Justice']
    #f = open(transcript_file, 'r')
    
    
    ## The eight speaking justices and the three (for this case) other speakers
    speakers = ['MR. HUNGAR', 'MR. GERSHENGORN', 'MR. LAYCOCK', 'CHIEF JUSTICE ROBERTS', 'JUSTICE SCALIA', 'JUSTICE KENNEDY', 'JUSTICE GINSBURG', 'JUSTICE BREYER', 'JUSTICE ALITO', 'JUSTICE SOTOMAYOR', 'JUSTICE KAGAN']
    ## A dictionary to store the word counts for each speaking turn for all speakers
    words = {}	
    cutoffs = {}
    for p in speakers:
        words[p] = []
        cutoffs[p] = 0
    ## Initialize some variables
    word_count = 0
    speaker = ""
    
    ## open the file and read line by line.
    ## When a new speaker appears, store the words counted for the previous speaker.
    transcript = open(transcript_file, "rU")
    for line in transcript:
        #print(line)
        last_word = line.split()[-1]
        #print(last_word)
        if line.find(':') != -1:
            split_colon = line.split(':')
            potential_speaker = split_colon[0].strip()
            ## If everything preceding a colon is all uppercase, we have a new speaker
            if potential_speaker.isupper():
                #print('potential speaker:', potential_speaker)	
                ## score the last entry if necessary
                if speaker in words:
                    #print('old speaker:', speaker) 		
                    words[speaker].append(word_count)
                    if last_word in ['-','--']:
                        cutoffs[speaker] += 1
				## reset the word count
                #print('word_count', word_count)
                word_count = 0	
				## update the speaker
                speaker = potential_speaker
				## Add the rest of this line to the word count
                if len(split_colon[1]) > 0:
                    word_count += count_words(split_colon[1])
			## if whatever precedes a maybe-existent colon is not all uppercase, it is speech. Add it to the running total.
            else:
                word_count += count_words(line)
        else:
            word_count += count_words(line)
    
    sys.exit(1)
    
    print('Saving output to file....')
    
	## Save the output to file
    outfile = '/Users/nasrallah/Desktop/greece_words.txt'
    with open(outfile, 'w') as f:
        f.write('Word counts for Greece v Galloway\n')
        for w in words:
            f.write( w + ',' + ','.join([str(x) for x in words[w]]) + '\n' )

    outfile = '/Users/nasrallah/Desktop/greece_cutoffs.txt'
    with open(outfile, 'w') as f:
        f.write('Cutoff counts for Greece v Galloway\n')
        for w in cutoffs:
            f.write( w + ',' + str(cutoffs[w]) + '\n' )




if __name__ == '__main__':
    main()
