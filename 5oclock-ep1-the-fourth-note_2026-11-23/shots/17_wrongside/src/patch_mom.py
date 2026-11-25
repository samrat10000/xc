import os, ast
D = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(D, 'paint_day17.py'); t = open(p, encoding='utf-8').read()
n = t.count("c.set_source_rgb(.30, .22, .26)")
t = t.replace("c.set_source_rgb(.30, .22, .26)", "c.set_source_rgb(.16, .11, .15)")                  # dark against the lit door
t = t.replace("c.set_source_rgb(.86, .82, .72)                                              # apron", "c.set_source_rgb(.74, .70, .62)                                              # apron")
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('recoloured', n)
