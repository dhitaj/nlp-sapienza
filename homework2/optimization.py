__author__ = 'dorjan'

# Use scikit-learn to grid search the batch size and epochs
import numpy
import gensim
from sklearn.grid_search import GridSearchCV
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from keras.layers import LSTM
from keras.utils import np_utils
# Function to create model, required for KerasClassifier


def create_model():
	# create model
	model = Sequential()
	# model.add(Embedding(max_features, 128))
	model.add(LSTM(128, input_shape=(7,300)))
	model.add(Dense(17, activation='softmax'))
	# try using different optimizers and different optimizer configs
	model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
	return model

#the pretrained vord vectors. each word vector is an array of length 300
model = gensim.models.KeyedVectors.load_word2vec_format('/home/dorjan/Downloads/GoogleNews-vectors-negative300.bin', binary=True)
model_unknown = gensim.models.Word2Vec([['UNKNOWN']], min_count=1, size=300)

pos_tags = ['ADJ', 'ADV', 'INTJ', 'NOUN', 'PROPN', 'VERB', 'ADP', 'AUX', 'CONJ','DET', 'NUM', 'PART', 'PRON', 'SCONJ','PUNCT', 'SYM', 'X']
label_to_indices = dict((c,i) for i, c in enumerate(pos_tags))
indices_to_label = dict((i,c) for i,c in enumerate(pos_tags))

dataY = []
filehandle = open('homework_2/data/en-ud-dev.conllu')

sentences = []
single_sentence = []

sentence_count = 0
for line in filehandle:
    if line.startswith('#'):
        sentence_count += 1
        single_sentence = []
        continue
    else:
        if len(line.rstrip()) == 0:
            #append to the big list
            sentences.append(single_sentence)
        else:
            splitted = line.split()
            word = splitted[1]
            # print(word)
            tag = splitted[3]
            dataY.append(label_to_indices[tag])
            single_sentence.append(word)
# else:
#     if len(single_sentence)>0:
#         sentences.append(single_sentence)

y=np_utils.to_categorical(dataY)
print(y.shape, ' <--- the shape of Y vector (num_words, num_classes)')

padding_array = numpy.zeros(300)
window_size = 3
final_array = []
word_context = []
for seq in sentences:
    for i in range(len(seq)):
        word_context = []
        for j in range(window_size):
            #append to the left
            if (i-window_size+j) < 0:
                word_context.append(padding_array)
            else:
                if i-window_size+j>=0:
                    if seq[i-window_size+j] in model:
                        word_context.append(model[seq[i-window_size+j]])
                    else:
                        word_context.append(model_unknown['UNKNOWN'])
        if seq[i] in model:
            word_context.append(model[seq[i]])
        else:
                        word_context.append(model_unknown['UNKNOWN'])

        for j in range(window_size):
            #append to the left
            if (i+j) > len(seq)-1:
                word_context.append(padding_array)
            else:
                if i+j <= len(seq)-1:
                    if seq[i+j] in model:
                        word_context.append(model[seq[i+j]])
                    else:
                        word_context.append(model_unknown['UNKNOWN'])
        # print(len(word_context))
        final_array.append(word_context)

X_train_final_numpy=numpy.array(final_array)

print(X_train_final_numpy.shape, '<--- the shape of x vector')


# fix random seed for reproducibility
seed = 7
numpy.random.seed(seed)

# split into input (X) and output (Y) variables
X = X_train_final_numpy
Y = y
# create model
model = KerasClassifier(build_fn=create_model, verbose=0)
# define the grid search parameters
batch_size = [16, 32, 64, 96, 128]
epochs = [5, 10, 15]
param_grid = dict(batch_size=batch_size, epochs=epochs)
grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1)
grid_result = grid.fit(X, Y)

# summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']

for mean, stdev, param in zip(means, stds, params):
	print("%f (%f) with: %r" % (mean, stdev, param))
