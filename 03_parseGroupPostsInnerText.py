from utils import *

#ts = input('Enter TS') # input timefile timestamp

with open('outputs/02/innertext/0303_2237_posinset_inner.pkl', 'rb') as f:
    loaded_dict_text = pickle.load(f)

post_text = pd.DataFrame(columns=['post', 'reacts', 'comments'])

group_name = 'Fairy Floss Real Estate' 

for idx, post in loaded_dict_text.items():
    if idx:# in (73, 89, 380, 406, 585, 601, 846, 904, 1045, 1113, 1257, 1263, 1293, 1339, 1402, 1443, 1448, 1538, 1618, 1639, 1664, 1706):
        
        repl = {
            "Shared with Members of " + group_name: "", 
            "Top contributor": "", 
            "Shared with Public group": "", 
            "New contributor": "",
            "·": "",
            group_name: "",
            "Write a comment": "",
            "View more comments": "",
            "Message": "",
            "Like": "",
            "Comment": "",
            "Reply": ""
            }
        
        post = replace_all(post, repl)

        reacts = re.findall(r"All reactions (\d+)", post)
        if not reacts:
            reacts = '0'
        else:
            reacts = reacts[0]

        comments = re.findall(r"\b(\d+)\s*comments?\b", post)
        if not comments:
            comments = '0'
        else:
            comments = comments[0]

        repl = {"All Reactions": "",
                "comments": ""}

        list_row = [post, reacts, comments]

        post_text.loc[len(post_text)] = list_row

print(post_text)
post_text.to_csv('outputs/03/parsed_text.csv')
