from flask import Flask, request, render_template ,redirect
from courses import sample_recommendation_user, runMF,create_user_dict, create_item_dict, create_interaction_matrix
import pandas as pd
import time

# Create the application.
APP = Flask(__name__)


@APP.route('/' , methods=['POST','GET'])
def index():
    """ Displays the index page accessible at '/'
    """
    if request.method == 'GET':
        return render_template('index.html')  
    if request.method == 'POST':
        print(request.data)
        text = int(request.form['student_id'])
        print(text)
           # print('File Not Uploaded')
           # return  ('File Not Uploaded')
        # Get recommend of prediction
        data = pd.read_csv('./data/data.csv')
        interactions = create_interaction_matrix(df = data,
                                         student_id = 'student_id',
                                         item_col = 'course_id',
                                         interest_col = 'intrest')


        user_dict = create_user_dict(interactions=interactions)
        # Create Item dict
        items_dict = create_item_dict(df = data,
                                    id_col = 'course_id',
                                    name_col = 'course_name')
        mf_model = runMF(interactions = interactions,
                    n_components = 20,
                    loss = 'warp',
                    epoch = 15,
                    n_jobs = 4)
        recommend =  sample_recommendation_user(model = mf_model, 
                                    interactions = interactions, 
                                    user_id = text, 
                                    user_dict = user_dict,
                                    item_dict = items_dict, 
                                    threshold = 4,
                                    nrec_items = 5,
                                    show = True)
            
        # Render the result template
        return render_template('result.html',len=len(recommend) , recommend=recommend)
        time.sleep(30)



if __name__ == '__main__':
    APP.debug=True
    APP.run()
