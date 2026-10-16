import re
class Q(str):
    """quoted atom"""
    pass
def tokenize(s):
    i=0;n=len(s)
    while i<n:
        c=s[i]
        if c in ' \t\r\n': i+=1
        elif c=='(' : yield '('; i+=1
        elif c==')' : yield ')'; i+=1
        elif c=='"':
            j=i+1; buf=[]
            while s[j]!='"':
                if s[j]=='\\': buf.append(s[j:j+2]); j+=2
                else: buf.append(s[j]); j+=1
            yield Q(''.join(buf)); i=j+1
        else:
            j=i
            while j<n and s[j] not in ' \t\r\n()': j+=1
            yield s[i:j]; i=j
def parse(s):
    stack=[[]]
    for t in tokenize(s):
        if t=='(' : stack.append([])
        elif t==')':
            x=stack.pop(); stack[-1].append(x)
        else: stack[-1].append(t)
    return stack[0]
def dump(x,indent=0,compact=False):
    if isinstance(x,Q): return '"'+x+'"'
    if isinstance(x,str): return x
    if compact or not x: 
        return '('+' '.join(dump(c,0,True) for c in x)+')'
    # head atoms on first line, sublists on own lines
    head=[];i=0
    while i<len(x) and not isinstance(x[i],list):
        head.append(dump(x[i])); i+=1
    out='('+' '.join(head)
    rest=x[i:]
    if not rest: return out+')'
    pad='\t'*(indent+1)
    for c in rest:
        if isinstance(c,list): out+='\n'+pad+dump(c,indent+1)
        else: out+=' '+dump(c)
    out+='\n'+'\t'*indent+')'
    return out
def find(x,name):
    return [c for c in x if isinstance(c,list) and c and c[0]==name]
def find1(x,name):
    r=find(x,name); return r[0] if r else None
