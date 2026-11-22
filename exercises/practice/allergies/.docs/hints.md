# Hints

## Choosing a representation

The reference keeps the score as a bit mask and probes the bit for each item
when `allergic_to` is called. For an object that will be queried many times, an
alternative is to decode the known bits once into a set of selected names and
then use set membership. A set uses extra memory and takes work to build, so
the direct bit test is simpler for a small number of queries. The set can make
repeated membership checks easier to read; build the public `lst` in the
exercise's listed order rather than relying on set iteration order.

For example, score `5` has its first and third known bits set (`1 + 4`), so it
selects eggs and shellfish:

<!-- approach-example-start -->
```python
allergens = ["eggs", "peanuts", "shellfish"]
score = 5
selected = {
    item for bit, item in enumerate(allergens) if score & (1 << bit)
}
print("shellfish" in selected)
print([item for item in allergens if item in selected])
```
<!-- approach-example-end -->

The output is:

```text
True
['eggs', 'shellfish']
```
