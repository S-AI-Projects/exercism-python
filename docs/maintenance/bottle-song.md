# Bottle Song: a test that catches a singular/plural mutant

The reference chooses the wording of the final line from the number remaining
after the fall. A small deliberate mutant changes that condition from checking
whether one bottle remains to checking the starting count. This causes the
two-bottle verse to say `one green bottles`.

The smallest in-contract input that reaches the one-bottle remainder is
`recite(start=2)` (the default `take=1`). The existing
`BottleSongTest.test_verse_with_2_bottles` case rejects the mutant and expects
the final line `There'll be one green bottle hanging on the wall.` The check
runs all seven current cases against the reference and then runs this named
case against the temporary mutant. The learner starter file is not changed.
