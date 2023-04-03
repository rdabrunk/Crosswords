import pandas as pd
import tensorflow as tf
from transformers import GPT2Tokenizer, TFGPT2LMHeadModel, AutoTokenizer, TFAutoModelForCausalLM

# # Load the dataset into a pandas DataFrame
# df = pd.read_csv('Solving/Data/train.csv')
# # only keep the first 1000 rows
# df = df[:1000]
#
#
# # Remove the index column
# df.drop(columns=['id'], inplace=True)
#
# # Remove any rows with missing values
# df.dropna(inplace=True)
#
# # Format the data into a list of dictionaries
# data = df.to_dict('records')
#
# # Preview the first 5 records
# print(data[:5])
# print(df.info())
#
# import pandas as pd
# from transformers import pipeline, TextDataset, DataCollatorForLanguageModeling, GPT2LMHeadModel, TrainingArguments, Trainer
#
# # Load the dataset into a pandas DataFrame
# df = pd.read_csv('Solving/Data/train.csv')
# # only keep the first 10000
# df = df[:10000]
#
# # Remove the index column
# df.drop(columns=['id'], inplace=True)
#
# # Remove any rows with missing values
# df.dropna(inplace=True)
#
# # Write the modified DataFrame to a text file
# df.to_csv('crossword_data.csv', header=None, index=None, sep=',', mode='a')

data = pd.read_csv('Solving/crossword_data.csv', encoding='utf-8', names=['clue', 'answer'])

clues = data['clue'].tolist()
answers = data['answer'].tolist()
data.info()

# Initialize the tokenizer
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Set the padding token
tokenizer.padding_side = "left"
tokenizer.pad_token = tokenizer.eos_token

# Tokenize the clues and answers
tokenized_clues = tokenizer(clues, padding=True, truncation=True, return_tensors="tf")
tokenized_answers = tokenizer(answers, padding=True, truncation=True, return_tensors="tf")

# Pad the sequences
max_length = 128
padded_clues = tf.keras.preprocessing.sequence.pad_sequences(tokenized_clues['input_ids'],maxlen=max_length, padding='post')
padded_answers = tf.keras.preprocessing.sequence.pad_sequences(tokenized_answers['input_ids'],maxlen=max_length, padding='post')

# Check the shape of the padded sequences
print(padded_clues.shape)
print(padded_answers.shape)

# Create a TensorFlow dataset
dataset = tf.data.Dataset.from_tensor_slices((padded_clues, padded_answers))

# Load the GPT-2 model
model = TFAutoModelForCausalLM.from_pretrained("gpt2")

# Define the loss function and optimizer
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
optimizer = tf.keras.optimizers.Adam(learning_rate=5e-5)

# Compile the model
model.compile(optimizer=optimizer, loss=[loss_fn, *[None] * model.config.n_layer])

# Fine-tune the model on the dataset
model.fit(dataset.batch(batch_size=16), epochs=2)
