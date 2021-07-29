from user_lib.copy import deepcopy

old_list = [[1, 2, 3], [4, 'a', 5]]
new_list = old_list

new_list = deepcopy(old_list)
new_list[1][2] = 'b'

print('Old List:', old_list)
print('ID of Old List:', id(old_list))

print('New List:', new_list)
print('ID of New List:', id(new_list))