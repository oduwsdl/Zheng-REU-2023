import os
import json
import csv

urls = ['instagram.com/instagram', 'instagram.com/cristiano', 'instagram.com/leomessi', 'instagram.com/selenagomez', 
     'instagram.com/kyliejenner', 'instagram.com/therock', 'instagram.com/arianagrande', 'instagram.com/kimkardashian', 
     'instagram.com/beyonce', 'instagram.com/khloekardashian', 'instagram.com/nike', 'instagram.com/justinbieber',
     'instagram.com/kendalljenner', 'instagram.com/natgeo', 'instagram.com/taylorswift', 'instagram.com/virat.kohli',
     'instagram.com/jlo', 'instagram.com/kourtneykardash', 'instagram.com/nickiminaj', 'instagram.com/mileycyrus',
     'instagram.com/neymarjr', 'instagram.com/katyperry', 'instagram.com/zendaya', 'instagram.com/kevinhart4real', 'instagram.com/iamcardib' ]

def get_memento_analysis(cdx, index):
    x=json.loads(cdx[index+15:])
    print(x)
    timestamp=cdx[index:index+14]
    uri_m = "https://arquivo.pt/wayback/" + timestamp + "/" + x['url']
    memento_year = int(timestamp[:4])
    date="{}/{}/{}".format(timestamp[:4], timestamp[4:6], timestamp[6:8])
    time="{}:{}:{}".format(timestamp[8:10], timestamp[10:12], timestamp[12:])
    mimetype=x['mime']
    if mimetype=="text/html":
        mimetype=''
    status_code = x['status']

    redirects_to=''
    redirect_type=''

    cmd = 'curl -I -L -s ' + uri_m  +'|grep "HTTP\|^location:"'

    #if the memento is a warc/revisit or a redirect, get the location of the revisit
    if status_code=='-' or 300<=int(status_code)<400:
        output = os.popen(cmd)
        x=output.readlines()
        print(x)
        list_of_locations=[]
        list_of_status_codes=[]

        #separate redirect locations from status codes
        for item in x:
            if item.startswith('location:'):
                list_of_locations.append(item)
            else:
                list_of_status_codes.append(item[9:12])

        if len(list_of_status_codes)==1:
            assert len(list_of_locations)==0
            redirect_type=get_redirect_type(list_of_status_codes)
        elif len(list_of_locations)>0:
            redirects_to=list_of_locations[-1][10:]
            if 'login' in redirects_to:
                redirect_type='login'
            else:
                redirect_type=get_redirect_type(list_of_status_codes)

    return [memento_year, uri_m, status_code, date, time, mimetype, redirects_to, redirect_type]
    #return [memento_year, uri_m, date, time]

def get_redirect_type(list_of_status_codes):
    status_code=int(list_of_status_codes[-1])
    if status_code==200:
        redirect_type='2xx'
    elif 400<=status_code<500:
        redirect_type='4xx'
    elif 500<=status_code<600:
        redirect_type='5xx'
    else:
        print(status_code)
        exit()
    return redirect_type

with open('health_officials_arquivo.csv', 'a', encoding='utf-8') as file:
    writer = csv.writer(file)
    #csv headers
    writer.writerow(["year", "urim", "status_code", "date", "time", "mimetype", "redirects_to", "redirect_type"])
    for url in urls:
        print(url)
        username=url[14:]
        index=16+len(username)
        cmd='curl -L -s \"https://arquivo.pt/wayback/cdx?url=https://www.' + url + '"'
        output=os.popen(cmd)
        lines=output.readlines()
        print(len(lines))
        #writer.writerow(["year", "urim", "date", "time"])
        count=0
        for line in lines:
            print(line[index:index+14])
        #["urlkey","timestamp","original","mimetype","statuscode","digest","length"]
            try:
                data=get_memento_analysis(line, index)
                #print(data)
                #update csv
                writer.writerow(data)
            except Exception as e:
                print('failed to write to file: ')
                print(line)
                print(e)
            count+=1
            print(count)
        print('\n')
    