
import os
from utils import gen_word_embeddings


class RatingModel():
    def __init__(self):
        super().__init__()
        self.name = 'RatingModel'
        
        self.MODEL_LOAD = True
        self.MODEL_SAVE_PATH = './model/rating_model.h5'
        self.DATA_PATH = './data/'
        self.SAMPLING = False
        self.DATA_COLUMN = 'sep_line'
        self.LABEL_COLUMN = 'rating'

        self.model = None

    def load(self):
        if self.model is not None:
            return
        
        def build_model():
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, Dropout
            from tensorflow.keras import optimizers
            model = Sequential()
            '''
            model.add(Dense(1024, input_dim=768, activation='relu'))
            model.add(Dense(1024, activation='relu'))
            model.add(Dropout(0.2))
            model.add(Dense(512, activation='relu'))
            model.add(Dropout(0.2))
            model.add(Dense(256, activation='relu'))
            model.add(Dropout(0.2))
            model.add(Dense(128, activation='relu'))
            model.add(Dense(6, activation='softmax'))
            '''
            model.add(Dense(1000, input_dim=768, activation='relu'))
            model.add(Dropout(0.3))
            model.add(Dense(500, activation='relu'))
            model.add(Dropout(0.3))
            model.add(Dense(200, activation='relu'))
            model.add(Dropout(0.3))
            model.add(Dense(100, activation='relu'))
            model.add(Dense(6, activation='softmax'))
            # rmsprop=optimizers.RMSprop(lr=0.001, rho=0.9, epsilon=None, decay=0.0)
            model.compile(loss='categorical_crossentropy',
                          metrics=['accuracy', 'categorical_accuracy'],
                          optimizer='adam')

            return model
        
        if self.MODEL_LOAD and os.path.exists(self.MODEL_SAVE_PATH):
            from tensorflow.keras.models import load_model
            self.model = load_model(self.MODEL_SAVE_PATH)
            print(f'[INFO] Successfully load the model from {self.MODEL_SAVE_PATH}')
        else:
            self.model = build_model()
            print(self.model.summary())


    def save(self):
        if self.MODEL_LOAD:
            self.model.save(self.MODEL_SAVE_PATH)
            print(f'[INFO] Successfully save the model to {self.MODEL_SAVE_PATH}')


    def train(self, train_df, train_word_embeddings=None, epochs=5, batch_size=2048):
        from tensorflow.keras.utils import to_categorical
        import numpy as np

        self.load()

        # import word embeddings if exists
        # this is weird
        
        if train_word_embeddings is None:
            if os.path.exists(os.path.join(self.DATA_PATH, 'train_word_embeddings.npy')):
                train_word_embeddings = np.load(os.path.join(
                    self.DATA_PATH, 'train_word_embeddings.npy'))
            else:
                train_word_embeddings = gen_word_embeddings(train_df[self.DATA_COLUMN])
                '''
                np.save(os.path.join(self.DATA_PATH, 'train_word_embeddings.npy'),
                        train_word_embeddings)
                '''
        
        
        # balance training data
        balanced_train_df, balanced_train_word_embeddings = self.balance_data(
            train_df, train_word_embeddings)
        balanced_train_label_onehot = to_categorical(
            balanced_train_df[self.LABEL_COLUMN])

        # fit
        train_history = self.model.fit(x=balanced_train_word_embeddings,
                                       y=balanced_train_label_onehot,
                                       validation_split=0.2,
                                       epochs=epochs,
                                       batch_size=batch_size,
                                       verbose=1)
        
        # self.save()
        
        
    def get_list_of_predictions(self, test_df):
        import numpy as np
        self.load()

        # import word embeddings if exists
        # this is weird
        if os.path.exists(os.path.join(self.DATA_PATH, 'test_word_embeddings.npy')):
            test_word_embeddings = np.load(os.path.join(
                self.DATA_PATH, 'test_word_embeddings.npy'))
        else:
            test_word_embeddings = gen_word_embeddings(test_df[self.DATA_COLUMN])
            np.save(os.path.join(self.DATA_PATH, 'test_word_embeddings.npy'),
                    test_word_embeddings)

        # Print f1, precision, and recall scores
        predictions = self.model.predict_classes(test_word_embeddings)
        return predictions
    
    
    def evaluate(self, test_df, test_word_embeddings=None):
        import numpy as np
        import pandas as pd

        self.load()

        # import word embeddings if exists
        # this is weird
        if test_word_embeddings is None:
            if os.path.exists(os.path.join(self.DATA_PATH, 'test_word_embeddings.npy')):
                test_word_embeddings = np.load(os.path.join(
                    self.DATA_PATH, 'test_word_embeddings.npy'))
            else:
                test_word_embeddings = gen_word_embeddings(test_df[self.DATA_COLUMN])
                '''
                np.save(os.path.join(self.DATA_PATH, 'test_word_embeddings.npy'),
                        test_word_embeddings)
                '''

        # Print f1, precision, and recall scores
        predictions = self.model.predict_classes(test_word_embeddings)

        from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
        y_test = test_df[self.LABEL_COLUMN]

        p = precision_score(y_test, predictions, average='micro')
        r = recall_score(y_test, predictions, average='micro')
        f = f1_score(y_test, predictions, average='micro')
        
        print(f'[INFO] precision_score={p}')
        print(f'[INFO] recall_score={r}')
        print(f'[INFO] f1_score={f}')
        
        print(f'[INFO] confusion_matrix:')
        print(pd.crosstab(y_test, predictions,
            rownames=['label'], colnames=['predict']))


    def predict_classes(self, text_list):
        self.load()
        word_embeddings = gen_word_embeddings(text_list)
        predictions = self.model.predict_classes(word_embeddings)
        return predictions
    

    def predict_classes_embeddings(self, word_embeddings):
        self.load()
        predictions = self.model.predict_classes(word_embeddings)
        return predictions


    def balance_data(self, df, word_embeddings):
        '''
        balancing different rating
        '''
        from sklearn.utils import shuffle
        import numpy as np

        num_rate = [len(df[self.LABEL_COLUMN][df[self.LABEL_COLUMN] == i])
                    for i in range(1, 6)]
        highest_rate = max(num_rate)

        balanced_df = df.copy()
        balanced_word_embeddings = word_embeddings.copy()
        for i in range(1, 6):
            num_sample = highest_rate - num_rate[i - 1]
            balanced_df = balanced_df.append(
                df[df[self.LABEL_COLUMN] == i].sample(num_sample, replace=True))

        balanced_df = shuffle(balanced_df)

        balanced_word_embeddings = np.array(
            [word_embeddings[i] for i in balanced_df.index])

        return (balanced_df, balanced_word_embeddings)
    
    
    '''def average_star(self, test_df):
        import numpy as np
        self.load()
        if os.path.exists(os.path.join(self.DATA_PATH, 'test_word_embeddings.npy')):
            test_word_embeddings = np.load(os.path.join(
                self.DATA_PATH, 'test_word_embeddings.npy'))
        else:
            test_word_embeddings = gen_word_embeddings(test_df[self.DATA_COLUMN])
            np.save(os.path.join(self.DATA_PATH, 'test_word_embeddings.npy'),
                    test_word_embeddings)

        # Print f1, precision, and recall scores
        predictions = self.model.predict_classes(test_word_embeddings)
        
        print(np.mean(predictions))'''
    
    
    def add_PredictedStar_col(self, df):
        import pandas as pd
        predictions = self.get_list_of_predictions(df)
        df['predicted_star'] = pd.Series(predictions)
        return df
