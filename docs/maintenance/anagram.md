# Anagram reference cost

The reference filters every candidate by calling `_letters` on the candidate
and on the target. `_letters` lowercases and sorts its input. With `k`
candidates whose lengths are near `m`, the reference therefore does about
`2k` sorts and takes `O(k * m log m)` time. The target sort is repeated inside
the candidate loop. The result list can also use `O(k)` space in the case that
every candidate matches.

The check uses three valid word lengths (8, 32, and 128 letters) and 100, 300,
and 900 candidates respectively. Inputs use only lowercase letters and include
both rotations of an anagram target and same-length nonmatches. It runs each
input seven times and reports the median; the raw measurements in
`work/R36-T045/results.json` are evidence from one local run, not a performance
guarantee. The test suite also checks no matches, two anagrams, and rejection
of anagram subsets, among all 18 enabled cases.
