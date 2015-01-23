
transcript_file = "greece_mod2.txt"

transcript = open(transcript_file, "r")

speaker = ""

caps = "HELLO WORLD:"
if ":" in caps:
	print "success!"

## what are the data structures i need?
## I will need to keep track of the times people speak and how many words are said each time.
## So I need a dictionary of lists, where the key is the names and the entries of the lists
## are the number of words spoken each time. Perhaps I will have two such dictionaries, one
## for uninterrupted speech, another for interrupted speech?  But I need to know who did the interrupting.
## For that I really need a matrix of people x people where the entries are the counts of interruptions
## such as interruptions['Scalia']['Ginsburg'] would be the number of times she interrupted him.
## This can be a dictionary of dictionaries.

## For uninterrupted speech:
u_speech = {}
## for interrupted speech:
i_speech = {}
## counts of who interrupted whom. The first key is the person interrupted, the second is the interruptor.
interruptions = {}

wasinterrupted = 1


speaker = "CHIEF JUSTICE ROBERTS"
count = 0
for line in transcript:
	split_colon = line.split(':')
	potential_name = split_colon[0]
	
		## Check that the bit preceding the colon (hopefully the name of the speaker) consists
		## of alphabetic characters only (after whitespace is removed), that the letters are all capital,
		## and that something follows the colon (says something hopefully). This is important because a 
		## line ending in a colon in the preamble would otherwise be counted.
	if potential_name.isupper() and potential_name.replace(" ", "").isalpha() and not split_colon[1].isspace():
		## There is a new speaker.
		new_speaker = potential_name.strip()
				

		
		## if the interrupted flag is true (last line ended in '--') then process this as an interruption
		if wasinterrupted:
		
			## if this person has not been interrupted before, create the two dictionaries for them
			if speaker not in i_speech:
				i_speech[speaker] = []
				interruptions[speaker] = {}
				
			## increment the interruptions matrix (dict of dicts)
			## if interruptor is not in the interrupted person's dictionary, add them.
			if new_speaker not in interruptions[speaker]:
				interruptions[speaker][new_speaker] = 0
				
			## add the count to the interrupted speech dictionary
			interruptions[speaker][new_speaker] += 1
			
			## reset interruption flag to false
	#		wasinterrupted = 0	
			## update the speaker
			## reset the word count to the words in this line
		
		
		## if the speaker was not interrupted, process this as a normal speech
		
			## if the speaker is not in the dictionary, add them.
			
			## add the count to the uninterrupted dictionary
		
	## if not a new speaker, but a continuation of previous speaker
	
		## add current words to word count
		## check to see if interrupted at end ('--'). if so, set flag.


		
#		print len(split_colon), potential_name
#	line_words = line.split()
#	print len(splitline), " : ", line 
#	if 
#	print line_words[0].split(':')[0]

	
print interruptions	
print count




## For each line
##	 Check to see if new speaker
##	 If so, store total of words for that speaker, update speaker, and begin new count.
##	 If not, continue counting words for current speaker.
##	 Check to see if speaker is interrupted "(--" end)
## If there was an interruption, I need to record who interrupted whom.



## Maybe look and see how frequently justices address the lawyers as "Ms." and "Mr." versus
## "council." For example, does Ginsburg call people "Ms. " more than Scalia does?