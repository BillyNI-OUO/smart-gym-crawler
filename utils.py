bc = None

def gen_word_embeddings(text_list):
    '''
    Compute word embedding
    '''
    from bert_serving.client import BertClient
    import numpy as np
    from tqdm import tqdm
    
    global bc
    if bc is None:
        bc = BertClient('localhost', check_length=False)
    
    train_vectors = None
    
    BATCH_SIZE = 256
    rows = len(text_list)
    step = BATCH_SIZE
    for i in tqdm(range(0, rows, step)):
        train_x = text_list[i:i + step]
        vectors = bc.encode(list(train_x))
        if train_vectors is None:
            train_vectors = vectors
        else:
            train_vectors = np.concatenate((train_vectors, vectors), axis=0)
    
    # print(f'Generating {rows} word embeddings.')
    # print('[INFO] Successfully computed all word embeddings.')
    return train_vectors
