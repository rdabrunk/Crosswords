from puzzle import *
from Solving.Data.data import *
import openai
from timeit import default_timer as timer


if __name__ == '__main__':

    file_name = 'Universal - 20230401 - Universal Freestyle 66'
    file_path = f"Puzzles/{file_name}.puz"
    p = puz.read(file_path)
    grid = make_grid(p)
    full_grid = make_solved_grid(p)
    across, down = initialize_clues(p)

    # initialize the data frame with the correct encoding
    data = pd.read_csv('Solving/Data/train.csv', encoding='latin-1')
    start = timer()

    # find the clues that match the across clues by indexing the data frame  # find the clues that match the across clues by indexing the data frame
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

    # merge the two grids
    merged_grid_h = merge_grids(h_grid, v_grid)
    merged_grid_v = merge_grids(v_grid, h_grid)
    merged_grid = get_common_grid(merged_grid_h, merged_grid_v)
    analyze(merged_grid, full_grid)

    # # do an initial revision by trying filling from both sides and taking the common grid between them
    # print("Starting revision:")
    # h_candidates, v_candidates = find_revision_candidates(merged_grid, full_grid, across, down, threshold=0.1)
    # common_grid_h = revise_horizontal(merged_grid, h_candidates)
    # common_grid_v = revise_vertical(merged_grid, v_candidates)
    # new_percent = initial_analyze(merged_grid, common_grid_v, full_grid)
    #
    # revised_grid = get_common_grid(common_grid_h, common_grid_v)

    revised_grid = merged_grid
    thresh = 0.64
    # revise the grid
    h_candidates, v_candidates = find_revision_candidates(revised_grid, full_grid, across, down, threshold=thresh)

    print("Starting revision:")
    while len(h_candidates) > 0 or len(v_candidates) > 0:
        if len(h_candidates) > 0:
            revised_grid = revise_horizontal(revised_grid, h_candidates)
            h_candidates, v_candidates = find_revision_candidates(revised_grid, full_grid, across, down,
                                                                  threshold=thresh)

        if len(v_candidates) > 0:
            revised_grid = revise_vertical(revised_grid, v_candidates)
            h_candidates, v_candidates = find_revision_candidates(revised_grid, full_grid, across, down,
                                                                  threshold=thresh)

        if (thresh > 0.15):
            thresh -= 0.1
            print(f"Threshold is now: {thresh}")
            h_candidates, v_candidates = find_revision_candidates(revised_grid, full_grid, across, down,
                                                                  threshold=thresh)

        else:
            break

    # save_grid(revised_grid, f"{file_name}_revised")
    acc = analyze(revised_grid, full_grid)

    # h_candidates, v_candidates = find_revision_candidates(revised_grid, full_grid, across, down, threshold=0)
    #
    # print("Checking horizontal:")
    # checked_grid = check_horizontal(revised_grid, h_candidates)
    # # analyze(checked_grid_h, full_grid)
    # print("Checking vertical:")
    # checked_grid = check_vertical(checked_grid, v_candidates)
    # # analyze(checked_grid_v, full_grid)
    #
    # acc = analyze(checked_grid, full_grid)

    # print("merging checked grids:")
    # checked_grid = get_common_grid(checked_grid_h, checked_grid_v)
    # acc = analyze(checked_grid, full_grid)
    # print(acc)

    # do a final revision by trying to fill from both sides and taking the common grid between them
    # thresh = 0.64
    # h_candidates, v_candidates = find_revision_candidates(checked_grid, full_grid, across, down, threshold=thresh)
    # print("Starting final revision:")
    # while len(h_candidates) > 0 or len(v_candidates) > 0:
    #     if len(h_candidates) > 0:
    #         checked_grid = revise_horizontal(checked_grid, h_candidates)
    #         h_candidates, v_candidates = find_revision_candidates(checked_grid, full_grid, across, down,
    #                                                               threshold=thresh)
    #
    #     if len(v_candidates) > 0:
    #         checked_grid = revise_vertical(checked_grid, v_candidates)
    #         h_candidates, v_candidates = find_revision_candidates(checked_grid, full_grid, across, down,
    #                                                               threshold=thresh)
    #
    #     if (thresh > 0.05):
    #         thresh -= 0.1
    #         print(f"Threshold is now: {thresh}")
    #         h_candidates, v_candidates = find_revision_candidates(checked_grid, full_grid, across, down,
    #                                                               threshold=thresh)
    #     else:
    #         break
    #
    # save_grid(checked_grid, f"{file_name}_final")
    # acc = analyze(checked_grid, full_grid)

    end = timer()
    print(f"Time elapsed: {int((end - start) // 60)} minutes and {int((end - start) % 60)} seconds")
