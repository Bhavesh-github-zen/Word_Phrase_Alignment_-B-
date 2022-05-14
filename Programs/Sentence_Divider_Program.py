hverb=["am", "is", "are", "didn't", "was", "were", "being", "been", "be","may", "might", "must", "can", "could", "have", "has", "had", "do", "does", "did", "will", "would", "shall","should"]

def sent_with_hverb(sent):
    l=sent.split()
    #print(len(l))
    #print(l)
    for i in l:
        if i in hverb:
            index=l.index(i)
            break
    subj=l[0:index]
    helpverb=l[index]
    verb=l[index+1]
    rem_sent=l[index+2:]
    print("\nGroup1:", end=" ")
    for i in subj:
        print(i, end=" ")
    print()
    print("Group2: "+ helpverb+" "+verb)
    print("Group3:", end=" ")
    for i in rem_sent:
        print(i, end=" ")
        
def sent_without_hverb(sent):
    l=sent.split()
    subj=l[0]
    verb=l[1]
    rem_sent=l[2:]
    """
    print("Group1:", end=" ")
    for i in subj:
        print(i, end=" ")
    print()
    """
    print("\nGroup1: "+subj)
    print("Group2: "+verb)
    print("Group3:", end=" ")
    for i in rem_sent:
        print(i, end=" ")

sent = str(input("Sentence: "))
l=sent.split()
hv=None
for i in l:
    if i in hverb:
        index=l.index(i)
        hv=l[index]
        break
helpverb=hv
if helpverb in hverb:
    sent_with_hverb(sent)
else:
    sent_without_hverb(sent)