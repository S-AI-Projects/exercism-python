# Hints

## Choosing a conversion approach

One approach first evaluates the input digits as a positional sum, then repeatedly divides that integer by the output base to collect its remainders. This keeps the conversion compact and lets Python's integer arithmetic handle the intermediate value.

Another approach keeps the value as a list of digits in the output base while reading the input from left to right. For each new input digit, multiply the stored value by the input base and add that digit, carrying across the output digits as needed.

For example, convert `101010` from base 2 to base 10. With the digit-list approach, the partial decimal digits (least significant first) evolve as:

`[0]` → `[1]` → `[2]` → `[5]` → `[0, 1]` → `[1, 2]` → `[2, 4]`

The last list represents 42 because its digits are stored in reverse order, so return `[4, 2]`. Each step appends one binary digit by doubling the partial value and adding the new digit.

The positional-sum approach is shorter and often easier to follow when the value fits comfortably in the language's integer type. The digit-list approach makes the target-base representation visible at every step and avoids building one large whole-number intermediate, but it needs carry bookkeeping and may update several stored digits for each input digit. Choose the representation that makes the conversion invariant easiest for you to reason about.
