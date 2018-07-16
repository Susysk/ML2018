import json

with open("leagues/campionati") as FileObj:
    for lines in FileObj:
        campionato={}
        campionato['area']=lines[33:].split("/")[0]
        campionato['league']=lines[33:].split("/")[1]
        campionato['urls']=[]
        for i in range(2010,2019):
            campionato['urls'].append(lines.replace('/results/','-'+str(i)+'-'+str(i+1)+'/results/').replace('\n',''))
            campionato['urls'].append(lines.replace('/results/','-'+str(i)+'/results/').replace('\n',''))
        with open('leagues/soccer/'+lines[33:-9].replace('/','-')+'.json', 'w') as outfile:
            json.dump(campionato, outfile,indent=4)
