#####################################################
#                                                   #
#   Quick Starter on Python Sets                    #
#                                                   #
#   Author: Braden Dubois (braden.dubois@usask.ca)  #
#   Written for: Dr. Eric Neufeld                   #
#                                                   #
#####################################################

#######################################
# Creating a Set
#######################################

my_first_set = set()

print("Empty Set:", my_first_set)

print("\nTrying single-element set constructors.")

# You can specify one value, but will get an error that it expected something iterable
try:
    single_element_set = set(1)
    print("One element set:", single_element_set)
except TypeError:
    print("Can't do non-iterable constructor parameters.")

# You really want to put a list or similar iterable container in to the constructor
single_element_set = set([1])
print("\nOne element set (proper constructor):", single_element_set)

# Which, of course, can be a list of multiple values
multiple_element_set = set([6, 2, 3, 1, 4, 5])
print("Multiple element set:", multiple_element_set)

# We should really drop the constructor though.
better_constructor = {6, 2, 3, 1, 4, 5}

#######################################
#   Set Membership
#######################################

print("\nExamples with set membership")

print("Does the prior set contain 4?:", 4 in multiple_element_set)
print("What about 9?:", 9 in multiple_element_set)

#######################################
#   Lists <--> Sets
#######################################

print("\nExamples of how lists can be sorted/converted to lists")

# Sets are iterable, but don't guarantee ordering, so calling sorted will return a *new* LIST of values, but sorted
print("Sorted:", sorted(multiple_element_set))  # It does seem to sort when it's only integers, interestingly...

# We can also quick create a list from the set
my_list_from_set = list(multiple_element_set)
print("List Created:", my_list_from_set, "of type:", type(my_list_from_set))

# The following examples sort the resulting sets. It's obviously not needed to print a set, I just think it shows
#   the examples more clearly so you can see the difference between sets.

#######################################
#    Updating Sets
#######################################

print("\nUpdating set to include 1 and 7.")

# We can easily add a value into a set, but this doesn't return a new set
multiple_element_set.update([7])  # New Value
multiple_element_set.update([1])  # Ignore duplicates
print("Updated set:", multiple_element_set)

#######################################
#  Some slick set properties
#######################################

print("\nSome slick set properties involving |, &, ^")

# All of the following operations will return *new* sets

consonants = {"b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "y", "z"}
vowels = {"a", "e", "i", "o", "u", "y"}

print("\nConsonants:", sorted(consonants))
print("Vowels:", sorted(vowels))

# I'll just back these up to prove later that the original sets are not modified.
consonants_backup = {"b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "y", "z"}
vowels_backup = {"a", "e", "i", "o", "u", "y"}
assert consonants == consonants_backup and vowels == vowels_backup, "Backup sets of consonants and vowels are not the same."

# Set Union: use the pipe "|" operator for "or"/union
print("\nEntire Alphabet:", sorted(consonants | vowels))

# Set Intersection: use the ampersand "&" for what is in *both* sets
print("Protean letters:", consonants & vowels)

# Disjoint sets: Use the caret "^" for the set disjoint
print("Well-defined letters who play it safe:", sorted(consonants ^ vowels))

# We can also take set difference with minus signs
print("\nThe consonants have kicked out 'y':", sorted(consonants - {"y"}))
# NOTE: +. *, and / are *NOT* defined for sets.

print("\nA neat (and contrived) example merging two sets")

# And the original sets were not modified!
assert consonants == consonants_backup and vowels == vowels_backup, "Backup sets of consonants and vowels are not the same."

# Same as how we can combine equals signs with the operator in regular arithmetic,  +=. -=, /=, *=, we can use
#   these set operators to assign the sets to variables

# Worth noting that this does not create a new set; this creates a pointer to the same set
consonants_accepting_new_members = consonants
for vowel in vowels:
    print("\nThe set of consonants accepting new members has welcomed:", vowel)
    consonants_accepting_new_members |= {vowel}
    print(sorted(consonants_accepting_new_members))

# Let's ensure now that our pointer to the same set really did change the original set
try:
    # This should actually fail, since consonants was modified through consonants_accepting_new_members
    assert consonants == consonants_backup, "Consonants are not the same."
    raise Exception("The original set of consonants was not modified?!")
except AssertionError:
    print("\nConsonants has indeed, been modified.")

#######################################
#   Automata Theory Example
#######################################

print("\nSet membership used in a less contrived example.")

# In some free time I'm overhauling a bit of my automata theory project, but these set operations are great.
#   For example, consider the definition of acceptance of a world in an NFA
F = {"q0", "q1", "q5"}
results = {"q1", "q3"}
print("Word accepted in NFA:", F, "&", results, "!=", set(), ":", F & results != set())
