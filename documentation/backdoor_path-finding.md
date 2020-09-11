# Backdoor Path-finding

A brief explanation of the modified path-finding algorithm used in the Backdoor Controller to find a "backdoor path". 
Most of it is fairly straightforward; the key to the backdoor detection algorithm is understanding the meaning of a backdoor path, and especially so on "blocking" these paths. You find that a variable might be necessarily in Z, but in putting it in Z (as in the case of a collider) can still *open* a path; the path-finding must be nuanced enough to understand that something in Z or not in Z changes whether we can go "up" (child to parent), "down" (parent to child), or both.

Generally, however, we want to find all sufficient sets Z. We begin by taking all variables in G, and removing any that could not possibly be in Z. This is easy enough; we cannot have a variable in X or a variable Y also in Z. We can not have a variable along a straight-forward path from X to Y in Z either; the use of an incredibly helpful path algorithm provided by Dr. Neufeld is employed here. We take the remaining variables (after removing X, Y, and all variables along X->Y) and take the power set; any possible set in this may be a sufficient Z if it blocks all back-door paths.

The backdoor detection algorithm for backdoor paths from X -> Y, with a de-confounder Z take the cross product of X and Y, and sees if a backdoor path exists along any of these. The actual path-finding is as a follows (starting from x, searching for y):

```pseudo
backdoor(x, y, Z, current path, paths, previous movement)
    
    if x == y
        we complete a backdoor path
        return all paths so far, plus this path

    if x is not in the path

        if previous movement was down

            if x is in Z, or a descendant of x is in Z
                for every parent of x
                    paths = backdoor(parent, y, current path + x, paths, up)


            if x is not in Z
                for every child of x
                    paths = backdoor(child, y, current path + x, paths, down)

        if previous movement was up
            if x is not in Z
                
                for every parent of x
                    paths = backdoor(parent, y, current path + x, paths, up)
                for every child of x
                    paths = backdoor(child, y, current path + x, paths, up)

    return paths 
```

The idea is that we can always move "up" or "down" through non-controlled variables if we are heading in the same direction. This is consistent with Pearl's definitions, where a path can be blocked along i -> j -> k, if j is in Z. We can also move up, then down, if the variable is not in Z, just as i <- j -> k, where j is *not* in Z. We can also move down, then up, if this variable is in Z, or a child of Z is; i -> j <- k, where j is in Z.
