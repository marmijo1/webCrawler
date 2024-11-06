import sys

#This function is ran based on the characters in the file so it would run once for every character in the text file.
#Runtime complexity: O(a) where a is the number of characters in the file being read.
#This is linear in time complexity since it's going throught the characters one by one. 
def tokenize(content):
    tokens = []

    content = content.lower()
    token = ''
            
    for char in content:
        if ('a'<= char <= 'z' and char.isascii) or char.isdigit():
            token += char 
        else:
            if token:
                tokens.append(token)
                token = ''

    if token:
        tokens.append(token)

   
    return tokens

#The computeWordFrequencies function takes the token list and converts it in a map to assign it's corelating frequency
#Runtime complexity: O(b) where b is the number of tokens in the list being parsed through.
#This function is linear in time complexity since the function is going through the tokens one by one. 
def computeWordFrequencies(tokens):

    frequencyMap = {}

    for token in tokens:
        if token in frequencyMap:
            frequencyMap[token] += 1
        else:
            frequencyMap[token] = 1
    return frequencyMap

#The printResults function takes a sorted map and prints the word along with the frequency of it
#Runtime Complexity: O(c log c) where d is a token on the map
#This function is log-linear in time complexity since the map is sorted.
def printResults(frequencyMap):

    sortedMap = sorted(frequencyMap.items(), key = lambda word: word[1], reverse = True)

    for tuples in sortedMap:
        word, frequency = tuples

        print(f"{word} - {frequency}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please input: python3 PartA.py <text_file_path>")
        sys.exit(1)
    
    filePath = sys.argv[1]
    
    tokens = tokenize(filePath)
    frequencies = computeWordFrequencies(tokens)
    printResults(frequencies) 