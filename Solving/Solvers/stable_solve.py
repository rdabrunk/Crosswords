from puzzle import *
from timeit import default_timer as timer
from Solving.Data.data import *

if __name__ == '__main__':
    # initialize the puzzle and the grid
    file_name = 'lat230403'
    file_path = f"Puzzles/{file_name}.puz"
    p = puz.read(file_path)
    grid = make_grid(p)
    full_grid = make_solved_grid(p)
    across, down = initialize_clues(p)

    # initialize the data frame with the correct encoding
    data = pd.read_csv('Solving/Data/train.csv', encoding='latin-1')
    start = timer()

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

    # Solve the grid horizontally and vertically
    h_attempt = solve_horizontal(grid, across)
    save_grid(h_attempt, f"htest")
    v_attempt = solve_vertical(grid, down)
    save_grid(v_attempt, f"vtest")

    # start by taking the common grids of the two grids from the data frame, which have the highest accuracy
    print("hgvg")
    common_grid_hgvg = get_common_grid(h_grid, v_grid)
    # analyze(common_grid_hgvg, full_grid)

    # take the rest of the common grids

    print("hava")
    common_grid_hava = get_common_grid(h_attempt, v_attempt)
    # analyze(common_grid_hava, full_grid)

    print("hgva")
    common_grid_hgva = get_common_grid(h_grid, v_attempt)
    # analyze(common_grid_hgva, full_grid)

    print("hgha")
    common_grid_hgha = get_common_grid(h_grid, h_attempt)
    # analyze(common_grid_hgha, full_grid)

    print("vgha")
    common_grid_vgha = get_common_grid(v_grid, h_attempt)
    # analyze(common_grid_vgha, full_grid)

    print("vgva")
    common_grid_vgva = get_common_grid(v_grid, v_attempt)
    # analyze(common_grid_vgva, full_grid)

    # merge the common grids in order of accuracy
    merged_grid = merge_grids(common_grid_hgvg, common_grid_hgva)
    merged_grid = merge_grids(merged_grid, common_grid_vgha)
    merged_grid = merge_grids(merged_grid, common_grid_hava)
    merged_grid = merge_grids(merged_grid, common_grid_hgha)
    merged_grid = merge_grids(merged_grid, common_grid_vgva)

    analyze(merged_grid, full_grid)

    # merge the confident grids
    # merged_grid_hgvg = merge_grids(h_grid, v_grid)
    # merged_grid = merge_grids(merged_grid, merged_grid_hgvg)
    # analyze(merged_grid, full_grid)

    common_grid = merged_grid

    thresh = 0.59
    h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down,
                                                          threshold=thresh)
    print("Starting revision:")
    while len(h_candidates) > 0 and len(v_candidates) > 0:
        common_grid_h = common_grid
        common_grid_v = common_grid
        h_attempts = 0
        v_attempts = 0

        while len(h_candidates) > 0 and h_attempts < 4:
            common_grid_h = revise_horizontal(common_grid_h, h_candidates)
            h_candidates, v_candidates = find_revision_candidates(common_grid_h, full_grid, across, down,
                                                                  threshold=thresh)
            h_attempts += 1
            print(h_attempts)

        while len(v_candidates) > 0 and v_attempts < 4:
            common_grid_v = revise_vertical(common_grid_v, v_candidates)
            h_candidates, v_candidates = find_revision_candidates(common_grid_v, full_grid, across, down,
                                                                  threshold=thresh)
            v_attempts += 1
            print(v_attempts)

        common_grid = get_common_grid(common_grid_h, common_grid_v)

        if (thresh > 0.02):
            thresh -= 0.15
            print(f"Threshold is now: {thresh}")
            h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down,
                                                                  threshold=thresh)
        else:
            break

    revised_grid = common_grid
    save_grid(common_grid, f"{file_name}_revised")
    # revised_grid = load_grid(f"test")
    acc = analyze(revised_grid, full_grid)
    final_grid_priority = revised_grid

    # h_candidates, v_candidates = find_revision_candidates(revised_grid, full_grid, across, down, threshold=0)
    #
    # print("Checking horizontal:")
    # checked_grid_h = check_horizontal(revised_grid, h_candidates)
    # # analyze(checked_grid_h, full_grid)
    # print("Checking vertical:")
    # checked_grid_v = check_vertical(revised_grid, v_candidates)
    # # analyze(checked_grid_v, full_grid)
    #
    # print("merging checked grids:")
    # checked_grid = get_common_grid(checked_grid_h, checked_grid_v)
    # acc = analyze(checked_grid, full_grid)
    #
    # common_grid = checked_grid
    # thresh = 0.64
    # h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down,
    #                                                       threshold=thresh)
    # print("Starting final revision:")
    # while len(h_candidates) > 0 or len(v_candidates) > 0:
    #     if len(h_candidates) > 0:
    #         common_grid = revise_horizontal(common_grid, h_candidates)
    #         h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down,
    #                                                               threshold=thresh)
    #         # thresh += 0.03
    #
    #     if len(v_candidates) > 0:
    #         common_grid = revise_vertical(common_grid, v_candidates)
    #         h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down,
    #                                                               threshold=thresh)
    #         # thresh += 0.03
    #
    #     if (thresh > 0.15):
    #         thresh -= 0.1
    #         print(f"Threshold is now: {thresh}")
    #         h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down,
    #                                                               threshold=thresh)
    #     else:
    #         break
    #
    # final_grid = common_grid
    # save_grid(final_grid, f"{file_name}_final")
    # acc = analyze(revised_grid, full_grid)

    thresh = 0.64
    h_priority = False
    h_candidates, v_candidates = find_revision_candidates(revised_grid, full_grid, across, down, threshold=thresh)
    print("Starting final revision:")
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

    acc = analyze(revised_grid, full_grid)
    final_grid = merge_grids(final_grid_priority, revised_grid)
    save_grid(final_grid, f"{file_name}_final")
    acc = analyze(final_grid, full_grid)

    end = timer()
    print(f"Time elapsed: {int((end - start) // 60)} minutes and {int((end - start) % 60)} seconds")
