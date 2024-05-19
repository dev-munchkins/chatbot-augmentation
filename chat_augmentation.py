import nltk
from nltk.corpus import wordnet
import random
from deep_translator import GoogleTranslator # API for back translation
import pandas as pd
import argparse
import pickle
import time

# nltk.download('wordnet')
# 0. Load Korean Wordnet
wordnet = {}
with open("wordnet.pickle", "rb") as f:
	wordnet = pickle.load(f)
     
# 1. Synonym Replacement
def synonym_replacement(text, n):
    words = text.split()
    new_words = words.copy()
    random_word_list = list(set([word for word in words]))
    random.shuffle(random_word_list)

    num_replaced = 0
    for random_word in random_word_list:
        synonyms = get_synonyms(random_word)
        if synonyms:
            synonym = random.choice(list(synonyms))
            new_words = [synonym if word == random_word else word for word in new_words]
            num_replaced += 1
        if num_replaced >= n:
            break
    return ' '.join(new_words)

def get_synonyms(word):
	synomyms = []     
	try:
		for syn in wordnet[word]:
			for s in syn:
				synomyms.append(s)
	except:
		pass
	return synomyms

# 2. Random Insertion
def random_insertion(text, n):
    words = text.split()
    for _ in range(n):
        add_word = random.choice(words)
        random_idx = random.randint(0, len(words))
        words.insert(random_idx, add_word)
    return ' '.join(words)


# 3. Random Swap
def random_swap(text, n):
    words = text.split()
    for _ in range(n):
        idx1, idx2 = random.sample(range(len(words)), 2)
        words[idx1], words[idx2] = words[idx2], words[idx1]
    return ' '.join(words)
    
# 4. Back Translation
def back_translation(text, label):
    translated_list = []
    lang_list = ['en', 'es', 'fr', 'it', 'ja', 'pl', 'ro', 'tr', 'zh-CN', 'sv']
    for i in range(len(lang_list)):
        try:
            translated = GoogleTranslator(source='ko', target=lang_list[i]).translate(text)
            back_translated = GoogleTranslator(source=lang_list[i], target='ko').translate(translated)
            translated_list.append([back_translated, label])
        except:
            time.sleep(2)
            translated = GoogleTranslator(source='ko', target=lang_list[i]).translate(text)
            back_translated = GoogleTranslator(source=lang_list[i], target='ko').translate(translated)
            translated_list.append([back_translated, label])
    return translated_list

if __name__ == '__main__':
    merge_list = []

    parser = argparse.ArgumentParser()
    parser.add_argument('--base_path', type=str, help='path for base_text file')
    parser.add_argument('--save_path', type=str, help='path for augmentated text file')
    parser.add_argument('--n_iters', type=int, default=3, help='number of augmentation iterations')
    parser.add_argument('--syn_replace_num', type=int, default=2, help='number of synonym replacement operations')
    parser.add_argument('--rand_ins_num', type=int, default=2, help='number of random insertion operations')
    parser.add_argument('--rand_swap_num', type=int, default=2, help='number of synonym replacement operations')

    args = parser.parse_args()
    base_text = pd.read_excel(args.base_path)

    for i in range(len(base_text)):
        input_string = base_text['text'][i]
        input_label = base_text['label'][i]
        print(f'=====================Augmentation for {i+1}th text data===========================')
        print('input string: ', input_string)
        print('input label:', input_label)
        print('Starting augmentation..')
        print('example augmentated data)')
        for i in range(args.n_iters):
            aug1 = synonym_replacement(input_string, args.syn_replace_num)
            aug2 = random_insertion(input_string, args.rand_ins_num)
            aug3 = random_swap(input_string, args.rand_swap_num)
            aug4 = back_translation(input_string, input_label)

            merge_list.append([aug1, input_label])
            merge_list.append([aug2, input_label])
            merge_list.append([aug3, input_label])
            merge_list += aug4
            # print(f"{i+1}th iteration completed...")
            print('[example 1]', aug1)
            print('[example 2]', aug2)
            print('[example 3]', aug3)
        print(f'Augmentation successfully done for {args.n_iters} iterations...')

    print('Merging augmented text into DataFrame...')
    merge_df = pd.DataFrame(merge_list, columns=['text', 'label'])
    merge_df.to_csv(args.save_path)
    print(f'Augmentation Data converted to csv and saved at {args.save_path}')