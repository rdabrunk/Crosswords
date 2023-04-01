import pandas as pd
import rapidfuzz.fuzz as fuzz
# import every function from puzzle.py
import puz
from timeit import default_timer as timer
from Solving.Solvers.puzzle import *
import openai

openai.api_key = "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"


# find the clues that match the given clue by indexing the data frame
def find_clues(data, clue):
    list_of_clues = []
    clues = data[data['Clue'] == clue]
    # add each answer to the list of answers
    for index, row in clues.iterrows():
        list_of_clues.append(row['Word'])
    return list_of_clues


def find_clues_2(data, clue):
    list_of_clues = []
    clues = data[data['clue'] == clue]
    # add each answer to the list of answers
    for index, row in clues.iterrows():
        list_of_clues.append(row['answer'])
    return list_of_clues


# find the clues that are at more than 90% similarity to the given clue using rapidfuzz
def find_clues_fuzzy(data, clue):
    list_of_clues = []
    # find the clues that are at least 90% similar to the given clue
    clues = data[data['Clue'].apply(lambda x: fuzz.token_sort_ratio(x, clue) > 90)]
    # add each answer to the list of answers
    for index, row in clues.iterrows():
        list_of_clues.append(row['Word'])
    return list_of_clues


if __name__ == '__main__':

    # initialize the puzzle and the grid
    file_name = 'uc230329'
    file_path = f"Puzzles/{file_name}.puz"
    p = puz.read(file_path)
    grid = make_grid(p)
    across, down = initialize_clues(p)

    # initialize the data frame with the correct encoding
    data = pd.read_csv('Solving/Data/train.csv', encoding='latin-1')
    start = timer()

    full_grid = make_solved_grid(p)

    # find the clues that match the across clues by indexing the data frame
    h_grid = grid
    for entry in across:
        clue = entry[0]
        answer = entry[1]
        position = entry[2]
        answer_list = find_clues_2(data, clue)
        # print(answer_list)
        # only keep the answers that are the same length as the answer in the puzzle
        answer_list = [x for x in answer_list if len(x) == len(answer)]
        # keep the answer that occurs the most
        if len(answer_list) > 0:
            new_answer = max(answer_list, key=answer_list.count).upper()
            # check if all of the characters in the answer are 'X'
            if not all(char == 'X' for char in new_answer):
                h_grid = fill_horizontal(h_grid, new_answer, position)
    analyze(h_grid, full_grid)

    # repeat for down
    v_grid = grid
    for entry in down:
        clue = entry[0]
        answer = entry[1]
        position = entry[2]
        answer_list = find_clues_2(data, clue)
        answer_list = [x for x in answer_list if len(x) == len(answer)]
        if len(answer_list) > 0:
            new_answer = max(answer_list, key=answer_list.count).upper()
            # check if all of the characters in the answer are 'X'
            if not all(char == 'X' for char in new_answer):
                v_grid = fill_vertical(v_grid, new_answer, position)
    analyze(v_grid, full_grid)

    # merge the two grids from the dataset
    merged_grid_h = merge_grids(h_grid, v_grid)
    merged_grid_v = merge_grids(v_grid, h_grid)
    merged_grid = get_common_grid(merged_grid_h, merged_grid_v)
    analyze(merged_grid, full_grid)

    # # # revise the grid starting from the vertical guesses
    # h_candidates = find_horizontal_candidates(v_grid, full_grid, across, threshold=0.1)
    # revised_grid_h = revise_horizontal(v_grid, h_candidates)
    # v_candidates = find_vertical_candidates(revised_grid_h, full_grid, down, threshold=0.1)
    # # revised_grid_h = revise_vertical(revised_grid_h, v_candidates)
    # h_percent = get_accuracy(revised_grid_h, full_grid)
    # if float(h_percent) > 99.99:
    #     end = timer()
    #     # print the time with minutes and seconds
    #     print(f"Time elapsed: {int((end - start) // 60)} minutes and {int((end - start) % 60)} seconds")
    #     exit()
    #
    # # repeat for the horizontal guesses
    # v_candidates = find_vertical_candidates(h_grid, full_grid, down, threshold=0.1)
    # revised_grid_v = revise_vertical(h_grid, v_candidates)
    # h_candidates = find_horizontal_candidates(revised_grid_v, full_grid, across, threshold=0.1)
    # # revised_grid_v = revise_horizontal(revised_grid_v, h_candidates)
    # v_percent = get_accuracy(revised_grid_h, full_grid)
    # if float(v_percent) > 99.99:
    #     end = timer()
    #     # print the time with minutes and seconds
    #     print(f"Time elapsed: {int((end - start) // 60)} minutes and {int((end - start) % 60)} seconds")
    #     exit()
    #
    # initial_analyze(revised_grid_h, revised_grid_v, full_grid)
    common_grid = merged_grid

    # print("Starting revision:")
    # h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down, threshold=0.1)
    # common_grid_h = revise_horizontal(common_grid, h_candidates)
    # common_grid_v = revise_vertical(common_grid, v_candidates)
    # new_percent = initial_analyze(common_grid_h, common_grid_v, full_grid)
    #
    # common_grid = get_common_grid(common_grid_h, common_grid_v)

    thresh = 0.64
    h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down,
                                                          threshold=thresh)
    print("Starting final revision:")
    while len(h_candidates) > 0 or len(v_candidates) > 0:
        if len(h_candidates) > 0:
            common_grid = revise_horizontal(common_grid, h_candidates)
            h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down,
                                                                  threshold=thresh)
            # thresh += 0.03

        if len(v_candidates) > 0:
            common_grid = revise_vertical(common_grid, v_candidates)
            h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down,
                                                                  threshold=thresh)
            # thresh += 0.03

        if (thresh > 0.15):
            thresh -= 0.1
            print(f"Threshold is now: {thresh}")
            h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down,
                                                                  threshold=thresh)
        else:
            break

    save_grid(common_grid, f"{file_name}_revised")
    revised_grid = load_grid(f"{file_name}_revised")
    acc = analyze(revised_grid, full_grid)

    # h_candidates, v_candidates = find_revision_candidates(revised_grid, full_grid, across, down, threshold=0.74)
    # while len(h_candidates) > 0 or len(v_candidates) > 0:
    #     revised_grid = revise_vertical(revised_grid, v_candidates)
    #     h_candidates = find_horizontal_candidates(revised_grid, full_grid, across, threshold=0.74)
    #     revised_grid = revise_horizontal(revised_grid, h_candidates)
    #     h_candidates, v_candidates = find_revision_candidates(revised_grid, full_grid, across, down, threshold=0.74)
    #     analyze(revised_grid, full_grid)
    #
    # h_candidates, v_candidates = find_revision_candidates(revised_grid, full_grid, across, down, threshold=0.49)
    # while len(h_candidates) > 0 or len(v_candidates) > 0:
    #     revised_grid = revise_vertical(revised_grid, v_candidates)
    #     h_candidates = find_horizontal_candidates(revised_grid, full_grid, across, threshold=0.49)
    #     revised_grid = revise_horizontal(revised_grid, h_candidates)
    #     h_candidates, v_candidates = find_revision_candidates(revised_grid, full_grid, across, down, threshold=0.49)
    #     analyze(revised_grid, full_grid)

    save_grid(revised_grid, f"{file_name}_revised")

    end = timer()
    # print the time with minutes and seconds
    print(f"Time elapsed: {int((end - start) // 60)} minutes and {int((end - start) % 60)} seconds")
