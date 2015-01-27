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
    for line in f:
        sl = line.split('\t')
        docket = sl[dcol]
        caseName = sl[ncol]
        winner = 'Pet' if sl[wcol] == '1' else 'Res'
        majority_votes = sl[majcol]
        minority_votes = sl[mincol]
        if docket not in d:
            d[docket] = {}
            d[docket]['caseName'] = caseName
            d[docket]['partyWinning'] = winner
            d[docket]['majVotes'] = majority_votes
            d[docket]['minVotes'] = minority_votes                   
    f.close()
    return pd.DataFrame.from_dict(d,orient='index')


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
#         unrepresented = 'Pet'
#         if 'Res' not in d.values():
#             unrepresented = 'Res'
#         ## This will change any lawyer not the 'Pet' or 'Res' (whichever one was found) into the unrepresented side
#         for lawyer in d:
#             if d[lawyer] not in ['Pet','Res']:
#                 d[lawyer] = unrepresented
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


def count_cutoffs_and_words(text): 
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
                if speaker != '' and potential_speaker != speaker:
                    ## If a new speaker, initialize containers
                    if speaker not in words:
                        words[speaker] = {}
                        phrases[speaker] = []
                        cutoffs[speaker] = 0
                    #print('old speaker:', speaker) 	
                    ## Process the data for the speaker	who just stopped talking
                    if potential_speaker not in words[speaker]:
                        words[speaker][potential_speaker] = 0
                    words[speaker][potential_speaker] += word_count
                    phrases[speaker].append(word_count)
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
        
#     for i in words:
#         print(i)
#         for j in words[i]:
#             print('\t', j, words[i][j])

    return cutoffs, phrases, words



def main():

    ## Define the years we want to analyze
    first_year = '2005'
    last_year = '2013'

    ## Get the main directory in which each years' cases are stored
    main_path = '/Users/nasrallah/Desktop/Insight/scotus_predict/data/transcripts/'  
    
    ## Define a container for the combination of most-interrupted and most-lawyers
    factors = {}
    ## Define a dictionary for all cases properties. Key is the docket, Values will be other dictionaries.
    case_features = {}
    scdb_file = '/Users/nasrallah/Desktop/Insight/scotus_predict/data/SCDB/SCDB_2014_01_justiceCentered_Citation_tab.txt'
    case_info = get_SCDB_info(scdb_file)
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
            with open(file, 'rU') as f:
                text = f.read()
            
            ## Change all pesky 'McGREGOR' 'McCONNELL and DiNARDO to all caps
            text = re.sub(r'[DM][aci]c*[A-Z]+', lambda pat: pat.group().upper(), text)
            
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
                             
            if winning_side not in ['Pet', 'Res']:
                print('hmm. neither the petitioner nor repondent won?')
            
            ## Convert petitioner/respondent into winner/loser for this case.
            outcomes = get_winning_lawyers(sides, winning_side)
             
            ## Analyze the oral argument text for the number of cutoffs and the sentence length distributions
            cutoffs, ind_phrases, words = count_cutoffs_and_words(text)
            
            ## Print some stuff about this case
            #print('\ndocket:',docket)
            #for x in sides: print(x, sides[x], cutoffs[x]) 
            #for x in outcomes: print(x, outcomes[x]) 
            #for c in cutoffs: print('\t', c, cutoffs[c])
            #for w in ind_phrases: print(w, sum(ind_phrases[w]))
            #for w in words: print(w, words[w])

            ## For each speaker, if that speaker is not a lawyer, sum across al lawyers on each side the words spoken to them.
            words_to_sides = {}                    
            for j in words:
                if j not in sides:
                    words_to_sides[j] = {'Pet':0,'Res':0}
                    for lawyer in sides:
                        if lawyer in words[j]:
                            if sides[lawyer] in ['Pet','Res']:
                                words_to_sides[j][sides[lawyer]] += words[j][lawyer]
            ## Convert to a DataFrame and calculate normalized word score
            words_to_sides = pd.DataFrame.from_dict(words_to_sides, orient='index')
            words_to_sides['score'] = (words_to_sides.Res - words_to_sides.Pet) / (words_to_sides.Res + words_to_sides.Pet)
            words_to_sides.replace(to_replace=float('inf'),value=0.0, inplace=True)
            #print(words_to_sides)
            
            ## Create dictionary keyed by side with value the total interruptions of all lawyers on that side
            side_cuts = {}
            for v in sides.values():
                side_cuts[v] = 0
            for x in sides:
                if x in cutoffs:
                    side_cuts[sides[x]] += cutoffs[x]
            #for x in side_cuts: print(x, side_cuts[x])
            #print('winner:', winning_side)
            #### Assumes there is a singular maximum. 08-205 reargued was a tie. 
            
            ## Classify interrupted side as 'Pet' (1) or 'Res' (-1). If tied, call it 'Res' (-1)
            #print(side_cuts)
            int_side = 1 if side_cuts['Pet'] > side_cuts['Res'] else -1
            
            ## If the the most interrupted person is on the losing side, call that right. Else wrong.
            #print(docket, cutoffs)
            most_interrupted = max(cutoffs.iteritems(), key=operator.itemgetter(1))[0]
            #print('most interrupted:', most_interrupted)
            if most_interrupted not in outcomes:
                print(docket, 'most_interrupted', most_interrupted, outcomes[most_interrupted])       

            ## See if there were more lawyers on winning/losing side
            num_pet = sides.values().count('Pet')
            num_res = sides.values().count('Res')
            ## Create variable -1/0/1 for Res/None/Pet
            amicus_side = 0
            if num_pet > num_res:
                amicus_side = 1
            elif num_pet < num_res:
                amicus_side = -1          
            
            feature_key = (winning_side, amicus_side, int_side)
            #cases[docket] = feature_key
            if feature_key not in factors:
                factors[feature_key] = 0
            factors[feature_key] += 1

            #print(docket, feature_key)
            
            if docket not in case_features:
                case_features[docket] = {}
                case_features[docket]['amicus'] = amicus_side 
                case_features[docket]['interrupted'] = int_side
                #case_features[docket]['feature_key'] = feature_key
                ## convert winning_side into 0/1
                case_features[docket]['winner'] = 1 if winning_side == 'Pet' else 0
#                for j in words_to_sides.index.values:
                for j in ['BREYER', 'GINSBURG', 'KENNEDY', 'ROBERTS', 'SCALIA']:
                    case_features[docket]['words_%s' % j] = words_to_sides.score[j] if j in words_to_sides.index.values else 0
    
    for f in factors:
        print(f,factors[f])
    
    ## Define a few lists of labels for the different features
    amicus_labels = [1,0,-1]
    interrupt_labels = [-1, 1]
    
    print('\nResults:\n', '_'*30)
    print('(winning_side, amicus_side, most_interrupted_side)') 
    for h in ['Pet', 'Res']:
        for i in amicus_labels:
            for j in interrupt_labels:
                    t = (h,i,j)
                    if t in factors:
                        print(t, factors[t])
                    else:
                        print(t, '?')
        print()

    p = np.empty(0)
    for i in amicus_labels:
        for j in interrupt_labels:
            t = ('Pet',i,j)
            if t in factors:
                p = np.append(p,factors[t])
            else:
                p = np.append(p,0)
    
    r = np.empty(0)
    for i in amicus_labels:
        for j in interrupt_labels:
            t = ('Res',i,j)
            if t in factors:
                r = np.append(r,factors[t])
            else:
                r = np.append(r,0)
 
    ## Number of petitioner wins,respondent wins, and total cases for each feature combination
    print('N(w,cond):', p)
    print('N(l,cond):', r)
    print('N(cond)', p+r)
    print()
    ## Number of correct guesses for each feature combination
    N_correct = [max(p[i],r[i]) for i in range(len(p))]
    print('N(correct|cond)', N_correct)
    print('P(correct|cond)', N_correct/(p+r))
    print()
    ## Marginal probability the petitioner wins
    P_correct = sum(N_correct) / (sum(p) + sum(r))
    print('Marginal P(correct) = ', P_correct)
    print()
    ## Probability the petitioner wins given features
    P_pet_wins = pd.DataFrame(np.reshape(p/(p+r), (3,2)), index = amicus_labels, columns = interrupt_labels)
    print('P(Pet wins|cond):')
    print(P_pet_wins)
    
    ## For each case and its features, get the prob the Pet wins, make a prediction, and see if it is right. Store these.
    for docket in case_features:
        amicus = case_features[docket]['amicus']
        inter = case_features[docket]['interrupted']
        #print(docket, amicus, inter)
        ## get the prob the petitioner wins given these features. Note DataFrames typically index by column then row. .loc switches this.
#         prob = P_pet_wins.loc[amicus, inter]
#         ## get my prediction of who would have won (if > or < 0.5)
#         prediction = 1 if prob > 0.5 else -1
#         ## Am I correct?
#         correct = 1 if prediction == case_features[docket]['winner'] else 0
#         ## Add these things to the case_features dictionary
#         case_features[docket]['toy_prediction'] = prediction
#         case_features[docket]['toy_confidence'] = prob
#         case_features[docket]['toy_correct'] = correct

 
    ## Convert the case_features into a DataFrame and join with the info from SCDB
    case_features = pd.DataFrame.from_dict(case_features, orient='index')
    case_features = case_features.join(case_info,how='inner')
    case_features.drop('partyWinning', axis=1, inplace=True)
    case_features.sort(axis=1, inplace=True)
    #print(case_features)
 
#    print('p(correct) = ', case_features.toy_correct.mean() )

    outfile = '/Users/nasrallah/Desktop/Insight/scotus_predict/db/feature_table.txt'
    case_features.to_csv(outfile, sep='\t')



if __name__ == '__main__':
    main()
