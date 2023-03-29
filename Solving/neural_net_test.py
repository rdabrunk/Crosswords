import pandas as pd
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
import tensorflow as tf
# Set the visible devices to use the CPU
tf.config.set_visible_devices([], 'GPU')


if __name__ == '__main__':
    # Load the training and validation data
    train_data = pd.read_csv('Puzzles/Data/train.csv', encoding='latin-1')
    valid_data = pd.read_csv('Puzzles/Data/valid.csv', encoding='latin-1')
    train_data['answer'] = train_data['answer'].astype(str)
    train_data['clue'] = train_data['clue'].astype(str)
    valid_data['answer'] = valid_data['answer'].astype(str)
    valid_data['clue'] = valid_data['clue'].astype(str)

    # Convert the clues and answers to sequences of word indices
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(train_data['clue'])
    train_clue_seqs = tokenizer.texts_to_sequences(train_data['clue'])
    train_answer_seqs = tokenizer.texts_to_sequences(train_data['answer'])
    valid_clue_seqs = tokenizer.texts_to_sequences(valid_data['clue'])
    valid_answer_seqs = tokenizer.texts_to_sequences(valid_data['answer'])

    # Pad the sequences to a fixed length
    max_clue_len = max(len(seq) for seq in train_clue_seqs)
    max_answer_len = max(len(seq) for seq in train_answer_seqs)
    train_clue_seqs = pad_sequences(train_clue_seqs, maxlen=max_clue_len)
    train_answer_seqs = pad_sequences(train_answer_seqs, maxlen=max_answer_len)
    valid_clue_seqs = pad_sequences(valid_clue_seqs, maxlen=max_clue_len)
    valid_answer_seqs = pad_sequences(valid_answer_seqs, maxlen=max_answer_len)

    # Build the neural network model
    model = Sequential()
    model.add(Embedding(len(tokenizer.word_index) + 1, 128, input_length=max_clue_len))
    model.add(LSTM(128))
    model.add(Dense(max_answer_len, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Train the model
    model.fit(train_clue_seqs, train_answer_seqs, validation_data=(valid_clue_seqs, valid_answer_seqs), epochs=10,
              batch_size=32)

    # Evaluate the model on the validation set
    loss, accuracy = model.evaluate(valid_clue_seqs, valid_answer_seqs, batch_size=32)
    print('Validation loss:', loss)
    print('Validation accuracy:', accuracy)
