def seq(parts, msgs, out, width=1040, top=40, step=25, note_h=0):
    n = len(parts)
    xs = [p[1] for p in parts]
    y0 = top + 56
    H = y0 + len(msgs)*step + 36
    o = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">' % (width, H)]
    o.append('<defs>'
             '<marker id="s1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#1f3c56"/></marker>'
             '<marker id="s2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,2 L10,5 L0,8" fill="none" stroke="#44525f" stroke-width="1.3"/></marker>'
             '<marker id="s3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#b8341c"/></marker>'
             '</defs>')
    for (lab, x, sub) in parts:
        w = 150
        o.append('<rect x="%d" y="%d" width="%d" height="38" rx="4" fill="#1f3c56"/>' % (x-w//2, top, w))
        o.append('<text x="%d" y="%d" font-size="9.6" font-weight="600" fill="#fff" text-anchor="middle">%s</text>' % (x, top+16, lab))
        o.append('<text x="%d" y="%d" font-size="8.1" fill="#b9c8d6" text-anchor="middle">%s</text>' % (x, top+29, sub))
        o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#aebbc6" stroke-width="1" stroke-dasharray="4 4"/>' % (x, top+38, x, H-26))
    for i,(a,b,lab,kind) in enumerate(msgs):
        y = y0 + i*step
        if kind == "note":
            o.append('<rect x="%d" y="%d" width="%d" height="19" rx="3" fill="#fdf0ec" stroke="#b8341c" stroke-width=".9"/>' % (xs[a]-6, y-13, (xs[b]-xs[a])+12 if b!=a else 300))
            o.append('<text x="%d" y="%d" font-size="8.6" fill="#b8341c" font-weight="600">%s</text>' % (xs[a]+4, y, lab))
            continue
        if a == b:
            x = xs[a]
            o.append('<path d="M%d,%d L%d,%d L%d,%d L%d,%d" fill="none" stroke="#1f3c56" stroke-width="1.2" marker-end="url(#s1)"/>' % (x, y-8, x+34, y-8, x+34, y+4, x+2, y+4))
            o.append('<text x="%d" y="%d" font-size="8.6" fill="#16202b">%s</text>' % (x+42, y+2, lab))
            continue
        x1, x2 = xs[a], xs[b]
        if kind == "ret":
            o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#44525f" stroke-width="1.1" stroke-dasharray="5 3" marker-end="url(#s2)"/>' % (x1, y, x2, y))
            col = "#44525f"
        elif kind == "err":
            o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#b8341c" stroke-width="1.3" marker-end="url(#s3)"/>' % (x1, y, x2, y))
            col = "#b8341c"
        else:
            o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#1f3c56" stroke-width="1.2" marker-end="url(#s1)"/>' % (x1, y, x2, y))
            col = "#16202b"
        mid = (x1+x2)//2
        o.append('<text x="%d" y="%d" font-size="8.6" fill="%s" text-anchor="middle">%s</text>' % (mid, y-5, col, lab))
    o.append('</svg>')
    open(out, "w", encoding="utf-8").write("\n".join(o))
