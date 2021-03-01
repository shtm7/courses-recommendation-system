### Load packages
#import arabic_reshaper
import numpy as np
import scipy.stats as stats
import pandas as pd


df= pd.read_csv('./data/Academy Full Pack clean.csv' , encoding = "UTF-8")


rate=pd.read_csv('./data/rate clean.csv' , encoding = "UTF-8")


intrest=pd.read_csv('./data/intrest clean.csv' , encoding = "UTF-8")
#############################################

data=pd.merge(df,intrest,on='student_id')
intr=data[['student_id', 'course_id', 'course_name']]

#######################################
from sklearn.preprocessing import LabelEncoder
encoder= LabelEncoder()
data['intr_no']=encoder.fit_transform(data['intrest'].fillna(np.nan))

# data.to_csv('./data/data.csv')

# convert the word catagorical lables to numbers 

from sklearn.preprocessing import LabelEncoder
import numpy as np

def encoder(df,col):
    encoder= LabelEncoder()
    df[col]=encoder.fit_transform(df[col].fillna(np.nan))
    return df[col]
encoder(data , 'intrest')
print('')

############ start model ###########


from scipy import sparse
from lightfm import LightFM
from sklearn.metrics.pairwise import cosine_similarity

def create_interaction_matrix(df,student_id, item_col, interest_col, norm= False, threshold = None):
    '''
    Function to create an interaction matrix dataframe from transactional type interactions
    Required Input -
        - df = Pandas DataFrame containing user-item interactions
        - student_id = column name containing user's identifier
        - item_col = column name containing item's identifier
        - interest col = column name containing user feedback on interaction with a given item
        - norm (optional) = True if a normalization of interests is needed
        - threshold (required if norm = True) = value above which the interest is favorable
    Expected output - 
        - Pandas dataframe with user-item interactions ready to be fed in a recommendation algorithm
    '''
    interactions = df.groupby([student_id, item_col])[interest_col]             .sum().unstack().reset_index().             fillna(0).set_index(student_id)
    if norm:
        interactions = interactions.applymap(lambda x: 1 if x > threshold else 0)
    return interactions

########

interactions = create_interaction_matrix(df = data,
                                         student_id = 'student_id',
                                         item_col = 'course_id',
                                         interest_col = 'intrest')


#########



def create_user_dict(interactions):
    '''
    Function to create a user dictionary based on their index and number in interaction dataset
    Required Input - 
        interactions - dataset create by create_interaction_matrix
    Expected Output -
        user_dict - Dictionary type output containing interaction_index as key and user_id as value
    '''
    user_id = list(interactions.index)
    user_dict = {}
    counter = 0 
    for i in user_id:
        user_dict[i] = counter
        counter += 1
    return user_dict

########


def create_item_dict(df,id_col,name_col):
    '''
    Function to create an item dictionary based on their item_id and item name
    Required Input - 
        - df = Pandas dataframe with Item information
        - id_col = Column name containing unique identifier for an item
        - name_col = Column name containing name of the item
    Expected Output -
        item_dict = Dictionary type output containing item_id as key and item_name as value
    '''
    item_dict ={}
    for i in range(df.shape[0]):
        item_dict[(df.loc[i,id_col])] = df.loc[i,name_col]
    return  item_dict

##############

user_dict = create_user_dict(interactions=interactions)
# Create Item dict
items_dict = create_item_dict(df = data,
                               id_col = 'course_id',
                               name_col = 'course_name')

###################

def runMF(interactions, n_components=30, loss='warp', k=15, epoch=30,n_jobs = 4):
    '''
    Function to run matrix-factorization algorithm
    Required Input -
        - interactions = dataset create by create_interaction_matrix
        - n_components = number of embeddings you want to create to define Item and user
        - loss = loss function other options are logistic, brp
        - epoch = number of epochs to run 
        - n_jobs = number of cores used for execution 
    Expected Output  -
        Model - Trained model
    '''
    x = sparse.csr_matrix(interactions.values)
    model = LightFM(no_components= n_components, loss=loss,k=k)
    model.fit(x,epochs=epoch,num_threads = n_jobs)
    return model

##############

mf_model = runMF(interactions = interactions,
                 n_components = 20,
                 loss = 'warp',
                 epoch = 15,
                 n_jobs = 4)

################

def sample_recommendation_user(model, interactions, user_id, user_dict, 
                               item_dict,threshold = 0,nrec_items = 10, show = True):
    '''
    Function to produce user recommendations
    Required Input - 
        - model = Trained matrix factorization model
        - interactions = dataset used for training the model
        - user_id = user ID for which we need to generate recommendation
        - user_dict = Dictionary type input containing interaction_index as key and user_id as value
        - item_dict = Dictionary type input containing item_id as key and item_name as value
        - threshold = value above which the interest is favorable in new interaction matrix
        - nrec_items = Number of output recommendation needed
    Expected Output - 
        - Prints list of items the given user has already bought
        - Prints list of N recommended items  which user hopefully will be interested in
    '''
    if user_id in user_dict.keys():
        n_users, n_items = interactions.shape
        user_x = user_dict[user_id]
        scores = pd.Series(model.predict(user_x,np.arange(n_items)))
        scores.index = interactions.columns
        scores = list(pd.Series(scores.sort_values(ascending=False).index))

        known_items = list(pd.Series(interactions.loc[user_id,:]                                      [interactions.loc[user_id,:] > threshold].index)                                      .sort_values(ascending=False))

        scores = [x for x in scores if x not in known_items]
        return_score_list = scores[0:nrec_items]
        known_items = list(pd.Series(known_items).apply(lambda x: item_dict[x]))
        scores = list(pd.Series(return_score_list).apply(lambda x: item_dict[x]))
        rec=[]
        if show == True:
            # print("Known Likes:")
            # counter = 1
            # for i in known_items:
            #     print(str(counter) + '- ' + i)
            #     counter+=1

            print("\n Recommended Items:")
            counter = 1
            for i in scores:
                rec.append( i +'\n' )
                counter+=1
        result =rec
        return scores

    else:
        print('Student ID not found but we recommend :')
        intract = interactions.sum().sort_values(ascending=False).head().index.tolist()
        lest=[]
        for i  in intract:
            if i in items_dict.keys():
                   lest.append(items_dict[i])
        counter = 1
        notfo=[]
        for i in lest:
                notfo.append(i+ '\n' )
                counter+=1
        result =notfo
        return result

###################

## Calling 10 item recommendation for user id 11

# def __init__(self, name, age):
#         self.name = name
#         self.age = age


