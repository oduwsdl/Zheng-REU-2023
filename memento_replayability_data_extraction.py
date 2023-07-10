import argparse
import os
import csv

#list of uris to get the mementos of (instagram.com/username)
#urls= ['instagram.com/RobertFKennedyJr']
    # urls = ['instagram.com/drmercola', 'instagram.com/RobertFKennedyJr', 'instagram.com/thetruthaboutvaccinesttav',
    #         'instagram.com/drtenpenny', 'instagram.com/_rizzaislam', 'instagram.com/drbuttar',
    #         'instagram.com/healthnutnews', 'instagram.com/greenmedinfo', 'instagram.com/kellybroganmd',
    #         'instagram.com/drchristianenorthrup', 'instagram.com/dr.bentapper']

    # urls = ['instagram.com/bbcnews', 'instagram.com/unicef', 'instagram.com/cdcgov',
    #         'instagram.com/who', 'instagram.com/thisisbillgates', 'instagram.com/ukgovofficial',
    #         'instagram.com/nhs', 'instagram.com/gatesfoundation', 'instagram.com/lshtm']

    #urls = ['instagram.com/instagram', instagram.com/cristiano', 'instagram.com/leomessi', 'instagram.com/selenagomez', 
    # 'instagram.com/kyliejenner', 'instagram.com/therock', 'instagram.com/arianagrande', 'instagram.com/kimkardashian', 
    # 'instagram.com/beyonce', 'instagram.com/khloekardashian', 'instagram.com/nike', 'instagram.com/justinbieber',
    # 'instagram.com/kendalljenner', 'instagram.com/natgeo', 'instagram.com/taylorswift', 'instagram.com/virat.kohli',
    # 'instagram.com/jlo', 'instagram.com/kourtneykardash', 'instagram.com/nickiminaj', 'instagram.com/mileycyrus'
    # 'instagram.com/neymarjr', 'instagram.com/katyperry', 'instagram.com/zendaya', 'instagram.com/kevinhart4real', 'instagram.com/iamcardib' ]

def get_mementos(url):
    cmd = 'curl -L -s \"http://web.archive.org/cdx/search/cdx?url=https://www.' + url + '"'
    output = os.popen(cmd)
    return output.readlines()

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
    redirects_to=''
    redirect_type=''

    cmd = 'curl -I -L -s ' + uri_m  +'|grep "HTTP\|^location:"'

    #if the memento is a warc/revisit or a redirect, get the location of the revisit
    if status_code=='-' or 300<=int(status_code)<400:
        output = os.popen(cmd)
        x=output.readlines()
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
            
    return [memento_year, uri_m, status_code, date, time, mimetype, cdx_object[5], redirects_to, redirect_type]

def get_memento_data_from_one_account(url, start, end):
    mementos=get_mementos(url)
    print(len(mementos))
    if start is None:
        start=0
    if end is None:
        end=len(mementos)
    #filename=username.csv
    filename=url[14:]+'.csv'
    with open(filename, 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        #csv headers
        if start==0:
            writer.writerow(["year", "urim", "status_code", "date", "time", "mimetype", "digest", 'redirects_to', 'redirect_type'])
        count=0
        for line in mementos[start:end]:
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
            if count%50==0:
                print(count)
                print("currently processing: "+ str(cdx_object[1:]))

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

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command')

    cdx_objects = subparser.add_parser('cdx')
    cdx_objects.add_argument('--input', type=str, required=True)
    cdx_objects.add_argument('--output', type=str, required=True)

    mult_accounts = subparser.add_parser('mult')
    mult_accounts.add_argument('--input', type=str, required=True)

    singular_account = subparser.add_parser('one', help='get memento data for ONE url')
    singular_account.add_argument('--url', type=str, required=True)
    singular_account.add_argument('--start', type=int, required=False)
    singular_account.add_argument('--end', type=int, required=False)

    #not finished
    args=parser.parse_args()
    if args.command=='cdx':
        pass
        # with open(args.input, 'r') as input_file:
        #     with open(args.output, 'a', encoding='utf-8') as output_file:
        #         writer = csv.writer(output_file)
        #         for line in output_file:
        #             cdx_object = line.split(" ") #["urlkey","timestamp","original","mimetype","statuscode","digest","length"]
        #             try:
        #                 data=get_memento_analysis(cdx_object)
        #                 #update csv
        #                 writer.writerow(data)
        #                 update_summary()
        #             except:
        #                 print(line)

    elif args.command=='one':
        get_memento_data_from_one_account(args.url, args.start, args.end)

    #not finished
    elif args.command=='mult':
        with open(args.input, 'r') as file:
            input = file.read().splitlines()
            print(input)
            #if args.combine is not None:
                #main_url(input, combine=True, output=args.combine)
            for url in input:
                get_memento_data_from_one_account(url)
