import puz
import gpt_integration
import csv
from timeit import default_timer as timer
import openai

openai.api_key = "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"


def initialize_clues(puzzle):
    numbering = puzzle.clue_numbering()
    across = []

    full_grid = make_solved_grid(puzzle)

    down = []
    down_answers = get_ordered_vertical_answers(full_grid)

    x = 0
    y = 0
    for clue in numbering.across:
        answer = ''.join(
            puzzle.solution[clue['cell'] + i]
            for i in range(clue['len']))
        across.append((clue['clue'], answer, x))
        x += 1

    for clue in numbering.down:
        answer = ''.join(
            puzzle.solution[clue['cell'] + i * numbering.width]
            for i in range(clue['len']))

        num = down_answers.index(answer)

        down.append((clue['clue'], answer, num))
        y += 1

    return across, down

    return clues


def make_grid(puzzle):
    grid = []
    for row in range(puzzle.height):
        cell = row * puzzle.width
        grid.append(puzzle.fill[cell:cell + puzzle.width])
    return grid


def make_solved_grid(puzzle):
    grid = []
    for row in range(puzzle.height):
        cell = row * puzzle.width
        grid.append(puzzle.solution[cell:cell + puzzle.width])
    return grid


def save_grid(grid, file_name):
    file_name = f"Solving/solve_attempts/{file_name}.csv"
    # write the grid to a csv file with no delimiters
    with open(file_name, 'w', newline='') as file:
        for row in grid:
            file.write(f"{'  '.join(row)}\n")


def load_grid(file_name):
    file_name = f"Solving/solve_attempts/{file_name}.csv"
    grid = []
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            grid.append(row[0].split())
    return grid


def print_grid(grid):
    for row in grid:
        print('  '.join(row))


def to_horizontal(grid):
    horizontal_grid = []
    for row in grid:
        # split each row into a list of dashes, use periods as delimiters
        row = ''.join(row).split('.')
        horizontal_grid.append(row)
    return horizontal_grid


def to_vertical(grid):
    vertical_grid = []
    for i in range(len(grid[0])):
        column = []
        for row in grid:
            column.append(row[i])
        new_column = ''.join(column).split('.')
        vertical_grid.append(new_column)
    return vertical_grid


def get_ordered_vertical_answers(grid):
    grid = to_vertical(grid)
    vertical = []
    for row in grid:
        for word in row:
            if word != '':
                vertical.append(word)
    return vertical


def fill_horizontal(grid, word, location):
    # locate the position of the word in the grid
    horizontal_grid = to_horizontal(grid)
    count = 0
    x = 0
    y = 0
    while count != (location):
        entry = horizontal_grid[y][x]
        if x == len(horizontal_grid[y]) - 1:
            y += 1
            x = 0
            if entry != "":
                count += 1
        elif entry == '':
            x += 1
        else:
            x += 1
            count += 1
    while horizontal_grid[y][x] == '':
        if x == len(horizontal_grid[y]) - 1:
            y += 1
            x = 0
        else:
            x += 1

    # fill in the word
    horizontal_grid[y][x] = word

    # recreate the grid
    grid = []
    for i in range(len(horizontal_grid)):
        row = '.'.join(horizontal_grid[i])
        grid.append(row)
    return grid


def fill_vertical(grid, word, location):
    #   locate the position of the word in the grid
    vertical_grid = to_vertical(grid)
    grid_length = len(grid)

    count = 0
    x = 0
    y = 0
    while count != (location):
        entry = vertical_grid[y][x]
        if x == len(vertical_grid[y]) - 1:
            y += 1
            x = 0
            if entry != "":
                count += 1
        elif entry == '':
            x += 1
        else:
            x += 1
            count += 1
    while vertical_grid[y][x] == '':
        if x == len(vertical_grid[y]) - 1:
            y += 1
            x = 0
        else:
            x += 1

    # fill in the word
    vertical_grid[y][x] = word

    # recreate the grid
    grid = []
    for i in range(grid_length):
        row = []
        for j in range(grid_length):
            row.append('')
        grid.append(row)
    for i in range(len(vertical_grid)):
        column = '.'.join(vertical_grid[i])
        for j in range(len(column)):
            grid[j][i] = column[j]
    return grid


def solve_horizontal(grid, across):
    for entry in across:
        clue = entry[0]
        clue_answer = entry[1]
        clue_location = entry[2]
        if len(clue_answer) < 7:
            answer = gpt_integration.generate_answer_3(clue, len(clue_answer))
            grid = fill_horizontal(grid, answer, clue_location)
            for row in grid:
                print("  ".join(row))
    return grid


def solve_vertical(grid, down):
    for entry in down:
        clue = entry[0]
        clue_answer = entry[1]
        clue_location = entry[2]
        if len(clue_answer) < 7:
            answer = gpt_integration.generate_answer_3(clue, len(clue_answer))
            grid = fill_vertical(grid, answer, clue_location)
            for row in grid:
                print("  ".join(row))
    return grid


def get_accuracy(attempt, correct_grid):
    correct = 0
    num_black_squares = 0
    for i in range(len(attempt)):
        for j in range(len(attempt[i])):
            if attempt[i][j] == correct_grid[i][j]:
                correct += 1
            if attempt[i][j] == '.':
                num_black_squares += 1
    # format the accuracy as a percentage
    accuracy = ((correct - num_black_squares) / (len(attempt) * len(attempt[0]) - num_black_squares)) * 100
    # return the accuracy formatted to 2 decimal places
    return "{:.2f}".format(accuracy)


def get_common_grid(grid_1, grid_2):
    common_grid = []
    for i in range(len(grid_1)):
        row = []
        for j in range(len(grid_1[i])):
            if grid_1[i][j] == grid_2[i][j]:
                row.append(grid_1[i][j])
            else:
                row.append('-')
        common_grid.append(row)
    return common_grid


def initial_analyze(horizontal_solve, vertical_solve, solved_grid):
    horizontal_accuracy = get_accuracy(horizontal_solve, solved_grid)
    vertical_accuracy = get_accuracy(vertical_solve, solved_grid)
    common_grid = get_common_grid(horizontal_solve, vertical_solve)
    combined_with_full = get_common_grid(common_grid, solved_grid)
    percent_grid_filled = get_percentage_filled(common_grid, solved_grid)
    common_accuracy = get_accuracy(common_grid, combined_with_full)
    print("Analysis for initial horizontal and vertical attempts:")
    print("------------------------------------------------------")
    print("Common Grid:")
    print_grid(common_grid)
    print(f"Horizontal Accuracy: {horizontal_accuracy}%")
    print(f"Vertical Accuracy: {vertical_accuracy}%")
    print(f"Percent of grid filled: {percent_grid_filled}%")
    print(f"Accuracy of confident fill: {common_accuracy}%")
    return percent_grid_filled


def find_revision_candidates(common_grid, solved_grid, across, down, threshold=0.65):
    horizontal_candidates = []
    vertical_candidates = []

    horizontal_grid = to_horizontal(common_grid)
    vertical_grid = to_vertical(common_grid)
    solved_horizontal_grid = to_horizontal(solved_grid)
    solved_vertical_grid = to_vertical(solved_grid)

    for i in range(len(horizontal_grid)):
        for j in range(len(horizontal_grid[i])):
            if len(horizontal_grid[i][j]) > 0:
                percent_dashes = horizontal_grid[i][j].count('-') / len(horizontal_grid[i][j])
                # get the percentage of letters that are not dashes
                percent_letters = 1 - percent_dashes
                if percent_letters >= threshold:
                    # check if no letters are dashes
                    if horizontal_grid[i][j].count('-') != 0:
                        correct_word = solved_horizontal_grid[i][j]
                        # find the location of the word in the across list
                        location = 0
                        for entry in across:
                            if entry[1] == correct_word:
                                correct_entry = entry
                                break
                            location += 1
                        horizontal_candidate = (correct_entry + (horizontal_grid[i][j].replace('-', '_'),))
                        horizontal_candidates.append(horizontal_candidate)

    for i in range(len(vertical_grid)):
        for j in range(len(vertical_grid[i])):
            if len(vertical_grid[i][j]) > 0:
                percent_dashes = vertical_grid[i][j].count('-') / len(vertical_grid[i][j])
                # get the percentage of letters that are not dashes
                percent_letters = 1 - percent_dashes
                if percent_letters >= threshold:
                    # check if no letters are dashes
                    if vertical_grid[i][j].count('-') != 0:
                        correct_word = solved_vertical_grid[i][j]
                        # find the location of the word in the across list
                        location = 0
                        for entry in down:
                            if entry[1] == correct_word:
                                correct_entry = entry
                                # remove the word from the across list
                                break
                            location += 1
                        vertical_candidate = (correct_entry + (vertical_grid[i][j].replace('-', '_'),))
                        vertical_candidates.append(vertical_candidate)

    return horizontal_candidates, vertical_candidates


def find_horizontal_candidates(common_grid, solved_grid, across, threshold=0.65):
    horizontal_candidates = []

    horizontal_grid = to_horizontal(common_grid)
    solved_horizontal_grid = to_horizontal(solved_grid)

    for i in range(len(horizontal_grid)):
        for j in range(len(horizontal_grid[i])):
            if len(horizontal_grid[i][j]) > 0:
                percent_dashes = horizontal_grid[i][j].count('-') / len(horizontal_grid[i][j])
                # get the percentage of letters that are not dashes
                percent_letters = 1 - percent_dashes
                if percent_letters >= threshold:
                    # check if no letters are dashes
                    if horizontal_grid[i][j].count('-') != 0:
                        correct_word = solved_horizontal_grid[i][j]
                        # find the location of the word in the across list
                        location = 0
                        for entry in across:
                            if entry[1] == correct_word:
                                correct_entry = entry
                                break
                            location += 1
                        horizontal_candidate = (correct_entry + (horizontal_grid[i][j].replace('-', '_'),))
                        horizontal_candidates.append(horizontal_candidate)

    return horizontal_candidates


def find_vertical_candidates(common_grid, solved_grid, down, threshold=0.65):
    vertical_candidates = []

    vertical_grid = to_vertical(common_grid)
    solved_vertical_grid = to_vertical(solved_grid)

    for i in range(len(vertical_grid)):
        for j in range(len(vertical_grid[i])):
            if len(vertical_grid[i][j]) > 0:
                percent_dashes = vertical_grid[i][j].count('-') / len(vertical_grid[i][j])
                # get the percentage of letters that are not dashes
                percent_letters = 1 - percent_dashes
                if percent_letters >= threshold:
                    # check if no letters are dashes
                    if vertical_grid[i][j].count('-') != 0:
                        correct_word = solved_vertical_grid[i][j]
                        # find the location of the word in the down list
                        location = 0
                        for entry in down:
                            if entry[1] == correct_word:
                                correct_entry = entry
                                break
                            location += 1
                        vertical_candidate = (correct_entry + (vertical_grid[i][j].replace('-', '_'),))
                        vertical_candidates.append(vertical_candidate)

    return vertical_candidates


def revise_horizontal(grid, horizontal_candidates):
    for candidate in horizontal_candidates:
        clue = candidate[0]
        clue_location = candidate[2]
        current_answer = candidate[3]
        new_answer = gpt_integration.revise_answer(clue, len(current_answer), current_answer)
        if new_answer == None:
            break
        grid = fill_horizontal(grid, new_answer, clue_location)
        for row in grid:
            print("  ".join(row))
        print()
    return grid


def revise_vertical(grid, vertical_candidates):
    for candidate in vertical_candidates:
        clue = candidate[0]
        clue_location = candidate[2]
        current_answer = candidate[3]
        new_answer = gpt_integration.revise_answer(clue, len(current_answer), current_answer)
        if new_answer == None:
            break
        grid = fill_vertical(grid, new_answer, clue_location)
        for row in grid:
            print("  ".join(row))
        print()
    return grid


def get_percentage_filled(grid, solved_grid):
    # get the number of squares that are filled in the grid
    filled = 0
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] != '-' and grid[i][j] != '.':
                filled += 1
    print(filled)
    # get the number of squares that are filled in the solved grid
    solved_filled = 0
    for i in range(len(solved_grid)):
        for j in range(len(solved_grid[i])):
            if solved_grid[i][j] != '-' and solved_grid[i][j] != '.':
                solved_filled += 1
    # return the percentage of the grid that is filled formatted to 2 decimal places
    return round(filled / solved_filled * 100, 2)


def analyze(grid, solved_grid):
    accuracy = get_accuracy(grid, solved_grid)
    combined_with_full = get_common_grid(grid, solved_grid)
    percent_grid_filled = get_percentage_filled(grid, solved_grid)
    common_accuracy = get_accuracy(grid, combined_with_full)
    print("Analysis for Revised Grid:")
    print("------------------------------------------------------")
    print("Revised Grid:")
    print_grid(grid)
    # find the percentage of the grid that is filled
    print(f"Raw accuracy: {accuracy}%")
    print(f"Percentage of grid filled: {percent_grid_filled}%")
    print(f"Accuracy of filled squares: {common_accuracy}%")

    return float(accuracy)


def merge_grids(grid1, grid2):
    merged_grid = []
    for i in range(len(grid1)):
        row = []
        for j in range(len(grid1[i])):
            if grid1[i][j] != '-' and grid1[i][j] != '.':
                row.append(grid1[i][j])
            else:
                row.append(grid2[i][j])
        merged_grid.append(row)
    return merged_grid


if __name__ == '__main__':

    start = timer()

    file_name = 'nyt230328'

    file_path = f"Puzzles/{file_name}.puz"
    p = puz.read(file_path)
    empty_grid = make_grid(p)
    across, down = initialize_clues(p)

    full_grid = make_solved_grid(p)

    # Solve the grid horizontally and vertically, then save the results
    horizontal_attempt = solve_horizontal(empty_grid, across)
    save_grid(horizontal_attempt, f"{file_name}_horizontal")

    vertical_attempt = solve_vertical(empty_grid, down)
    save_grid(vertical_attempt, f"{file_name}_vertical")

    horizontal_solve = load_grid(f"{file_name}_horizontal")
    vertical_solve = load_grid(f"{file_name}_vertical")

    # Analyze the first attempts
    percent_filled = initial_analyze(horizontal_solve, vertical_solve, full_grid)

    # combine the two grids from the horizontal and vertical solves
    common_grid = get_common_grid(horizontal_solve, vertical_solve)

    print("Starting revision:")
    h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down, threshold=0.1)
    common_grid_h = revise_horizontal(common_grid, h_candidates)
    common_grid_v = revise_vertical(common_grid, v_candidates)
    new_percent = initial_analyze(common_grid_h, common_grid_v, full_grid)

    common_grid = get_common_grid(common_grid_h, common_grid_v)

    thresh = 0.64
    # revise the grid
    h_candidates, v_candidates = find_revision_candidates(common_grid, full_grid, across, down, threshold=thresh)

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
    thresh = 0.64

    # check the grid against the full grid if the accuracy is too low and try again
    number_of_checks = 0
    # check_answer = input("Check against full grid? (y/n): ")
    # if check_answer == 'y':
    #
    #     while acc < 98 and number_of_checks < 2:
    #         print("Accuracy is too low, using check all")
    #
    #         checked_grid = get_common_grid(revised_grid, full_grid)
    #
    #         h_candidates, v_candidates = find_revision_candidates(checked_grid, full_grid, across, down, threshold=thresh)
    #
    #         while len(h_candidates) > 0 or len(v_candidates) > 0:
    #             if len(h_candidates) > 0:
    #                 checked_grid = revise_horizontal(checked_grid, h_candidates)
    #                 h_candidates, v_candidates = find_revision_candidates(checked_grid, full_grid, across, down,
    #                                                                       threshold=thresh)
    #
    #             if len(v_candidates) > 0:
    #                 checked_grid = revise_vertical(checked_grid, v_candidates)
    #                 h_candidates, v_candidates = find_revision_candidates(checked_grid, full_grid, across, down,
    #                                                                       threshold=thresh)
    #
    #             if (thresh > 0.15):
    #                 thresh -= 0.1
    #                 print(f"Threshold is now: {thresh}")
    #                 h_candidates, v_candidates = find_revision_candidates(checked_grid, full_grid, across, down,
    #                                                                       threshold=thresh)
    #             else:
    #                 break
    #
    #         save_grid(checked_grid, f"{file_name}_checked")
    #         checked_grid = load_grid(f"{file_name}_checked")
    #         number_of_checks += 1
    #         analyze(checked_grid, full_grid)
    #         print(f"Number of checks used: {number_of_checks}")

    end = timer()
    # print the time with minutes and seconds
    print(f"Time elapsed: {int((end - start) // 60)} minutes and {int((end - start) % 60)} seconds")
