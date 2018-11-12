def tokenize(doc_path):
  words = []
  with open(doc_path, 'r') as f:
    for line in f:
      for word_tag in line.split():
        words.append(word_tag)
  return words

def tokenize_sentences(doc_path):
  sentences = []
  with open(doc_path, 'r') as f:
    for line in f:
      words = []
      for word_tag in line.split():
        words.append(word_tag)
      sentences.append(words)
  return sentences