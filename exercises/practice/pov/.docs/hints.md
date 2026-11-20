# Hints

## 1. Detach Child Before Inverting Parent Relationship

When re-rooting a tree from a child node, remember that the child becomes the new parent of its former parent. However, the former parent must no longer list the child among its own children.

If you attach the former parent directly to the child without first removing the child from the parent's children list, the parent will retain a cyclical or duplicate reference back to the child (e.g. `Tree("parent", [Tree("sibling")])` would mistakenly remain `Tree("parent", [Tree("sibling"), Tree("x")])`). For a quick diagnostic, test re-rooting a tree `Tree("parent", [Tree("x"), Tree("sibling")])` from `"x"` and check whether `"x"` appears as a child of `"parent"` in the result.
