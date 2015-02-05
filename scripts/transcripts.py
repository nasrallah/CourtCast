## 2105-01-23 Big change is how I count tied interruptions. Eliminated separate class for ties.
## Pet must be strictly greater than Res to be called 'Pet' else 'Res'.

## 2015-01-21 I've done some cleanup and rearranging. Notably the creation of DataFrame objects. 
## I now read data for all cases from SCDB and store it. Then the loop over transcripts is really 
## to extract the key features: interruptions, amicus support, and maybe others. But I still have a
## function to get the winners again inside this loop, and I create a factors dictionary of
## key_features tuple that is redundant with the info in the DataFrame. For cleanup later.

## 2015-01-09 Trying to fix the assignment of petitioner and respondent using ordering.

## 2015-01-08 compiled a similar statistic for interruptions to see which side, not which individual, was interrupted most.

## 2015-01-07 compiled word counts for each side. Turns out that if you know who is petitioner, who has more lawyers, 
## and who was interrupted, then knowing who got more words in doesn't tell you anything significant. 
## Possibly because it doesn't matter and possible b/c sample sizes are quite low at that point.

## 2015-01-05 changed pattern matching for finding names of lawyers to allow for whitespace after '.' before '\n'

from __future__ import division, print_function
import numpy as np
import pandas as pd
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

def get_year_and_month(datestring):
    if datestring != 'NA':
        argYear, argMonth, argDay = datestring.split('-')
        return argYear, argMonth
    else:
        return 'NA', 'NA'


def get_SCDB_info(infile):
    ''' Takes as input the Supreme Court Database file and returns 
        a DataFrame indexed by docket number and columns the case properties
    '''
    ## Create a dictionary to store info
    d = {}
    ## open the file and read the header
    f = open(infile, 'r')
    header = f.next().split('\t')
    ## Find index of columns of interest.
    dcol = header.index('docket')
    ncol = header.index('caseName')
    wcol = header.index('partyWinning')
    majcol = header.index('majVotes')
    mincol = header.index('minVotes')
    issuecol = header.index('issueArea')
    decdatecol = header.index('dateDecision')
    argdatecol = header.index('dateArgument')
    reargdatecol = header.index('dateRearg')
    
    for line in f:
        sl = line.split('\t')
        docket = sl[dcol]
        caseName = sl[ncol]
        winner = 'Pet' if sl[wcol] == '1' else 'Res'
        majority_votes = sl[majcol]
        minority_votes = sl[mincol]
        decDate = sl[decdatecol]        ## Change to datetime object?
        argDate = sl[argdatecol]        ## same
        reargDate = sl[reargdatecol]
        if reargDate != 'NA':
            argDate = reargDate
        ## If we still don't have an argument date, just use the decision date
        if argDate == 'NA':
            argDate = decDate
        argYear, argMonth = get_year_and_month(argDate)

        if docket not in d:
            d[docket] = {}
            d[docket]['caseName'] = caseName
            d[docket]['partyWinning'] = winner
            d[docket]['majVotes'] = majority_votes
            d[docket]['minVotes'] = minority_votes 
            d[docket]['argDate'] = argDate  
            d[docket]['decDate'] = decDate
            d[docket]['argMonth'] = argMonth  
            d[docket]['argYear'] = argYear 
    f.close()
    return pd.DataFrame.from_dict(d,orient='index')


def append_new_case_info(infile, case_info):
    ''' Takes a text file of the new case info and the existing DataFrame and 
        returns a DataFrame with the new entries appended at the end.
        Based heavily on the get_SCDB_info() function but without a few columns.'''
        
    ## Create a dictionary to store info
    d = {}
    ## open the file and read the header
    f = open(infile, 'r')
    header = f.next().split('\t')
    ## Find index of columns of interest.
    dcol = header.index('docket')
    ncol = header.index('caseName')
    wcol = header.index('partyWinning')
    majcol = header.index('majVotes')
    mincol = header.index('minVotes')
    argdatecol = header.index('argDate')
    
    for line in f:
        sl = line.split('\t')
        #print(sl)
        docket = sl[dcol]
        if docket not in case_info.index:
            caseName = sl[ncol].strip()
            winner = sl[wcol]
            majority_votes = sl[majcol]
            minority_votes = sl[mincol]
            argDate = sl[argdatecol]        
            argMonth, argYear = argDate.split(', ')

            if docket not in d:
                d[docket] = {}
                d[docket]['caseName'] = caseName
                d[docket]['partyWinning'] = winner
                d[docket]['majVotes'] = majority_votes
                d[docket]['minVotes'] = minority_votes 
                d[docket]['argDate'] = argDate  
                d[docket]['argMonth'] = argMonth  
                d[docket]['argYear'] = argYear 
    f.close()
    ## convert to a DataFrame and append to the scdb case_info
    d = pd.DataFrame.from_dict(d,orient='index')
    return case_info.append(d)
    
        

def find_docket_number(text):
    ''' Takes the oral argument text as input and returns the docket number for the case. '''
    match = re.search(r'No\.\s*(\d+\-\d+)', text)
    if not match:
        #match = re.search(r'No\.\s*(\d+)', text)
        match = re.search(r'No\.\s*(.+)', text)
        #print(match.group(1)    )       ########## START FROM HERE FOR AKWARD DOCKET NUMBERS************************
    if not match:
        print('*'*40,'no docket found in this text')

    return match.group(1)


# def get_docket_winners(infile):
#     ''' Takes as input the Supreme Court Database file and returns 
#         a dictionary whose key is the docket number and value is 
#         the case winner ('Pet'/'Res') [petitioner/respondent]
#     '''
#     ## Create a dictionary to store info
#     d = {}
#     ## open the file and read the header
#     f = open(infile, 'r')
#     header = f.next().split('\t')
#     ## Find index of "majority" column. Note the quotes are in the name.
#     dcol = header.index('docket')
#     #print('dcol = ', dcol)
#     wcol = header.index('partyWinning')
#     for line in f:
#         split_line = line.split('\t')
#         docket = split_line[dcol]
#         winner = 'Res'
#         if split_line[wcol] == '1':
#             winner = 'Pet'
#         if docket not in d:
#             d[docket] = winner            
#     f.close()
#     return d


def get_docket_winners(case_info):
    ''' Takes as input the DataFrame of case info from SCDB and new cases,
        and returns only a dictionary whose key is the docket number and value is 
        the case winner ('Pet'/'Res'/'?') [petitioner/respondent/undecided]
    '''
    return case_info.partyWinning.to_dict()



def get_case_names(infile):
    ''' Takes as input the Supreme Court Database file and returns 
        a dictionary whose key is the docket number and value is 
        the case name.
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
    
    ## Define an empty dictionary
    d = {}
    ## Define a variable to keep track of which was the last represented side, sa amici following can support that side
    last_side = 'Pet'

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
            elif 'neither' in entry:
                d[name] = 'Other'
            else:
                if 'Res' in d.values():
                    d[name] = 'Res'
                elif 'Pet' not in d.values():
                    d[name] = 'Pet'
                ## This is the dubious part. It assumes there are only 2 lawyers and that b/c 'Pet' is in d the other must be Res....
                else:
                    d[name] = 'Res'
                #for x in split_names_text: print('-',x,'\n')
                #print(d[name])

    ## Do some checks here. Sometimes one side is appointed by the court and not labelled as for petitioner or respondent. Make sure both sides are represented and convert the 'Other' to that unrepresented side.        
    if not all(x in d.values() for x in ['Pet','Res']):
        #print('both pet and res not found')
        #for x in d: print(x, d[x])
        if 'Pet' in d:
            pass
        elif 'Res' in d:
            pass
        else:
            print('well, shit.')
            print(d.values())
        ## Find out if it is the petitioner or respondent that is not represented
        unrepresented = 'Pet'
        if 'Res' not in d.values():
            unrepresented = 'Res'
        ## This will change any lawyer not the 'Pet' or 'Res' (whichever one was found) into the unrepresented side
        for lawyer in d:
            if d[lawyer] not in ['Pet','Res']:
                d[lawyer] = unrepresented
        for x in d: print(x, d[x])
    
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


def get_argument_portion(text):
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
    return text[start:end]


def count_cutoffs_and_words(text, sides): 
    ''' This function parses the oral arguments. It identifies when someone has been cut off (-,--)
        and counts both the number of these occurrences and the words spoken before another speaker begins,
        whether they stopped talking due to interruption or not.
        The function takes the oral transcript text as input and returns 2 dictionaries:
        - one with key last name and value the number of times they were cut off
        - one with key last name and value a list of the number of words spoken before stopping talking.
    '''   
    ## get just the argument portion of the text
    arg_text = get_argument_portion(text)
    
    ## A dictionary to store the word counts for each speaking turn for all speakers
    cutoffs = {}
    words = {}
    phrases = {}
    justice_questions = {}
    	
    ## Initialize some variables
    word_count = 0
    cur_phrase = ''
    speaker = ''
    arguing_side = 'Pet'
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
                if 'JUSTICE' not in potential_speaker:
                    potential_speaker = potential_speaker.split()[-1]
            ## If everything preceding a colon is all uppercase, we have a new speaker
            if potential_speaker.isupper():
                #print('potential speaker:', potential_speaker)	
                ## score the last entry if necessary
                if speaker != '' and potential_speaker != speaker:
                    ## Check to see if we have changed argumentation sides
                    if potential_speaker in sides:
                        if sides[potential_speaker] != arguing_side:
                            arguing_side = sides[potential_speaker]
                            #print(speaker, potential_speaker, arguing_side)
                    ## If a new speaker, initialize containers
                    if speaker not in words:
                        words[speaker] = {}
                        phrases[speaker] = []
                        cutoffs[speaker] = {}
                    #print('old speaker:', speaker) 	
                    ## Add the speech to the right asker
                    if speaker not in justice_questions:
                        justice_questions[speaker] = {'Pet':'','Res':''}
                    if arguing_side in ['Pet','Res']:
                        justice_questions[speaker][arguing_side] += ' ' + cur_phrase                    
                    ## Process the data for the speaker	who just stopped talking
                    if potential_speaker not in words[speaker]:
                        words[speaker][potential_speaker] = 0
                    words[speaker][potential_speaker] += word_count
                    phrases[speaker].append(word_count)
                    if prev_line_last_word[-1] == '-':
                        if potential_speaker not in cutoffs[speaker]:
                            cutoffs[speaker][potential_speaker] = 0
                        cutoffs[speaker][potential_speaker] += 1
                    
				## reset the word count
                word_count = 0	
                cur_phrase = ''
				## update the speaker
                speaker = potential_speaker
				## Add the rest of this line to the word count
                if len(split_colon[1]) > 0:
                    word_count += count_words(split_colon[1])
                    cur_phrase += ' ' + split_colon[1]
			## if whatever precedes a maybe-existent colon is not all uppercase, it is speech. Add it to the running total.
            else:
                word_count += count_words(line)
                cur_phrase += ' ' + line
        else:
            word_count += count_words(line)
            cur_phrase += ' ' + line
        ## store the last word of this line. If the next line is a new speaker, we will use it to see if this speaker was interrupted.
        prev_line_last_word = line.split()[-1]
        #print(prev_line_last_word)
        
        ## Clarence Thomas speaks?
        #if speaker == 'THOMAS': print('*'*30, line)
        
#     for i in words:
#         print(i)
#         for j in words[i]:
#             print('\t', j, words[i][j])

    return cutoffs, phrases, words, justice_questions




def purge_dir(dir):
    for file in os.listdir(dir):
    	os.remove(os.path.join(dir, file))


def main():

    ## Define the years we want to analyze
    first_year = '2005'
    last_year = '2014'
    
    outfile_id = ''

    ## Get the main directory in which each years' cases are stored
    main_path = '/Users/nasrallah/Desktop/Insight/courtcast/data/transcripts/'  
    
    ## Define a container for the combination of most-interrupted and most-lawyers
    factors = {}
    ## Define a dictionary for all cases properties. Key is the docket, Values will be other dictionaries.
    case_features = {}
    ## Define a dictionary for the speech for each case. Key is docket. Value is dictionary of {speaker:{side:speech}}
    all_speech = {}
    scdb_file = '/Users/nasrallah/Desktop/Insight/courtcast/data/SCDB/SCDB_2014_01_justiceCentered_Citation_tab.txt'
    case_info = get_SCDB_info(scdb_file)
    new_case_file = '/Users/nasrallah/Desktop/Insight/courtcast/data/new_cases.txt'
    case_info = append_new_case_info(new_case_file, case_info)
    winner_dict = get_docket_winners(case_info)

    
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
            with open(file, 'rU') as f:
                text = f.read()
            
            ## Change all pesky 'McGREGOR' 'McCONNELL and DiNARDO to all caps
            text = re.sub(r'[DM][aci]c*[A-Z]+', lambda pat: pat.group().upper(), text)
#            test = re.sub(r'M R', r'MR', text)
            
            ## Find the docket number from the text file to look up the votes in the SCDB using the 'docket' column
            docket = find_docket_number(text)
            #print('\ndocket:',docket)
            if docket in case_features:
                print(docket,'appears multiple times')
                #continue   ## The second one encountered is likely a re-argument, and is probably the more useful one to examine, so let's replace the first one.
            
            ## Ensure the case is found in the SCDB. If not, skip it.
            if docket not in winner_dict:
                print(docket, 'not found in winner_dict', '*'*30)
                continue
                        
            ## Get from the text which lawyer supported which side (petitioner/respondent)
            sides = get_petitioners_and_respondents_speakers(text)
            #for x in sides: print(x, sides[x])

            ## Is the winning side the Petitioner or Respondent?
            winning_side = winner_dict[docket] 
                             
            #if winning_side not in ['Pet', 'Res']:
            #    print('hmm. neither the petitioner nor repondent won?')
            
#             ## Convert petitioner/respondent into winner/loser for this case.
#             outcomes = get_winning_lawyers(sides, winning_side)
             
            ## Analyze the oral argument text for the number of cutoffs and the sentence length distributions
            cutoffs, ind_phrases, words, justice_questions = count_cutoffs_and_words(text, sides)
            
            ## Print some stuff about this case
            #print('\ndocket:',docket)
            #for x in sides: print(x, sides[x], cutoffs[x]) 
            #for x in outcomes: print(x, outcomes[x]) 
            #for c in cutoffs: print('\t', c, cutoffs[c])
            #for w in ind_phrases: print(w, sum(ind_phrases[w]))
            #for w in words: print(w, words[w])
            #for j in justice_questions:
            #    for s in ['Pet','Res']:
            #        #print(j, s, justice_questions[j][s])
            #        print(j, s)
            
            ## For each speaker, if that speaker is not a lawyer, sum across all lawyers on each side the words spoken to them.
            words_to_sides = {}                    
            for j in words:
                if j not in sides:
                    words_to_sides[j] = {'Pet':0.0,'Res':0.0}
                    for lawyer in sides:
                        if lawyer in words[j]:
                            if sides[lawyer] in ['Pet','Res']:
                                words_to_sides[j][sides[lawyer]] += words[j][lawyer]
            ## Convert to a DataFrame and calculate normalized word score
            words_to_sides = pd.DataFrame.from_dict(words_to_sides, orient='index')
            words_to_sides['score'] = (words_to_sides.Res - words_to_sides.Pet) / (words_to_sides.Res + words_to_sides.Pet)
            words_to_sides.replace(to_replace=float('inf'),value=0.0, inplace=True)
            words_to_sides.replace(to_replace=float('nan'),value=0.0, inplace=True)
            #print(words_to_sides)

            cutoffs_to_sides = {}                    
            for lawyer in cutoffs:
                if lawyer in sides:
                    this_side = sides[lawyer]
                    if this_side in ['Pet','Res']:
                        if this_side not in cutoffs_to_sides:
                            cutoffs_to_sides[this_side] = {}
                        for justice in cutoffs[lawyer]:
                            if justice not in cutoffs_to_sides[this_side]:
                                cutoffs_to_sides[this_side][justice] = 0.0
                            cutoffs_to_sides[this_side][justice] += cutoffs[lawyer][justice]
            ## Convert to a DataFrame and calculate normalized word score
            cutoffs_to_sides = pd.DataFrame.from_dict(cutoffs_to_sides, orient='columns')
            cutoffs_to_sides.replace(to_replace=float('NaN'),value=0.0, inplace=True)       
            cutoffs_to_sides['score'] = (cutoffs_to_sides.Res - cutoffs_to_sides.Pet) / (cutoffs_to_sides.Res + cutoffs_to_sides.Pet)
            cutoffs_to_sides.replace(to_replace=float('inf'),value=0.0, inplace=True)
            #print(cutoffs_to_sides)
                        
            ## Get total interruptions of either side
            side_cuts = cutoffs_to_sides[['Pet','Res']].apply(sum, axis=0)
            #print(side_cuts)

            ## Get the difference in cutoffs between the two sides. Also a binary indicating which side was most interrupted.
            side_cuts_diff = side_cuts.Res - side_cuts.Pet
            int_side = 1 if side_cuts_diff < 0 else 0
            
            #print('winner:', winning_side)
            #### Assumes there is a singular maximum. 08-205 reargued was a tie. 
            
            ## If the the most interrupted person is on the losing side, call that right. Else wrong.
            #print(docket, cutoffs)
#             most_interrupted = max(cutoffs.iteritems(), key=operator.itemgetter(1))[0]
#             #print('most interrupted:', most_interrupted)
#             if most_interrupted not in outcomes:
#                 print(docket, 'most_interrupted', most_interrupted, outcomes[most_interrupted])       

            ## See if there were more lawyers on winning/losing side
            num_pet = sides.values().count('Pet')
            num_res = sides.values().count('Res')
            ## Create variable -1/0/1 for Pet/None/Res.  
            amicus_side = -1 if num_pet > num_res else 1 if num_pet < num_res else 0


            
            if docket not in case_features:
                case_features[docket] = {}
                case_features[docket]['amicus'] = amicus_side 
                case_features[docket]['cutoffs_ALL'] = side_cuts_diff
                ## convert winning_side into 0/1
                if winning_side == 'Pet':
                    win = 1
                elif winning_side == 'Res':
                    win = 0
                else:
                    win = 'NaN'
                case_features[docket]['winner'] = win
                #for j in words_to_sides.index.values:
                for j in ['JUSTICE BREYER', 'JUSTICE GINSBURG', 'JUSTICE KENNEDY', 'CHIEF JUSTICE ROBERTS', 'JUSTICE SCALIA']:
                    case_features[docket]['words_%s' % j.split()[-1]] = words_to_sides.score[j] if j in words_to_sides.index.values else 0
                    case_features[docket]['cutoffs_%s' % j.split()[-1]] = cutoffs_to_sides.score[j] if j in cutoffs_to_sides.index.values else 0
            ## Add the dictionary of speech to the 
            if docket not in all_speech:
                all_speech[docket] = dict.copy(justice_questions)


    ## Convert the case_features into a DataFrame and join with the info from SCDB
    case_features = pd.DataFrame.from_dict(case_features, orient='index')
    case_features = case_features.join(case_info,how='inner')
    print(case_features)
    case_features.drop('partyWinning', axis=1, inplace=True)
    case_features.sort(axis=1, inplace=True)
    #print(case_features)
 

    feature_outfile = '/Users/nasrallah/Desktop/Insight/courtcast/db/feature_table' + outfile_id + '.txt'
    case_features.to_csv(feature_outfile, sep='\t')

    ## directory to write question files
    q_dir = '/Users/nasrallah/Desktop/Insight/courtcast/db/questions/'
    ## Purge the directory of question files from previous runs
    purge_dir(q_dir)
    
    ## Output the justice speech to different files
    for j in ['JUSTICE BREYER', 'JUSTICE GINSBURG', 'JUSTICE KENNEDY', 'CHIEF JUSTICE ROBERTS', 'JUSTICE SCALIA']:
        for s in ['Pet','Res']:
            ## Let the Petitioner file be 0 and Respondent file be 1 (alphabetically)
            num = '0' if s == 'Pet' else '1'
            speech_file = q_dir + 'questions_' + j.split()[-1] + '_' + num + '.txt'  
            with open(speech_file, 'a') as f:
                for docket in case_features.index:    ## for ordering correctly
                    #print(j,s)
                    if j in all_speech[docket] and s in all_speech[docket][j]:
                        f.write(docket + ' +++$+++ ' + all_speech[docket][j][s] + '\n')            
                    else:
                        f.write(docket + ' +++$+++ ' + ' ' + '\n')


if __name__ == '__main__':
    main()
