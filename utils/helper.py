def return_user_id(url):
    return url.split("/")[-2]

def return_embedding_id(url):
    return url.split("/")[-2] + "/" + url.split("/")[-1]

def return_date(url):
    return url.split('/')[-1].split('_')[0]

def return_time(url):
    return url.split('/')[-1].split('_')[1]

def return_filename(url):
    return url.split('_')[-1]