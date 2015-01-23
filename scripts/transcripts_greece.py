from __future__ import division, print_function
import string


def count_words(s):
	s = s.split()
	non_words = ['-','--']
	return sum([x not in non_words for x in s])

def was_cut_off(w):
	if w in ['-','--']:
		return True
	return False


def main():
	## Define file
	transcript_file = "/Users/nasrallah/Desktop/scotus_project/scotus_python/greece_mod.txt"

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
	transcript = open(transcript_file, "r")
	for line in transcript:
		#print(line)
		last_word = line.split()[len(line.split())-1]
		print(last_word)
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
