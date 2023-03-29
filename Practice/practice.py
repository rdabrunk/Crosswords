import pandas as pd
import random
from gpt_integration import generate_description

if __name__ == '__main__':
    print("\nWelcome to the Crossword Clue Practice Program!")
    print("Type 'q' at any time to quit.")
    print("Type 'h' at any time to recieve a hint.")
    print("-" * 50)


    # initialize file paths and data frames
    file_path = "Clues/clues.csv"
    accuracy_path = "Clues/accuracies.csv"
    clues = pd.read_csv(file_path)

    # read the accuracies.csv file into a data frame
    accuracies = pd.read_csv(accuracy_path)

    # update any new answers to the accuracies.csv file
    for answer in clues['Answer']:
        if answer not in accuracies['Answer'].values:
            new_row = pd.DataFrame([[answer, 0, 0, 0.0]], columns=accuracies.columns)
            accuracies = pd.concat([accuracies, new_row], ignore_index=True)
            accuracies.to_csv(accuracy_path, index=False)

    # generate descriptions for any new answers
    pos = 0
    num_descriptions_added = 0
    entries_added = []
    print("Checking for new entries...")
    for description in clues['Description']:
        if type(description) == float:
            clue = clues.iloc[pos]['Clue']
            answer = clues.iloc[pos]['Answer']
            # print(clue)
            # print(answer)
            description = generate_description(clue, answer)
            # print(description)
            clues.loc[pos, 'Description'] = description
            clues.to_csv(file_path, index=False)
            entries_added.append([answer, clue, description])
            num_descriptions_added += 1
        pos += 1

    # print the number of new descriptions added and their answers, clues, and descriptions
    if num_descriptions_added > 0:
        print(f"{num_descriptions_added} new description(s) added!\n")
        for entry in entries_added:
            print(f"Answer: {entry[0]}")
            print(f"Clue: {entry[1]}")
            print(f"Description: {entry[2]}\n")
    else:
        print("No new descriptions added.")
    print("-" * 50)
    print("Let's practice!\n")

    answer = input("Would you like to use any filters? (a)ccuracy, (n)umber of attempts, or (t)raining mode? (y/n)\n")

    # set any desired filters
    filter_by_attempts = [False, 3]
    filter_by_accuracy = [False, 0.4]
    training_mode = [False, 15, 0.9]

    if answer == "y":
        answer = input("Which filter would you like to use? (a,n,t)\n")
        if answer == "a":
            filter_by_accuracy[0] = True
            filter_by_attempts[0] = False
            training_mode[0] = False
            filter_by_accuracy[1] = float(input("What accuracy would you like to filter by? (0.0-1.0)\n"))
        elif answer == "n":
            filter_by_attempts[0] = True
            filter_by_accuracy[0] = True
            training_mode[0] = False
            filter_by_attempts[1] = int(input("What number of attempts would you like to filter by?\n"))
        elif answer == "t":
            training_mode[0] = True
            filter_by_attempts[0] = False
            filter_by_accuracy[0] = False

    print("Let's practice!\n")
    while answer != "q":

        if filter_by_attempts[0]:
            # get each answer that has been attempted less than sortbyattempts[1] times
            filtered_clues = accuracies[accuracies['Attempts'] < filter_by_attempts[1]]
            if len(filtered_clues) == 0:
                print("No more answers to practice!")
                break
            # select a random answer from the filtered_clues data frame
            correct_answer = filtered_clues.iloc[random.randint(0, len(filtered_clues) - 1), 0]
            # get the corresponding clue of the answer in the clues data frame, and the location
            clue_index = clues[clues['Answer'] == correct_answer].index[0]
            clue = clues.iloc[clue_index, 1]
            location = clues[clues['Answer'] == correct_answer].index[0]
            print(f'Attempts for this answer: {accuracies.iloc[location, 1]}\n')

        elif filter_by_accuracy[0]:
            # get each answer that has an accuracy less than filterbyaccuracy[1]
            filtered_clues = accuracies[accuracies['Accuracy'] < filter_by_accuracy[1]]
            if len(filtered_clues) == 0:
                print("You've answered all the clues accurately! Try again later.")
                break
            # select a random answer from the filtered_clues data frame
            correct_answer = filtered_clues.iloc[random.randint(0, len(filtered_clues) - 1), 0]
            # get the corresponding clue of the answer in the clues data frame, and the location
            clue_index = clues[clues['Answer'] == correct_answer].index[0]
            clue = clues.iloc[clue_index, 1]
            location = clues[clues['Answer'] == correct_answer].index[0]
            print(f'Accuracy for this answer: {accuracies.iloc[location, 3]:.2f}\n')


        elif training_mode[0]:
            # get each answer that has an accuracy less than training_mode[2] or has been attempted less than training_mode[1] times
            filtered_clues = accuracies[
                (accuracies['Accuracy'] < training_mode[2]) | (accuracies['Attempts'] < training_mode[1])]
            if len(filtered_clues) == 0:
                print("All answers have been trained completely, Try again later.")
                break
            # select a random answer from the filtered_clues data frame
            correct_answer = filtered_clues.iloc[random.randint(0, len(filtered_clues) - 1), 0]
            # get the corresponding clue of the answer in the clues data frame, and the location
            clue_index = clues[clues['Answer'] == correct_answer].index[0]
            clue = clues.iloc[clue_index, 1]
            location = clues[clues['Answer'] == correct_answer].index[0]
            # print the current number of attempts and accuracy of the answer, and format the accuracy to 2 decimal places
            print(f'Attempts for this answer: {accuracies.iloc[location, 1]}')
            print(f'Accuracy for this answer: {accuracies.iloc[location, 3]:.2f}\n')



        else:
            # select a random clue from the second column and determine the correct answer
            location = random.randint(0, len(clues) - 1)
            clue = clues.iloc[location, 1]
            correct_answer = clues.iloc[location, 0]

        # get the corresponding values of the correct answer in the accuracies data frame
        index = accuracies[accuracies['Answer'] == correct_answer].index[0]

        print(f'Clue: {clue} ({len(correct_answer.strip())})\n')
        answer = input("Enter your answer: ")

        # check if the answer is correct, or if the user needs a hint
        i = 1
        hint_text = ""
        while answer.lower().strip() == "h":
            hint_text += correct_answer.strip()[i - 1]
            print(f"Hint: {hint_text}{'_' * (len(correct_answer.strip()) - i)}\n")
            i += 1
            accuracies.iloc[index, 1] += .25
            answer = input("Enter your answer: ")

        if answer.lower().strip() == correct_answer.lower():
            print("Correct!\n")

            # print the description of the answer, which is the third column
            print(f'Description: {clues.iloc[location, 2].capitalize()}')

            # update the accuracies data frame
            accuracies.iloc[index, 1] += 1
            accuracies.iloc[index, 2] += 1
            accuracies.iloc[index, 3] = accuracies.iloc[index, 2] / accuracies.iloc[index, 1]
            accuracies.to_csv(accuracy_path, index=False)

            print("-" * 165)


        elif answer == "q":
            break
        else:
            print(f'Incorrect! The correct answer is {clues.iloc[location, 0]}.\n')
            print()
            print(f'Description: {clues.iloc[location, 2]}')

            accuracies.iloc[index, 1] += 1
            accuracies.iloc[index, 3] = accuracies.iloc[index, 2] / accuracies.iloc[index, 1]
            print("-" * 165)
