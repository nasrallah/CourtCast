## 2015-01-05 changed pattern matching for finding names of lawyers to allow for whitespace after '.' before '\n'

from __future__ import division, print_function
import numpy as np
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
        #print('*'*40,'no docket found in this text')
        match = re.search(r'No\.\s*(\d+)', text)
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
    if end == -1:
        end = text.find('CONTENTS')
    if end == -1:
        end = text.find('PROCEED')
    if end == -1:
        end = text.find('P R O C E E D')
    if end == -1:
        end = text.find('CHIEF') 
    names_text = text[start:end].strip()
    #print(names_text)
    
    ## The lawyers appearing are separated by a period followed by maybe some spaces followed by a newline. 
    split_names_text = re.split('\.[ ]*\n', names_text)
    #for x in split_names_text: print(x)
    ## find all appearances of 'Petitioner/appellant' and 'Respondent/appellee' to identify the solicitors associated with each.
    for entry in split_names_text:
        #print(entry,'\n')
        ## Quick check to make sure the phrase 'on behalf of' appears in the line. this is unneeded, but can help point out weird cases, like docket 11-9307 which has a court-appointed attorney, presumably for the petitioner although it never says so.
        #if not any(x in entry for x in ['ehalf', 'upport', 'for']):
        #    print('*'*20,entry)
        ## Extract the lawyer's last name
        name = entry.strip().split(',')[0]
        if not any(x in name for x in ['ESQ', 'Jr.', 'III']):
            name = name.split()[-1]
        else:
            #print('!'*30, name, name.split()[-2])
            name = name.split()[-2]
        if name.isupper():
            #print(name)
            ## Find out if they are on behalf of petitioner or respondent
            if any(x in entry for x in ['etition' , 'ppellant', 'emand', 'evers', 'laintiff']):
                d[name] = 'Pet'
            elif any(x in entry for x in ['espond' , 'ppellee', 'efendant']):
                d[name] = 'Res'
            else:
                d[name] = 'Other'
    
    ## Do some checks here. Sometimes one side is appointed by the court and not labelled as for petitioner or respondent. Make sure both sides are represented and convert the 'Other' to that unrepresented side.        
    if not all(x in d.values() for x in ['Pet','Res']):
        #print('both pet and res not found')
        #for x in d: print(x, d[x])
        ## Find out if it is the petitioner or respondent that is not represented
        unrepresented = 'Pet'
        if 'Res' not in d.values():
            unrepresented = 'Res'
        ## This will change any lawyer not the 'Pet' or 'Res' (whichever one was found) into the unrepresented side
        for lawyer in d:
            if d[lawyer] not in ['Pet','Res']:
                d[lawyer] = unrepresented
        #for x in d: print(x, d[x])

    return d



def get_winning_lawyers(lawyers, winning_side):
    ''' takes a dictionary of key:lawyers_names and value: pet/res 
        and a string ('Pet'/'Res') saying who won the case (from SCDB)
        and returns a new dictionary with key lawyer_names and value W/L
    '''
    ## Convert petitioner/respondent into winner/loser for this case.
    outcomes = {}
    for x in lawyers:
        if lawyers[x] == 'Other':
            outcomes[x] = 'Other'
        elif lawyers[x] == winning_side:
            outcomes[x] = 'W'
        else:
            outcomes[x] = 'L'
    return outcomes


def count_cutoffs_and_words(text): 
    ''' This function parses the oral arguments. It identifies when someone has been cut off (-,--)
        and counts both the number of these occurrences and the words spoken before another speaker begins,
        whether they stopped talking due to interruption or not.
        The function takes the oral transcript text as input and returns 2 dictionaries:
        - one with key last name and value the number of times they were cut off
        - one with key last name and value a list of the number of words spoken before stopping talking.
    '''   
    ## Get just the argument portion of the transcript
    start = text.find('P R O C E E D')
    if start == -1:
        start = text.find('PROCEEDINGS')
    if start == -1:
        start = 0
    end = text.rfind('Whereupon')
    if end == -1:
        end = (re.search(r'[Cc]ase\sis\s[now\s]*submitted', text)).start()
    if any(x == -1 for x in [start,end]):
        print('\n*** There was a problem finding the oral argument section')
        print(start,end)
    #print(start,end)
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
            #print(line)
            #print(potential_speaker)
            ## Use only the last name of the speaker, because there is at least one instance of MR. X vs M R. X
            if potential_speaker != '':
                    potential_speaker = potential_speaker.split()[-1]
            ## If everything preceding a colon is all uppercase, we have a new speaker
            if potential_speaker.isupper():
                #print('potential speaker:', potential_speaker)	
                ## score the last entry if necessary
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

    ## Define the years we want to analyze
    first_year = '2005'
    last_year = '2013'

    ## Get the main directory in which each years' cases are stored
    main_path = '/Users/nasrallah/Desktop/scotus_project/scotus_transcript/'
    
    ## Counters for how often the most interrupted side loses the case
    interrupt_lose = 0
    interrupt_win = 0
    ## Counters for most-lawyers
    num_more_res = 0
    num_more_pet = 0
    ## Counters for Petitioner and Respondent victories
    pet_wins = 0
    res_wins = 0
    ## Counters for most words spoken winning/losing
    loq_win = 0
    loq_lose = 0
    
    ## Define a dictionary for all cases properties. Key is the docket, Values will be other dictionaries.
    cases = {}    
    ## Define a container for the combination of most-interrupted and most-lawyers
    factors = {}
    scdb_file = '/Users/nasrallah/Desktop/scotus_project/SCOTUS_2/data/SCDB_2014_01_justiceCentered_Citation_tab.txt'
    winner_dict = get_docket_winners(scdb_file)

    ## Analyze the transcripts for all cases in each year    
    years = map(str, range(int(first_year),int(last_year)+1))
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
            #print('\ndocket:',docket)
            if docket in cases:
                print(docket,'appears multiple times')
                continue
            
            ## Ensure the case is found in the SCDB. If not, skip it.
            if docket not in winner_dict:
                print(docket, 'not found in winner_dict', '*'*30)
                continue
            
            ## Is the winning side the Petitioner or Respondent?
            winning_side = winner_dict[docket] 
            
            ## Get from the text which lawyer supported which side (petitioner/respondent)
            sides = get_petitioners_and_respondents_speakers(text)
            #for x in sides: print(x, sides[x])
                             
            if winner_dict[docket] == 'Pet':
                pet_wins += 1
            elif winner_dict[docket] == 'Res':
                res_wins += 1
            else:
                print('hmm. neither the petitioner nor repondent won?')
            
            ## Convert petitioner/respondent into winner/loser for this case.
            outcomes = get_winning_lawyers(sides, winner_dict[docket])
             
            ## Analyze the oral argument text for the number of cutoffs and the sentence length distributions
            cutoffs, ind_words = count_cutoffs_and_words(text)
            
            ## Print some stuff about this case
            print('\ndocket:',docket)
            for x in sides: print(x, sides[x], cutoffs[x]) 
            #for x in outcomes: print(x, outcomes[x]) 
            #for c in cutoffs: print('\t', c, cutoffs[c])
            #for w in ind_words: print(w, sum(ind_words[w]))

            ## Create dictionary keyed by side with value the total words spoken by all lawyers on that side
            #for x in sides: print(x, sides[x], sum(ind_words[x])) 
            side_words = {}
            for v in sides.values():
                side_words[v] = 0
            for x in sides:
                if x in ind_words:
                    side_words[sides[x]] += sum(ind_words[x])
            #for x in side_words: print(x, side_words[x])
            print('winner:', winning_side)
            loq_side = max(side_words.iteritems(), key=operator.itemgetter(1))[0]
            if loq_side == winning_side:
                loq_win += 1
            elif loq_side == 'Other':
                print('loquacious amicus','$'*20)
            else:
                loq_lose +=1    

            
            

            ############### Everything below here can be moved outside the loop and operate on the cases dictionary.
            
            ## If the the most interrupted person is on the losing side, call that right. Else wrong.
            most_interrupted = max(cutoffs.iteritems(), key=operator.itemgetter(1))[0]
            #print('most interrupted:', most_interrupted)
            if most_interrupted in outcomes:
                if outcomes[most_interrupted] == 'L':
                    interrupt_lose += 1
                elif outcomes[most_interrupted] == 'W':
                    interrupt_win += 1
                    #for c in cutoffs: print('\t', c, cutoffs[c])
                else:
                    print(docket, 'most_interrupted', most_interrupted, outcomes[most_interrupted])       
            else:
                #print('most interrupted neither won nor lost:', sides[most_interrupted])
                for x in sides: print(x, sides[x])
                for x in outcomes: print(x, outcomes[x])
            ## See if there were more lawyers on winning/losing side
            num_pet = sides.values().count('Pet')
            num_res = sides.values().count('Res')
            more_lawyers = 'T'
            if num_pet > num_res:
                num_more_pet += 1
                more_lawyers = 'P'
            elif num_pet < num_res:
                num_more_res += 1
                more_lawyers = 'R'
                
            tuple = (winner_dict[docket], more_lawyers, sides[most_interrupted], loq_side)
            #tuple = (winner_dict[docket], more_lawyers, outcomes[most_interrupted])
            cases[docket] = tuple
            if tuple not in factors:
                factors[tuple] = 0
            factors[tuple] += 1

    
    print('\nResults:\n', '_'*30)
    print('pet_wins:', pet_wins, 'res_wins', res_wins)                
    print('num_more_pet', num_more_pet, 'num_more_res', num_more_res)
    print('interrupt_lose', interrupt_lose, 'interrupt_win', interrupt_win)   
    print('loq_win:',loq_win,'loq_lose:',loq_lose)
    print('(winning_side, more_lawyers, most_interrupted, most_loquacious)') 
    #for fac in factors:
    #    print(fac, factors[fac])
    for h in ['Pet', 'Res']:
        for i in ['P', 'T', 'R']:
            for j in ['Pet', 'Res']:
                for k in ['Pet', 'Res']:
                    t = (h,i,j,k)
                    print(t, factors[t])
        print()


    p = np.empty(0)
    for i in ['P', 'T', 'R']:
        for j in ['Pet', 'Res']:
            for k in ['Pet', 'Res']:
                t = ('Pet',i,j,k)
                p = np.append(p,factors[t])
    
    r = np.empty(0)
    for i in ['P', 'T', 'R']:
        for j in ['Pet', 'Res']:
            for k in ['Pet', 'Res']:
                t = ('Res',i,j,k)
                r = np.append(r,factors[t])
    
    print('N(w|cond):', p)
    print('N(l|cond):', r)
    print('P(w|cond):')
    print( (p/(p+r))[0:4] )
    print( (p/(p+r))[4:8] )
    print( (p/(p+r))[8:12] )
    print( sum(p[2:4]) / (sum(p[2:4]) + sum(r[2:4])) )
    
    ######### Something may be wrong here. In 2012-2013 the P(win|Pet,R,R) = 0.75
    ######### In 2005-2013 it is 0.38. Granted 2012-2013 sample size is only 4, but still the direction seems wrong. More likely to win if interrupted more?
    ### Marginal P(win | pet, tie)? (ptp + ptr) / (ptp + ptr + rtp + rtr)


    sys.exit()
           
    
    print('Saving output to file....')
    
	## Save the output to file
    outfile = '/Users/nasrallah/Desktop/greece_words.txt'
    with open(outfile, 'w') as f:
        f.write('Word counts for Greece v Galloway\n')
        for w in ind_words:
            f.write( w + ',' + ','.join([str(x) for x in ind_words[w]]) + '\n' )

    outfile = '/Users/nasrallah/Desktop/greece_cutoffs.txt'
    with open(outfile, 'w') as f:
        f.write('Cutoff counts for Greece v Galloway\n')
        for w in cutoffs:
            f.write( w + ',' + str(cutoffs[w]) + '\n' )




if __name__ == '__main__':
    main()
