import requests

class Helper(object):

    @classmethod
    def calculate_num_countries(self, access_token, user_id):
        # show the list of matching products in the database 
        print access_token
        print user_id
        req = """https://graph.facebook.com/v2.5/{uid}/tagged_places?access_token={at}""".format(at=access_token, uid=user_id)
        print req
        r = requests.get(req)
        json = r.json()
        distinct_c = []
        while json.get('paging').get('next'):
            for obj in json.get('data'):
                country = obj.get('place').get('location').get('country')
                if country not in distinct_c and country:
                    distinct_c.append(obj.get('place').get('location').get('country'))
            r = requests.get(json.get('paging').get('next'))
            json = r.json()

        print distinct_c
        return len(distinct_c)