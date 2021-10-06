import sympy as sp
import numpy as np

D = 12 / 5
point0 = np.array((5,2))
point1 = np.array((1,5))
center_point = (36/25+1, 48/25+2)

tmp = point0-point1
slope = tmp[1]/tmp[0]

x = sp.Symbol('x')
y = sp.Symbol('y')

expr1 = (x-center_point[0])**2+(y-center_point[1])**2-D**2
expr2 = -1/slope*(x-center_point[0])-y+center_point[1]
ans = sp.solve([expr1, expr2])
ans_point0 = (int(ans[0][x]),int(ans[0][y]))
ans_point1 = (int(ans[1][x]),int(ans[1][y]))

print(ans_point0)
print(ans_point1)
