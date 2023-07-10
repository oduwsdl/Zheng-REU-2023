import os
import csv
def get_memento_analysis(cdx_object):
    uri_m = "https://web.archive.org/web/" + cdx_object[1] + "/" + cdx_object[2]
    timestamp=cdx_object[1]
    memento_year = int(timestamp[:4])
    date="{}/{}/{}".format(timestamp[:4], timestamp[4:6], timestamp[6:8])
    time="{}:{}:{}".format(timestamp[8:10], timestamp[10:12], timestamp[12:])
    mimetype=cdx_object[3]
    if mimetype=="text/html":
        mimetype=''
    status_code = cdx_object[4]
            
    return [memento_year, uri_m, status_code, date, time, mimetype, cdx_object[5]]

if __name__ == "__main__":
    #get mementos of instagram.com/accounts/login from 2019
    cmd='curl -L -s \"http://web.archive.org/cdx/search/cdx?url=https://www.instagram.com/accounts/login&from=201901&to=201912"'
    output = os.popen(cmd)
    login_mementos=output.readlines()
    print(len(login_mementos))
    with open('login.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        #csv headers
        writer.writerow(["year", "urim", "status_code", "date", "time", "mimetype", "digest"])
        count=0
        for line in login_mementos:
            cdx_object = line.split(" ") #["urlkey","timestamp","original","mimetype","statuscode","digest","length"]
            try:
                data=get_memento_analysis(cdx_object)
                #print(data)
                #update csv
                writer.writerow(data)
            except Exception as e:
                print('failed to write to file: ')
                print(line)
                raise e
            count+=1
            if count%1000==0:
                print(count)
                print("currently processing: "+ str(cdx_object[1:]))