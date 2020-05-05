from nltk.corpus import wordnet as wn
import boto3
import string

ACCESS_KEY = "AKIAX2B7KX4ZPKF2GQMO"
SECRET_KEY = "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"
client = boto3.client('lex-models',
                      region_name='us-east-1',
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
values = []
nouns_count = {}
for synset in list(wn.all_synsets('n')):
    lemmas = synset.lemmas()
    # {
    #     'value': 'outdoor',
    #     'synonyms': []
    # }
    for lemma in lemmas:
        value = lemma.name()
        if value.isdigit() or value in string.punctuation:
            continue
        if value not in nouns_count:
            nouns_count[value] = 0
        nouns_count[value] += lemma.count()

nouns = sorted(nouns_count.items(), key = lambda x:x[1], reverse = True)
print("flowers" in nouns)
print(nouns[0])
nouns = nouns[:10000]
with open('lex_init.txt', 'w') as f:
    f.write(str(nouns))
    # break
for n, freq in nouns:
    new_value ={
        'value': n,
        'synonyms': []
    }
    values.append(new_value)
print(len(values))
response = client.put_slot_type(
    name='nouns_for_query',
    description='string',
    enumerationValues= values,
    # checksum='string',
    valueSelectionStrategy= 'TOP_RESOLUTION', #'ORIGINAL_VALUE',
    createVersion=True,

)
print(response)