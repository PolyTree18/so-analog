def shorten(s, i):
    l = s.split(" ")
    cl = 0
    li = 0
    out = ""
    while cl < i:
        try:
            out = f"{out} {l[li]}"
            cl += len(l[li])
            li += 1
        except IndexError:
            break
    return(out.replace(" ", "", 1))

def shorten_2(s, i):
    out = []
    out.append(shorten(s, i))
    s = s.replace(out[0], "", 1)
    out.append(shorten(s, i))
    return(out)
