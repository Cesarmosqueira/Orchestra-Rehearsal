#!/usr/bin/env python
# coding: utf-8

# In[1]:




# In[1]:


from ortools.sat.python import cp_model
import time
import numpy


# In[2]:


tabpxc = [[1, 0, 1, 1, 0, 1, 1, 0, 1], #Tabla del problema Musico x Numero de composicion
          [1, 0, 1, 1, 1, 1, 0, 1, 0],
          [1, 1, 0, 0, 1, 0, 0, 1, 0],
          [1, 0, 0, 0, 1, 0, 1, 0, 1], 
          [0, 1, 0, 1, 1, 1, 1, 0, 0]]

tabC2 = [[1,1,1,1,0], 
          [0,0,1,0,1],
          [1,1,0,0,0],
          [1,1,0,0,1], 
          [0,1,1,1,1],
          [1,1,0,0,1],
          [1,0,0,1,1],
          [0,1,1,0,0],
          [1,0,0,1,0]]

tabC = [[0,0,0,0,1], 
          [1,1,0,1,0],
          [0,0,1,1,1],
          [0,0,1,1,0], 
          [1,0,0,0,0],
          [0,0,1,1,0],
          [0,1,1,0,0],
          [1,0,0,1,1],
          [0,1,1,0,1]]

arrcxd = [2, 4, 1, 3, 3, 2, 5, 7, 6] #Duración de composiciones
comps = [[0,1,2,3],[2,4],[0,1],[0,1,4],[1,2,3,4],[0,1,4],[0,3,4],[1,2],[0,3]]
cN = [6,6,4,4,5]


# In[3]:


model = cp_model.CpModel()

waiti = model.NewIntVar(0, sum(arrcxd)*5, 'z') #Tiempo total de espera

tabcxo = [] #Tabla Numero de composicion x Orden de composición (1 si la composicion se da en ese orden y 0 si no)
for i in range(len(tabpxc[0])): 
    fila = [] 
    for j in range(len(tabpxc[0])):
      fila += [model.NewBoolVar('x'+str(i)+str(j))]
    tabcxo += [fila]

arrcxo = [] #Arreglo donde los indices son el Numero de la composición y el valor es el orden 
for i in range(len(tabcxo)):
    arrcxo += [model.NewIntVar(1, 9, 'x'+str(i))]
    for j in range(len(tabcxo)):
      model.Add(arrcxo[i] == j + 1).OnlyEnforceIf(tabcxo[i][j])
      model.Add(arrcxo[i] != j + 1).OnlyEnforceIf(tabcxo[i][j].Not())

tmp = [] # arreglo para reorganizar composiciones según el orden optimo
invtmp = []
for i in range(9):
    tmp += [[model.NewIntVar(0,1,'pcomp_'+str(i)+'_'+str(j)) for j in range(5)]]
    invtmp += [[model.NewIntVar(0,1,'invwaitTime_'+str(i)+'_'+str(j)) for j in range(5)]]

for i in range(9):
    for j in range(9):
        for z in range(5):
            model.Add(tmp[i][z] == tabpxc[z][j]).OnlyEnforceIf(tabcxo[j][i])
            model.Add(invtmp[i][z] == -1*tabpxc[z][j]+1).OnlyEnforceIf(tabcxo[j][i])

tmp2 = [] # arreglo para multiplicar los vacios por su duracion
tmp3 = []
for i in range(5):
    tmp2 += [[model.NewIntVar(0,100,'waitTime_'+str(i)+'_'+str(j)) for j in range(9)]]
    tmp3 += [[model.NewIntVar(0,100,'waitTime_'+str(i)+'_'+str(j)) for j in range(9)]]

for i in range(9):
    for j in range(9):
        for z in range(5):
            model.AddMultiplicationEquality(tmp2[z][j], [invtmp[j][z], arrcxd[j]])
            model.Add(tmp3[z][j] == tmp2[z][j]).OnlyEnforceIf(tabcxo[i][j])

arrival = []

val1 = model.NewIntVar(1,1,"val1")
for i in range(5):
    arrival +=[[model.NewIntVar(0,16,'arr'+str(i)+''+str(j)) for j in range(9)]]
for i in range(5):
  b=15
  for j in range(9):
    model.Add(arrival[i][j] == b).OnlyEnforceIf(tmp[j][i])
    b-=1


wait = []
for i in range(5):
    wait += [sum(tmp2[i])]
model.Add(sum(wait) == waiti)
model.Minimize(waiti)

model.AddAllDifferent(arrcxo)
model.Add(arrcxo[1] < arrcxo[7]) #La composición 2 debe estar antes que la composición 8
model.Add(arrcxo[4]+1 == arrcxo[5]) #La composición 6 debe darse justo despues de la 5


# In[4]:


solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
  #header
    print('\t',end='')
    for i in range(9):
        print(str(i+1),end='\t')
    print()
    print('Orden:', end='\t')
    for i in range(9):
        print(solver.Value(arrcxo[i]),end='\t')
    print()
    print('Dura:', end='\t')
    for i in range(9):
        print(arrcxd[i],end='\t')
    print()
    print()
    ######################################## 
    print("Relacion de que composicion toca cada hora del evento")
    i_t = [[],[],[],[],[]]
    prog = [[],[],[],[],[]]
    for i in range(9):
        print('Comp'+str(i+1),end='->\t')
        for j in range(9):
            print(solver.Value(tabcxo[i][j]),end='\t')
        print()
    print()
    ######################################## 
    print("Composicion x player: donde las composiciones donde participa son 1")
    for i in range(5):
        print('P'+str(i+1),end='->\t')
        for j in range(9):
            print(solver.Value(tmp[j][i]),end='\t')
            i_t[i].append(solver.Value(tmp[j][i]))
        print()
    print()
    print("Composicion x player: donde los valores > 0 son los espacios donde no toca el player (sin filtrar la llegada y salida)")
    for i in range(5):
        print('P'+str(i+1),end='->\t')
        for j in range(9):
            print(solver.Value(tmp2[i][j]),end='\t')
            prog[i].append(solver.Value(tmp2[i][j]))
        print()
    print()

    print('Tiempo Total: ', solver.Value(waiti))
else: print("NO")


# # Lo que se pretendia hacer (falta completar): Excluir las horas libres previas y posteriores a la llegada y salida del artista, del calculo de tiempo de espera total.

# In[5]:


llegadas = []
salidas = []
for i in range(5):
    for j in range(9):
        if i_t[i][j] == 1: 
            llegadas.append(j)
            break
for i in range(5):
    i_t[i].reverse()
    for j in range(9):
        if i_t[i][j] == 1: 
            salidas.append(9-j)
            break

tiempoTot = 0

for i in range(5):
    tiempoTot += sum(prog[i][llegadas[i]:salidas[i]-1])
print("Tiempo total de espera: ",tiempoTot)


# In[ ]:




