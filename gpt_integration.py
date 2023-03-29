
import openai

# set up your OpenAI API key
openai.api_key = "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"


def generate_description(clue, answer):
    question = f"In a crossword puzzle, why would {answer} would be clued as \"{clue}\"? Answer confidently in a single paragraph. If you can't determine a reason, just say 'no clue' and don't finish the paragraph."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a chatbot"},
            {"role": "user", "content": question},
        ]
    )
    description = ''
    for choice in response.choices:
        description += choice.message.content
    return description


def generate_answer(clue, length, tries=4):
    candidates = []
    best = ''
    for i in range(tries):
        question = f"""Give your three best guesses to the following clue: \"{clue}\"\n. make sure the answer is {length} letters long."""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a crossword solver, and you are trying to solve a crossword puzzle. You are given a clue, and you must answer it without any punctuation."},
                {"role": "user", "content": question},
            ]
        )
        answer = ''
        for choice in response.choices:
            answer += choice.message.content

        # remove any numbers and punctuation from the answer
        answer = ''.join([c for c in answer if c.isalpha()])
        # seperate the answer into words. Assume that each capitalized letter is the start of a new word
        answer = ''.join([c if c.islower() else ' ' + c for c in answer]).split()
        # check if any of the words are a length of 1
        for i in range(len(answer)):
            if len(answer[i]) == 1:
                new_entry = answer[i]
                if i != len(answer) - 1:
                    while len(answer[i + 1]) == 1:
                        new_entry += answer[i + 1]
                        i += 1
                        if i == len(answer) - 1:
                            break
                if i < len(answer) - 1 and len(answer[i + 1]) > 1 and (not answer[i + 1].isupper()):
                    new_entry += answer[i + 1][0]

                answer.append(new_entry)

        answer.append(answer[0])
        print(answer)

        for candidate in answer:
            if len(candidate) == length:
                candidates.append(candidate)

    # find the most common candidate
    print(candidates)
    # if there are no candidates, return dashes
    if len(candidates) == 0:
        return '-' * length
    else:
        best = max(set(candidates), key=candidates.count)
        return best.upper()


def revise_answer(clue, length, known_info, tries=1):
    candidates = []
    for i in range(tries):
        question = f"""I'm trying to solve the following clue in a crossword puzzle:
"{clue}"
Currently the clue is filled in this far:
{known_info}
give me your best guess for the answer surround by brackets. For example, if the answer is "hello", you would write "[hello]"
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a crossword solver, and you are trying to solve a crossword puzzle. you will be given a clue and information about the answer."},
                {"role": "user", "content": question},
            ]
        )
        answer = ''
        for choice in response.choices:
            answer += choice.message.content
        # find the answer in the response
        # check if the answer is in the response
        if (answer.count('[') != 0) and (answer.count(']') != 0):
            answer = answer[answer.find('[') + 1:answer.find(']')]
        # remove any numbers and punctuation from the answer
        answer = ''.join([c for c in answer if c.isalpha()])
        # make sure the answer is the correct length
        if len(answer) == length:
            candidates.append(answer.upper())
            print(candidates)

    # remove any candidate that areen't the correct length
    candidates = [c for c in candidates if len(c) == length]
    # find the best candidate
    if len(candidates) == 0:
        return known_info.replace('_', '-')
    else:
        best = max(set(candidates), key=candidates.count)
    return best


def generate_answer_2(clue, length, tries=1):
    candidates = []
    for i in range(tries):
        question = f"""I'm trying to solve the following clue in a crossword puzzle:
"{clue}"
I know the answer must be {length} letters long.
give me your best three guess for the answer surround by brackets. For example, if an answer is "hello", you would write "[hello]"
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a crossword solver, and you are trying to solve a crossword puzzle. You are given a clue, and you must up with some possible solutions."},
                {"role": "user", "content": question},
            ]
        )
        answer = ''
        for choice in response.choices:
            answer += choice.message.content

        is_first = True
        while (answer.count('[') != 0) and (answer.count(']') != 0):
            # find the next answer in the response by finding the first bracket and the first closing bracket
            candidate = answer[answer.find('[') + 1:answer.find(']')]
            if len(candidate) == length:
                # remove any numbers and punctuation from the answer
                candidate = ''.join([c for c in candidate if c.isalpha()])
                candidates.append(candidate.upper())
                print(candidates)
                # if this is the first guess from the answer, add the candidate again
                if is_first:
                    candidates.append(candidate.upper())
                    is_first = False
            # remove the answer from the response
            answer = answer[answer.find(']') + 1:]

    # remove all candidates that either are not the correct length or are spaces
    candidates = [c for c in candidates if (len(c) == length) and (c != '')]
    # if the list of candidates is empty, return dashes
    if len(candidates) == 0:
        return '-' * length

    # find the best candidate
    best = max(set(candidates), key=candidates.count)
    return best


def generate_answer_3(clue, length, tries=1):
    candidates = []
    for i in range(tries):
        question = f"""I'm trying to solve the following clue in a crossword puzzle:
        "{clue}"
        I know the answer must be {length} letters long.
        give me your best guess for the answer surround by brackets. For example, if the answer is "hello", you would write "[hello]"
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                    "content": "You are a crossword solver, and you are trying to solve a crossword puzzle. You are given a clue, and you must up with a possible solution."},
                {"role": "user", "content": question},
            ]
        )
        answer = ''
        for choice in response.choices:
            answer += choice.message.content

        # check if the answer is in the response
        if (answer.count('[') != 0) and (answer.count(']') != 0):
            answer = answer[answer.find('[') + 1:answer.find(']')]
            # remove any numbers and punctuation from the answer
            answer = ''.join([c for c in answer if c.isalpha()])
            # make sure the answer is the correct length
            if len(answer) == length:
                candidates.append(answer.upper())
                print(candidates)

            # remove any candidate that areen't the correct length
        candidates = [c for c in candidates if len(c) == length]
        # find the best candidate
        if len(candidates) == 0:
            return '-' * length
        else:
            best = max(set(candidates), key=candidates.count)
        return best


if __name__ == '__main__':
    pass
    # response = openai.Image.create(
    #     prompt="jupiter as a person",
    #     n=1,
    #     size="1024x1024"
    # )
    # image_url = response['data'][0]['url']
    # print(image_url)
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are a chatbot"},
    #         {"role": "user", "content": "hello there!"},
    #     ]
    # )
    # description = ''
    # for choice in response.choices:
    #     description += choice.message.content
    # print(description)

    # print(generate_answer("'Bob Hearts Abishola' network", 3))

    # print(revise_answer("Sailboat pole", 4, "M_ST"))
    # print(generate_answer_3("Sailboat pole", 4))
    print(generate_answer_3("'Bob Hearts Abishola' network", 3))
    #
