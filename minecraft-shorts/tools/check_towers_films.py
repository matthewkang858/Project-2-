import sys, time
t = time.time()
import render
name = sys.argv[1]
S = render.Session(name)
print("BUILD %s ok: %d shots, frames %d-%d, %.1f s" % (name, len(S.film.shots), S.film.frame_start, S.film.frame_end, time.time() - t))
