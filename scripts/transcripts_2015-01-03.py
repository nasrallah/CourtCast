from __future__ import division, print_function
import operator
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
        the case winner ('Pet'/'Res') [petitioner/respondent]
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
        ## Quick check to make sure the phrase 'on behalf of' appears in the line. this is unneeded, but can help point out weird cases, like docket 11-9307 which has a court-appointed attorney, presumably for the petitioner although it never says so.
        #if not any(x in entry for x in ['ehalf', 'upport', 'for']):
        #    print('*'*20,entry)
        ## Extract the lawyer's last name
        name = entry.split(',')[0]
        name = name.split()[-1]
        if name.isupper():
            ## Find out if they are on behalf of petitioner or respondent
            if any(x in entry for x in ['etition' , 'ppellant']):
                d[name] = 'Pet'
            elif any(x in entry for x in ['espond' , 'ppellee']):
                d[name] = 'Res'
            else:
                d[name] = 'Other'
    return d



def count_cutoffs_and_words(text): 
    ''' This function parses the oral arguments. It identifies when someone has been cut off (-,--)
        and counts both the number of these occurrences and the words spoken before another speaker begins,
        whether they stopped talking due to interruption or not.
        The function takes the oral transcript text as input and returns 2 dictionaries:
        - one with key last name and value the number of times they were cut off
        - one with key last name and value a list of the number of words spoken before stopping talking.
        '''   
    ## Get just the argument portion of the transcript
    start = text.find('P R O C E E D I N G S')
    end = text.find('Whereupon')
    if any(x == -1 for x in [start,end]):
        print('\n*** There was a problem finding the oral argument section')
    arg_text = text[start:end]
    ## A dictionary to store the word counts for each speaking turn for all speakers
    cutoffs = {}
    words = {}	
    ## Initialize some variables
    word_count = 0
    speaker = "" 
    for line in arg_text.split('\n'):
        line = line.strip()
        #print(line)
        if ':' in line:
            split_colon = line.split(':')
            potential_speaker = split_colon[0]
            potential_speaker = potential_speaker.split()[-1]
            ## If everything preceding a colon is all uppercase, we have a new speaker
            if potential_speaker.isupper():
                #print('potential speaker:', potential_speaker)	
                ## score the last entry if necessary
                ## Use only the last name of the speaker, because there is at least one instance of MR. X vs M R. X
                if speaker != '':
                    ## If a new speaker, initialize containers
                    if speaker not in words:
                        words[speaker] = []
                        cutoffs[speaker] = 0
                    #print('old speaker:', speaker) 	
                    ## Process the data for the speaker	who just stopped talking
                    words[speaker].append(word_count)
                    if prev_line_last_word[-1] == '-':
                        cutoffs[speaker] += 1
				## reset the word count
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
        ## store the last word of this line. If the next line is a new speaker, we will use it to see if this speaker was interrupted.
        prev_line_last_word = line.split()[-1]
        #print(prev_line_last_word)
        
        ## Clarence Thomas speaks?
        #if speaker == 'THOMAS': print('*'*30, line)

    return cutoffs, words



def main():
    if 1:
        ## Counters for how often the most interrupted side loses the case
        right = 0
        wrong = 0
        ## Counters for most-lawyers
        num_more_res = 0
        num_more_pet = 0
        ## Counters for Petitioner and Respondent victories
        pet_wins = 0
        res_wins = 0
        ## Define a container for the combination of most-interrupted and most-lawyers
        factors = {}
        scdb_file = '/Users/nasrallah/Desktop/scotus_project/SCOTUS_2/data/SCDB_2014_01_justiceCentered_Citation_tab.txt'
        winner_dict = get_docket_winners(scdb_file)
        years = ['2012','2013']
        ## list all files in the directory
        main_path = '/Users/nasrallah/Desktop/scotus_project/scotus_transcript/'
        for year in years:
            this_path = main_path + year + '/'
            files = [ os.path.join(this_path,x) for x in os.listdir(this_path) if 'mod.txt' in x ]
            ## for each file:
            for file in files:
                ## Get the argument text
                #print(file)   
                ## Read in the whole file as string to search a few things
                f = open(file, 'rU')
                text = f.read()
                f.close()
                
                ## Change all pesky 'McGREGOR' 'McCONNELL and DiNARDO to all caps
                text = re.sub(r'[DM][aci]c*[A-Z]+', lambda pat: pat.group().upper(), text)
                ## Find the docket number from the text file to look up the votes in the SCDB using the 'docket' column
                docket = find_docket_number(text)
                ## Get from the SCDB for each case which lawyer supported which side (petitioner/respondent)
                roles = get_petitioners_and_respondents_speakers(text)
                #for x in roles: print(x, roles[x])
                
                ## Ensure the case is found in the SCDB. If not, skip it.
                if docket not in winner_dict:
                    print(docket, 'not found in winner_dict', '*'*30)
                    continue
                if winner_dict[docket] == 'Pet':
                    pet_wins += 1
                elif winner_dict[docket] == 'Res':
                    res_wins += 1
                else:
                    print('hmm. neither the petitioner nor repondent won?')
                
                ## Convert petitioner/respondent into winner/loser for this case.
                outcomes = {}
                for x in roles:
                    if roles[x] == 'Other':
                        outcomes[x] = 'Other'
                    elif roles[x] == winner_dict[docket]:
                        outcomes[x] = 'W'
                    else:
                        outcomes[x] = 'L'
                cutoffs, words = count_cutoffs_and_words(text)
                
                ## Print some stuff about this case
                #print('\ndocket:',docket)
                #for x in outcomes: print(x, outcomes[x]) 
                #for c in cutoffs: print('\t', c, cutoffs[c]) 
                
                ## If the the most interrupted person is on the losing side, call that right. Else wrong.
                most_interrupted = max(cutoffs.iteritems(), key=operator.itemgetter(1))[0]
                #print('most interrupted:', most_interrupted)
                if most_interrupted in outcomes:
                    if outcomes[most_interrupted] == 'L':
                        right += 1
                    elif outcomes[most_interrupted] == 'W':
                        wrong += 1
                        #for c in cutoffs: print('\t', c, cutoffs[c])
                else:
                    print('most interrupted neither won nor lost:', roles[most_interrupted])
                ## See if there were more lawyers on winning/losing side
                num_pet = roles.values().count('Pet')
                num_res = roles.values().count('Res')
                more_lawyers = 'T'
                if num_pet > num_res:
                    num_more_pet += 1
                    more_lawyers = 'P'
                elif num_pet < num_res:
                    num_more_res += 1
                    more_lawyers = 'R'
                    
                tuple = (winner_dict[docket], more_lawyers, outcomes[most_interrupted])
                if tuple not in factors:
                    factors[tuple] = 0
                factors[tuple] += 1
        
        print('pet_wins:', pet_wins, 'res_wins', res_wins)                
        print('num_more_pet', num_more_pet, 'num_more_res', num_more_res)
        print('right', right, 'wrong', wrong)    
        for fac in factors:
            print(fac, factors[fac])

    sys.exit()





    ## Store all the dockets. The dockets here are the id numbers assigned to the case by the supreme court. These were redundant prior to 1971 or so. The SCDB stores these as 'docket' and has their own identification as 'docket_id'
    ## Use the dockets to query the SCDB to find the petitioner, respondent, winner and loser or each case. maybe even which justices voted how. Create an object to store these info.
    ## This can be done for all dockets in the SCDB in advance, not just for the ones being queried here.
    
    transcript_file = "/Users/nasrallah/Desktop/scotus_project/scotus_python/greece_mod.txt"
    #transcript_file = "/Users/nasrallah/Desktop/scotus_project/scotus_transcript/2013/12-536_7l48.txt"
    f = open(transcript_file, 'rU')
    text = f.read()
    f.close()

    ## Can classify the lawyers speaking as on behalf of the petitioner or respondent. The SCDB has a 'partyWinning' column that is 0/1/2 for the petitioner losing/winning/unclear
    ## Should probably also note from the SCDB if the outcome was a reversal or not. The Court tends to reverse lower Courts, so just being on the petitioner side that lost in lower Courts might help your chances of success.
 
    ## open the file and read line by line.
    ## When a new speaker appears, store the words counted for the previous speaker.
    cutoffs, words = count_cutoffs_and_words(text)
    for c in cutoffs:
        print(c, cutoffs[c]) 
           
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
