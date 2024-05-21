from utils import *

#ts = input('Enter TS') # input timefile timestamp
#f = open(f"outputs/02/{ts}_output_outerHTML.txt", "r")

with open('outputs/02/outerhtml/0303_2237_posinset_outer.pkl', 'rb') as f:
    dict_html = pickle.load(f)

with open('outputs/02/innertext/0303_2237_posinset_inner.pkl', 'rb') as f:
    dict_text = pickle.load(f)

post_html = pd.DataFrame(columns=['name', 'date', 'header', 'body', 'reacts', 'comments', 'top_react'])

group_name = 'Fairy Floss Real Estate' 

for idx, post in dict_html.items():
    if idx < 150:
        soup = BeautifulSoup(post, "lxml")
        div_element = soup.find('div')
        fts = div_element.get('aria-describedby', '').split()
        name = div_element.get('aria-labelledby', '')

        date = fts[0]
        body = fts[1]
        head = fts[2]
        like = fts[3]
        cmnt = fts[4]
        
        try:
            post_name = soup.find('h3', {"id": name}).text
            post_date = soup.find('span', {"id": date}).text
        except AttributeError:
            print(f'{idx}: name/date error')
            post_name, post_date = 'p name', 'p date'
        
        post_date = replace_all(post_date, date_repl)
        
        try:
            post_head = soup.find('div', {"id": head}).text[0:-7]
        except AttributeError:
            print(idx)
            post_head = ''
            # process innertext to fill body as body/header are incorrectly parsed
            inner_post = dict_text.get(idx)
            inner_post = replace_all(inner_post, inner_repl)
            pass

        # parse post body
        # handle for innertext to be used wherein a parsing error occurs
        if post_head == '':
            post_body = inner_post
        elif soup.find('div', {"id": body}) == None:
            innerText = soup.text
            set_var = [post_name, post_date, post_head]
            for i in set_var:
                innerText = innerText.replace(i, '')
            post_body = re.split('All reactions:| · |LikeComment', innerText)[0]
        else:
            post_body = soup.find('div', {"id": body}).text

        # parse post likes
        try:   
            post_top_reac = soup.find('span', {"id": like}).find('div').get('aria-label', '')
            post_reac = soup.find('span', {"aria-label": "See who reacted to this"}).parent.text.split()[2]
        except AttributeError:
            # post has no react/top react elements due to no reactions on posts. Populate values with 0
            post_reac = 0
            post_top_reac = 0
            pass

        try:
            post_cmnt = soup.find('div', {"id": cmnt}).text
            post_cmnt = re.findall(r"(\d+)\s*comments?\b", post_cmnt)
            post_cmnt = post_cmnt[0]
        except AttributeError:
            post_cmnt = '0'


        list_row = [post_name, post_date, post_head, post_body, post_reac, post_cmnt, post_top_reac]
        post_html.loc[len(post_html)] = list_row

# print(post_html)
post_html.to_csv('outputs/03/parsed_html.csv')