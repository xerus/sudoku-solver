#!/usr/bin/env python

from math import sqrt


class Sudoku(object):
    """docstring for Sudoku"""
    def __init__(self, rows=[], dim=9, boxes=9):
        super(Sudoku, self).__init__()
        self.dim = dim
        self.box_lim = int(sqrt(dim))
        self.numbers_range = set(range(1, dim+1))
        self.grid = [self.numbers_range] * (self.dim * self.dim)
        if rows != []:
            self.initialize_by_rows(rows)
            self.to_grid()
            self.solve()


    def make_boxes(self):
        boxes = []
        dim = self.dim
        rows = self.get_rows()
        for ri in range(0, dim, 3):
            for ci in range(0, dim, 3):
                boxes.append([rows[i][j] for i in range(ri, ri+3) for j in range(ci, ci+3)])
        return boxes

    def make_columns(self):
        rows = self.get_rows()
        return [[rows[i][j] for i in range(self.dim)] for j in range(self.dim)]

    def from_grid(self, grid=None):
        if grid == None:
            grid = self.grid
        else:
            self.grid = grid
        def f(arr):
            if len(arr) > 1 or len(arr) == 0:
                return 0
            else:
                return next(iter(arr))
        self.rows = [[f(grid[ri*self.dim + ji]) for ji in range(self.dim)] for ri in range(self.dim)]
        self.initialize_by_rows(self.rows)
        self.to_grid()

    def row_of_grid(self, index):
        return self.grid[index * self.dim : (index + 1) * self.dim]

    def column_of_grid(self, index):
        return [self.grid[i] for i in range(index, len(self.grid), self.dim)]

    def box_of_grid(self, index):
        return [self.grid[i] for i in range(len(self.grid)) if self.box_by_grid(i) == index]

    def row_by_grid(self, index):
        return index // self.dim

    def column_by_grid(self, index):
        return index % self.dim

    def box_by_grid(self, index):
        ri = self.row_by_grid(index)
        ci = self.column_by_grid(index)
        return (ri // self.box_lim) * self.box_lim + ci // self.box_lim

    def possibilities(self, index, miss_rows = None, miss_columns = None, miss_boxes = None):
        if miss_rows == None:
            miss_rows = self.get_rows_missing_values()
        if miss_columns == None:
            miss_columns = self.get_columns_missing_values()
        if miss_boxes == None:
            miss_boxes = self.get_boxes_missing_values()
        ri = self.row_by_grid(index)
        ci = self.column_by_grid(index)
        bi = self.box_by_grid(index)
        tmp_poss = self.grid[index] & miss_rows[ri] & miss_columns[ci] & miss_boxes[bi]
        if len(tmp_poss) == 1:
            return tmp_poss
        for p in tmp_poss:
            for items in [self.row_of_grid(ri), self.column_of_grid(ci), self.box_of_grid(bi)]:
                pos_cnt = 0
                for item in items:
                    if p in item:
                        pos_cnt += 1
                if pos_cnt == 1:
                    return set([p])
        return tmp_poss

    def to_grid(self):
        miss_rows = self.get_rows_missing_values()
        miss_columns = self.get_columns_missing_values()
        miss_boxes = self.get_boxes_missing_values()
        i = 0
        for row in self.rows:
            for value in row:
                if value == 0:
                    self.grid[i] = self.possibilities(i, miss_rows, miss_columns, miss_boxes)
                else:
                    self.grid[i] = set([value])
                i += 1

    def get_rows(self):
        return self.rows

    def get_boxes(self):
        return self.boxes

    def get_columns(self):
        return self.columns

    def get_grid(self):
        return self.grid

    def initialize_by_rows(self, rows):
        self.rows = rows
        self.columns = self.make_columns()
        self.boxes = self.make_boxes()

    def solve(self,param=None):
        change = True
        while change:
            old = self.wrong_values_count()
            self.from_grid()
            change = (old != self.wrong_values_count())

        # guess and try
        if self.wrong_values_count() == 0:
            return
        # print(param)
        # print(self)
        min_index = 0
        min_cnt = len(self.numbers_range) + 1
        newgrid = self.grid[:]

        min_field = None
        for i in range(len(newgrid)): # nalezeni prvku s nejmensim poctem moznosti
            field = newgrid[i]
            if len(field) < min_cnt and len(field) > 1:
                min_cnt = len(field)
                min_index = i
                min_field = field
        # mam policko s nejmensim poctem
        if min_field == None:
            # print(self)
            # print(self.wrong_values_count())
            return
        newsudoku = None
        rows_copy = self.get_rows()[:]
        for var in min_field:
            try:                
                rows_copy[self.row_by_grid(min_index)][self.column_by_grid(min_index)] = var
                newsudoku = Sudoku(rows_copy)
            except:
                continue
            if newsudoku.wrong_values_count() == 0:
                self.from_grid(newsudoku.get_grid())
                break


    def is_valid(self):
        return 0 == self.wrong_values_count()

    def missing_values(self, arr):
        return self.numbers_range - set(arr)

    def get_rows_missing_values(self):
        return [self.missing_values(row) for row in self.rows]

    def get_columns_missing_values(self):
        return [self.missing_values(col) for col in self.columns]

    def get_boxes_missing_values(self):
        return [self.missing_values(box) for box in self.boxes]

    def get_grid_missing_values(self):
        possible_values = []
        miss_rows = self.get_rows_missing_values()
        miss_columns = self.get_columns_missing_values()
        miss_boxes = self.get_boxes_missing_values()
        for i in range(len(self.grid)):
            poss = self.possibilities(i, miss_rows, miss_columns, miss_boxes)
            if len(poss) > 1:
                possible_values.append(poss)
        return possible_values

    def wrong_values_count(self):
        wrong_cnt = 0
        element_functions = [self.get_rows, self.get_columns, self.get_boxes]
        for getlist in element_functions:
            ilist = getlist()
            for item in ilist:
                wrong_cnt += self.dim - len(self.numbers_range & set(item))
        return wrong_cnt

    def __repr__(self):
        s = ""
        for ri in range(len(self.grid)):
                if ri > 0:
                    if ri % (self.dim * sqrt(self.dim)) == 0:
                        s += "\n" + "-" * int((self.dim + self.dim // sqrt(self.dim) - 1)*2 - 1)
                    if ri % self.dim == 0:
                        s += "\n"
                    elif ri % (self.dim // sqrt(self.dim)) == 0:
                        s += " | "
                    else:
                        s += " "
                els = self.grid[ri]
                s += str(0 if len(els) > 1 or 0 == len(els) else next(iter(els)))
        return s

def to_numbers(lines):
    return [[int(lines[i][j]) for j in range(len(lines[i].strip()))] for i in range(len(lines))]

def replace_zeros(row, values):
    return [values.pop() if i == 0 else i for i in row]

def replace_zeros_in_grid(grid, values):
    replaced = [set([values.pop()]) if len(field) > 1 else field for field in grid]
    # print(grid, replaced)
    return replaced

def missing_row_values_to_specimen(missing_in_row):
    return [[0, maxvalue] for maxvalue in range(len(missing_in_row) - 1, 0, -1)]

def missing_grid_values_to_specimen(missing_in_grid):
    return [[0, len(field)-1] for field in missing_in_grid]

